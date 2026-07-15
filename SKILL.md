
# Huawei Cloud Deployment Skill

## Overview

Helps deploy monolithic or distributed applications to Huawei Cloud, covering the complete infrastructure chain:

- **Security Groups**: Create, add rules, common port reference
- **ECS**: Create cloud servers, batch start/stop, query status
- **EIP**: Apply for Elastic Public IP, bind to ECS or ELB, join shared bandwidth package
- **Shared Bandwidth**: Create shared traffic packages, add/remove EIPs
- **OBS**: Create buckets, upload private images or artifacts (AK/SK signing)
- **ECS to RDS**: Security group setup + connection string configuration
- **ELB**: Create load balancers, listeners, backend server groups, add ECS nodes, health checks
- **RDS**: Create instances, backup and restore, account management, slow logs, parameter configuration

See `references/rds-api.md` for detailed API reference.

## When to Use

- User says "deploy my app to Huawei Cloud", "create an ECS", "configure a security group"
- User says "apply for a public IP", "set up load balancing for ECS", "multi-node deployment"
- User says "upload image to OBS", "how does ECS connect to RDS"
- Not applicable for: GaussDB, DCS, DDS and other database products; K8s/CCE container deployments

## Prerequisite Variables

| Variable | Description | Endpoint Derivation |
|------|------|---------------|
| `TOKEN` | IAM Token (valid 24h) | `POST iam.{REGION}.myhuaweicloud.com/v3/auth/tokens` |
| `REGION` | Region ID, e.g. `cn-north-4` | - |
| `PROJECT_ID` | Project ID | `GET iam.{REGION}.myhuaweicloud.com/v3/auth/projects` |

Service endpoints: `{service}.{REGION}.myhuaweicloud.com`, service = ecs / vpc / elb / rds / obs

## Typical Architecture

```
Monolithic:   Internet → EIP → ECS → RDS

Distributed:  Internet → EIP → ELB → ECS-1 ┐
                               ECS-2 ├→ RDS (primary/standby)
                               ECS-N ┘
```

**Complete deployment steps (distributed, in order):**
1. Create security group + add port rules
2. Create N ECS instances, associate security group
3. Apply for EIP (or join shared bandwidth package)
4. Upload private image to OBS (optional)
5. Create RDS instance, open ECS to RDS port in security group
6. Create ELB - Listener - Backend server group - Add ECS - Health check
7. Bind EIP to ELB

---

## 1. Security Groups

```bash
# Create security group
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-groups \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"security_group": {"name": "sg-web-app", "description": "Web application security group"}}'

# Add inbound rule (open HTTP port 80)
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "security_group_rule": {
      "security_group_id": "{SG_ID}", "direction": "ingress",
      "protocol": "tcp", "port_range_min": 80, "port_range_max": 80,
      "remote_ip_prefix": "0.0.0.0/0"
    }
  }'
```

**Common port reference:** HTTP:80, HTTPS:443, SSH:22, RDP:3389, MySQL:3306, PG:5432, Custom:8080/8443

ECS to RDS: `direction=ingress`, `remote_group_id={ECS_SG_ID}` (security group mutual access is more secure than CIDR)

---

## 2. ECS Cloud Servers

```bash
# Create ECS instance
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "server": {
      "name": "app-server-01", "imageRef": "{IMAGE_ID}", "flavorRef": "c3.xlarge.2",
      "availability_zone": "{AZ}", "vpcid": "{VPC_ID}",
      "nics": [{"subnet_id": "{SUBNET_ID}"}],
      "security_groups": [{"id": "{SG_ID}"}],
      "root_volume": {"volumetype": "SSD", "size": 50},
      "adminPass": "{PASSWORD}"
    }
  }'
# Returns job_id — poll GET /v1/{PROJECT_ID}/jobs/{JOB_ID} until status=SUCCESS

# Batch start / stop / reboot
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"os-start": {"servers": [{"id": "{SERVER_ID}"}]}}'
# os-stop: {"type":"SOFT","servers":[...]}, reboot: {"type":"SOFT","servers":[...]}

# Query list
curl -s "https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/detail?limit=20&offset=1" \
  -H "X-Auth-Token: {TOKEN}"
```

Status: `ACTIVE` Running / `SHUTOFF` Stopped / `BUILD` Creating / `ERROR` Abnormal

Flavor naming: `s6.large.2`=2C4G General, `c3.xlarge.2`=4C8G Compute, `m3.xlarge.8`=4C32G Memory

---

## 3. Elastic Public IP (EIP)

```bash
# Apply for dedicated EIP (billed by bandwidth, 5 Mbps)
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "publicip": {"type": "5_bgp"},
    "bandwidth": {"name": "bw-app", "size": 5, "share_type": "PER", "charge_mode": "bandwidth"}
  }'
# Returns publicip.id and public_ip_address

# Bind EIP to ECS NIC port
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID}/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"publicip": {"port_id": "{PORT_ID}"}}'
# PORT_ID = ECS NIC port — from the addresses field in ECS details

# Unbind EIP
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID}/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"publicip": {"port_id": null}}'
```

---

## 4. Shared Bandwidth Package

```bash
# Create shared bandwidth
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"name": "shared-bw-prod", "size": 50}}'
# Returns bandwidth.id

# Add EIP to shared bandwidth
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths/{BW_ID}/insert \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"publicip_info": [{"publicip_id": "{EIP_ID}", "publicip_type": "5_bgp"}]}}'

# Remove EIP from shared bandwidth (must specify new dedicated bandwidth size after removal)
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths/{BW_ID}/remove \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"publicip_info": [{"publicip_id": "{EIP_ID}", "publicip_type": "5_bgp"}], "size": 5, "charge_mode": "bandwidth"}}'
```

---

## 5. OBS — Upload Images and Artifacts

OBS uses AK/SK signing, not IAM Token. Create an access key (AK/SK) in the console first.

```bash
# Create Bucket (first time only)
curl -s -X PUT https://{BUCKET_NAME}.obs.{REGION}.myhuaweicloud.com \
  -H "Authorization: OBS {AK}:{SIGNATURE}" \
  -H "Date: {GMT_DATE}" \
  -H "x-obs-acl: private"

# Upload file (PUT Object)
curl -s -X PUT \
  https://{BUCKET_NAME}.obs.{REGION}.myhuaweicloud.com/{OBJECT_KEY} \
  -H "Authorization: OBS {AK}:{SIGNATURE}" \
  -H "Date: {GMT_DATE}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/your/image.tar.gz
```

**Recommended**: Use the official Huawei Cloud `obsutil` CLI to avoid manually computing signatures:
```bash
# Install obsutil
wget https://obs-community.obs.cn-north-1.myhuaweicloud.com/obsutil/current/linux_amd64/obsutil_linux_amd64.tar.gz
tar -xzf obsutil_linux_amd64.tar.gz && chmod +x obsutil

# Configure AK/SK
./obsutil config -i={AK} -k={SK} -e=obs.{REGION}.myhuaweicloud.com

# Upload
./obsutil cp /local/image.tar.gz obs://{BUCKET_NAME}/images/image.tar.gz
```

---

## 6. ECS to RDS Connectivity

1. **Security group setup**: Add an inbound rule to the RDS security group with `remote_group_id` set to the ECS security group ID, port = database port (MySQL:3306, PG:5432).
2. **Get RDS private IP**: From the `private_ips` field in the RDS instance details; reachable within the same VPC only.
3. **Connection strings**:
   - MySQL: `mysql -h {RDS_PRIVATE_IP} -P 3306 -u {DB_USER} -p {DB_NAME}`
   - PG: `psql -h {RDS_PRIVATE_IP} -p 5432 -U {DB_USER} -d {DB_NAME}`
   - App config: `jdbc:mysql://{RDS_PRIVATE_IP}:3306/{DB_NAME}?useSSL=true`

**Note**: ECS and RDS must be in the same VPC; cross-VPC access requires a VPC peering connection.

---

## 7. ELB Load Balancing (Multi-node)

Full steps: Create LB - Listener - Backend Server Group - Add ECS members - Health Check - Bind EIP

```bash
# Step 1: Create load balancer
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/loadbalancers \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "loadbalancer": {
      "name": "lb-prod", "vpc_id": "{VPC_ID}",
      "vip_subnet_cidr_id": "{SUBNET_ID}",
      "availability_zone_list": ["{AZ}"],
      "guaranteed": false
    }
  }'
# guaranteed=false = shared type (free tier); true = dedicated type (requires l4_flavor_id or l7_flavor_id)
# Returns loadbalancer.id

# Step 2: Create listener
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/listeners \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "listener": {
      "name": "listener-http-80", "loadbalancer_id": "{LB_ID}",
      "protocol": "HTTP", "protocol_port": 80
    }
  }'
# protocol options: TCP / UDP / HTTP / HTTPS / TERMINATED_HTTPS
# Returns listener.id

# Step 3: Create backend server group
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/pools \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "pool": {
      "name": "pool-app", "protocol": "HTTP",
      "lb_algorithm": "ROUND_ROBIN", "listener_id": "{LISTENER_ID}"
    }
  }'
# lb_algorithm: ROUND_ROBIN / LEAST_CONNECTIONS / SOURCE_IP
# Returns pool.id

# Step 4: Add ECS nodes as backend servers
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/pools/{POOL_ID}/members \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "member": {
      "name": "member-ecs-01", "address": "{ECS_PRIVATE_IP}",
      "protocol_port": 8080, "subnet_cidr_id": "{SUBNET_ID}",
      "weight": 1
    }
  }'
# address = ECS private IP; protocol_port = actual app listening port (not LB listener port)

# Step 5: Configure health check
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/healthmonitors \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "healthmonitor": {
      "pool_id": "{POOL_ID}", "type": "HTTP",
      "monitor_port": 8080, "url_path": "/health",
      "delay": 5, "timeout": 3, "max_retries": 3
    }
  }'
# type: TCP / HTTP / HTTPS; url_path only valid for HTTP/HTTPS

# Step 6: Bind EIP to ELB (via the port associated with LB vip_address)
# First query LB vip_port_id, then bind EIP
curl -s "https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/loadbalancers/{LB_ID}" \
  -H "X-Auth-Token: {TOKEN}"
# Get loadbalancer.vip_port_id, then use EIP bind API with this port_id
```

---

## 8. RDS Database

```bash
# Create MySQL 8.0 primary/standby instance
curl -s -X POST https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "name": "rds-prod", "datastore": {"type": "MySQL", "version": "8.0"},
    "ha": {"mode": "Ha", "replication_mode": "semisync"},
    "password": "{ADMIN_PASSWORD}", "flavor_ref": "rds.mysql.c2.large.ha",
    "volume": {"type": "ULTRAHIGH", "size": 100},
    "region": "{REGION}", "availability_zone": "{AZ1},{AZ2}",
    "vpc_id": "{VPC_ID}", "subnet_id": "{SUBNET_ID}",
    "security_group": {"id": "{RDS_SG_ID}"}
  }'

# Other common operations (all under /v3/{PROJECT_ID}/...):
# List instances:          GET /instances
# Create manual backup:    POST /backups
# PITR restore:            POST /instances (source.type=timestamp)
# Create account:          POST /instances/{id}/db_user
# Query slow logs:         GET /instances/{id}/slowlog
# Modify parameters:       PUT /instances/{id}/configurations
```

See `references/rds-api.md` for details.

---

## 9. End-to-End Scenario: 3-Node Web App + MySQL from Scratch

**Target architecture**:
```
Internet → EIP → ELB(HTTP:80) → app-01(8080)
                              → app-02(8080)  → RDS MySQL 8.0 (primary/standby)
                              → app-03(8080)
```

All operations depend on TOKEN, REGION, PROJECT_ID. Assumes VPC and subnet already exist.

### Phase 1: Security Groups

```bash
# 1a. Create Web tier security group (for ECS)
SG_WEB=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-groups \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"security_group":{"name":"sg-web","description":"Web ECS"}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['security_group']['id'])")

# 1b. Create DB tier security group (for RDS)
SG_DB=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-groups \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"security_group":{"name":"sg-db","description":"RDS MySQL"}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['security_group']['id'])")

# 1c. sg-web: open SSH(22), app port(8080), ELB health check (100.125.0.0/16)
for PORT in 22 8080; do
  curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-group-rules \
    -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
    -d "{\"security_group_rule\":{\"security_group_id\":\"${SG_WEB}\",\"direction\":\"ingress\",
         \"protocol\":\"tcp\",\"port_range_min\":${PORT},\"port_range_max\":${PORT},
         \"remote_ip_prefix\":\"0.0.0.0/0\"}}"
done

# 1d. sg-db: allow only sg-web to reach MySQL 3306 (security group mutual access)
curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"security_group_rule\":{\"security_group_id\":\"${SG_DB}\",\"direction\":\"ingress\",
       \"protocol\":\"tcp\",\"port_range_min\":3306,\"port_range_max\":3306,
       \"remote_group_id\":\"${SG_WEB}\"}}"
```

### Phase 2: Create 3 ECS Instances

```bash
# Loop to create app-01 / app-02 / app-03
for i in 01 02 03; do
  JOB=$(curl -s -X POST https://ecs.${REGION}.myhuaweicloud.com/v1/${PROJECT_ID}/cloudservers \
    -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
    -d "{
      \"server\": {
        \"name\": \"app-${i}\", \"imageRef\": \"${IMAGE_ID}\",
        \"flavorRef\": \"s6.large.2\",
        \"availability_zone\": \"${AZ}\", \"vpcid\": \"${VPC_ID}\",
        \"nics\": [{\"subnet_id\": \"${SUBNET_ID}\"}],
        \"security_groups\": [{\"id\": \"${SG_WEB}\"}],
        \"root_volume\": {\"volumetype\": \"SSD\", \"size\": 50},
        \"adminPass\": \"${PASSWORD}\"
      }
    }" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
  echo "app-${i} job_id=${JOB}"
  # Poll until SUCCESS
  while true; do
    STATUS=$(curl -s "https://ecs.${REGION}.myhuaweicloud.com/v1/${PROJECT_ID}/jobs/${JOB}" \
      -H "X-Auth-Token: ${TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
    [ "$STATUS" = "SUCCESS" ] && break
    echo "  waiting... $STATUS"; sleep 10
  done
done
```

### Phase 3: Apply for EIP + Shared Bandwidth

```bash
# 3a. Create shared bandwidth (50 Mbps, shared across EIPs)
BW_ID=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/${PROJECT_ID}/bandwidths \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"bandwidth":{"name":"shared-bw-prod","size":50}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['bandwidth']['id'])")

# 3b. Apply for EIP (to be bound to ELB; using dedicated for now)
EIP_ID=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v1/${PROJECT_ID}/publicips \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"publicip":{"type":"5_bgp"},"bandwidth":{"name":"bw-elb","size":50,"share_type":"PER","charge_mode":"bandwidth"}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['publicip']['id'])")
```

### Phase 4: Create RDS MySQL Primary/Standby Instance

```bash
RDS_JOB=$(curl -s -X POST https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{
    \"name\": \"rds-prod\",
    \"datastore\": {\"type\": \"MySQL\", \"version\": \"8.0\"},
    \"ha\": {\"mode\": \"Ha\", \"replication_mode\": \"semisync\"},
    \"password\": \"${DB_ADMIN_PASS}\",
    \"flavor_ref\": \"rds.mysql.c2.large.ha\",
    \"volume\": {\"type\": \"ULTRAHIGH\", \"size\": 100},
    \"region\": \"${REGION}\",
    \"availability_zone\": \"${AZ1},${AZ2}\",
    \"vpc_id\": \"${VPC_ID}\",
    \"subnet_id\": \"${SUBNET_ID}\",
    \"security_group\": {\"id\": \"${SG_DB}\"}
  }" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['instance']['id'])")
echo "RDS instance_id=${RDS_JOB}"

# Wait for RDS to become available (poll ~5-10 min)
while true; do
  S=$(curl -s "https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances/${RDS_JOB}" \
    -H "X-Auth-Token: ${TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['instance']['status'])")
  [ "$S" = "available" ] && break
  echo "  RDS status=$S, waiting..."; sleep 30
done

# Create application database account
curl -s -X POST https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances/${RDS_JOB}/db_user \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"name\":\"appuser\",\"password\":\"${DB_USER_PASS}\",
       \"databases\":[{\"name\":\"appdb\",\"readonly\":false}]}"
```

### Phase 5: ELB Configuration (Full Flow)

```bash
# 5a. Create load balancer
LB_ID=$(curl -s -X POST https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/loadbalancers \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"loadbalancer\":{\"name\":\"lb-prod\",\"vpc_id\":\"${VPC_ID}\",
       \"vip_subnet_cidr_id\":\"${SUBNET_ID}\",
       \"availability_zone_list\":[\"${AZ1}\"],\"guaranteed\":false}}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['loadbalancer']['id'])")

# 5b. Create HTTP listener (port 80)
LISTENER_ID=$(curl -s -X POST https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/listeners \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"listener\":{\"name\":\"listener-http-80\",\"loadbalancer_id\":\"${LB_ID}\",
       \"protocol\":\"HTTP\",\"protocol_port\":80}}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['listener']['id'])")

# 5c. Create backend server group (round-robin)
POOL_ID=$(curl -s -X POST https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/pools \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"pool\":{\"name\":\"pool-app\",\"protocol\":\"HTTP\",
       \"lb_algorithm\":\"ROUND_ROBIN\",\"listener_id\":\"${LISTENER_ID}\"}}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['pool']['id'])")

# 5d. Add 3 ECS instances to backend (replace ECS_IP_01/02/03 with actual private IPs)
for ECS_IP in ${ECS_IP_01} ${ECS_IP_02} ${ECS_IP_03}; do
  curl -s -X POST https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/pools/${POOL_ID}/members \
    -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
    -d "{\"member\":{\"address\":\"${ECS_IP}\",\"protocol_port\":8080,
         \"subnet_cidr_id\":\"${SUBNET_ID}\",\"weight\":1}}"
done

# 5e. Configure health check (HTTP GET /health)
curl -s -X POST https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/healthmonitors \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"healthmonitor\":{\"pool_id\":\"${POOL_ID}\",\"type\":\"HTTP\",
       \"monitor_port\":8080,\"url_path\":\"/health\",
       \"delay\":5,\"timeout\":3,\"max_retries\":3}}"

# 5f. Get ELB VIP port_id, then bind EIP
VIP_PORT=$(curl -s "https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/loadbalancers/${LB_ID}" \
  -H "X-Auth-Token: ${TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['loadbalancer']['vip_port_id'])")

curl -s -X PUT https://vpc.${REGION}.myhuaweicloud.com/v1/${PROJECT_ID}/publicips/${EIP_ID} \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"publicip\":{\"port_id\":\"${VIP_PORT}\"}}"
```

### Phase 6: Deploy Application + Configure Database Connection

```bash
# Run on each ECS (app-01 shown as example, via SSH)
ssh root@${ECS_IP_01} << 'EOF'
# Download application package from OBS
./obsutil cp obs://my-bucket/releases/app-v1.0.tar.gz /opt/app/ -i=${AK} -k=${SK}

# Extract and deploy
tar -xzf /opt/app/app-v1.0.tar.gz -C /opt/app/
cat > /opt/app/config.env << CONF
DB_HOST=${RDS_PRIVATE_IP}
DB_PORT=3306
DB_NAME=appdb
DB_USER=appuser
DB_PASS=${DB_USER_PASS}
APP_PORT=8080
CONF

# Start app (example: Java)
nohup java -jar /opt/app/app.jar --spring.config.location=/opt/app/config.env > /var/log/app.log 2>&1 &
echo "App started, PID=$!"
EOF
```

### Validation Checklist

```bash
# 1. Check ELB backend node health (expect ONLINE)
curl -s "https://elb.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/elb/pools/${POOL_ID}/members" \
  -H "X-Auth-Token: ${TOKEN}" | python3 -c \
  "import sys,json; [print(m['address'], m['operating_status']) for m in json.load(sys.stdin)['members']]"

# 2. Access application via EIP
curl -I http://${EIP_ADDRESS}/health
# Expected: HTTP/1.1 200 OK

# 3. Verify RDS connectivity (run on any ECS)
mysql -h ${RDS_PRIVATE_IP} -P 3306 -u appuser -p${DB_USER_PASS} appdb -e "SELECT 1;"
```

---

## GitHub Repository

The public version of this skill is hosted at: https://github.com/seagaruda/huaweicloud-rds-skill  
(`SKILL.md` main document + `references/rds-api.md` RDS API quick reference)

---

## Canonical Source

This skill is also published as a GitHub repository for use across AI platforms:
**https://github.com/seagaruda/huaweicloud-rds-skill**

Files in the repo mirror this skill:
- `SKILL.md` — main skill body (English)
- `references/rds-api.md` — RDS v3 API quick reference

When updating the skill, push changes to that repo as well.

## Common Pitfalls

1. **Context saturation silently truncates large write_file/execute_code content**: After a session accumulates large tool outputs (parallel web fetches, multi-read loops), the `content` parameter of `write_file` and `execute_code` is dropped silently, causing writes to fail with "missing required field 'content'". Signals: tool returns the error immediately with no content written, retrying produces the same error.
   - **For write + push**: delegate the entire "write file + git commit + push" to a `delegate_task` subagent with fresh context. Pass the full content via the `goal` string.
   - **For large translation (>400 lines)**: do NOT use a subagent — translation of 500+ lines times out at 600s. Instead, start a **new chat session** and do the translation there.
   - **Splitting strategy**: commit small files first (README, references), then handle the large SKILL.md in a separate session.

2. **EIP binding requires port_id, not server_id**: When binding an EIP, provide the ECS NIC's `port_id`, not the server ID. Get it from `OS-EXT-IPS:port_id` in the ECS details `addresses` field.

3. **ELB backend address is ECS private IP; port is the app port**: `member.address` = ECS private IP, `protocol_port` = actual app listening port (e.g. 8080), not the LB listener port (80).

4. **Removing EIP from shared bandwidth requires specifying new dedicated bandwidth size**: `size` and `charge_mode` are required fields on removal — they define the EIP's standalone config after leaving the shared pool.

5. **OBS does not use IAM Token**: OBS uses AK/SK signing (HMAC-SHA1), not the token used by other services. Use `obsutil` CLI rather than hand-crafting signatures.

6. **ECS creation returns job_id, not server_id directly**: Must poll `GET /v1/{PROJECT_ID}/jobs/{JOB_ID}` until `status=SUCCESS`, then read `entities.server_id`.

7. **RDS and ECS must be in the same VPC**: Cross-VPC RDS access requires a VPC peering connection first — not a direct connection.

8. **Bind EIP to ELB via vip_port_id**: ELB has no direct "bind EIP" API. Query LB details to get `vip_port_id`, then use the EIP binding API to attach that port.

9. **Git push conflict after concurrent remote edits**: If `git pull --rebase` produces a conflict on files where local is canonical, abort and use `git merge -X ours origin/main` instead to keep the local version, then push.
   ```bash
   git rebase --abort
   git fetch origin main
   git merge -X ours origin/main --no-edit
   GH_CONFIG_DIR=/home/zhp/.config/gh git push origin main
   ```

## Verification Checklist

- [ ] TOKEN obtained and not expired (valid 24h)
- [ ] ECS and RDS are in the same VPC and same region
- [ ] RDS security group inbound rule references ECS security group ID (not a CIDR)
- [ ] ELB member `address` = ECS private IP, `protocol_port` = application port
- [ ] ECS creation: poll job_id until SUCCESS before reading server_id
- [ ] OBS upload uses AK/SK, not IAM Token
- [ ] EIP binding uses port_id, not server_id
