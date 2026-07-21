# End-to-End Scenario: 3-Node Web App + MySQL

Complete deployment script for a production-ready distributed application.

## Target Architecture

```
Internet → EIP → ELB(HTTP:80) → app-01(8080)
                               → app-02(8080)  → RDS MySQL 8.0 (primary/standby)
                               → app-03(8080)
```

All operations depend on `TOKEN`, `REGION`, `PROJECT_ID`. Assumes VPC and subnet already exist.

---

## Phase 1: Security Groups

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

# 1c. sg-web: open SSH(22), app port(8080)
for PORT in 22 8080; do
  curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-group-rules \
    -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
    -d "{\"security_group_rule\":{\"security_group_id\":\"${SG_WEB}\",\"direction\":\"ingress\",
          \"protocol\":\"tcp\",\"port_range_min\":${PORT},\"port_range_max\":${PORT},
          \"remote_ip_prefix\":\"0.0.0.0/0\"}}"
done

> **Note**: `${PORT}` is a bash variable expanded at runtime. Replace with actual port numbers (e.g., `22`, `8080`) when testing individual commands.

# 1d. sg-db: allow only sg-web to reach MySQL 3306 (security group mutual access)
curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"security_group_rule\":{\"security_group_id\":\"${SG_DB}\",\"direction\":\"ingress\",
       \"protocol\":\"tcp\",\"port_range_min\":3306,\"port_range_max\":3306,
       \"remote_group_id\":\"${SG_WEB}\"}}"
```

---

## Phase 2: Create 3 ECS Instances

```bash
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
    [ "$STATUS" = "FAIL" ] && { echo "Job failed"; exit 1; }
    echo "  waiting... $STATUS"; sleep 10
  done
done
```

---

## Phase 3: Apply for EIP + Shared Bandwidth

```bash
# 3a. Create shared bandwidth (50 Mbps)
BW_ID=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v2.0/${PROJECT_ID}/bandwidths \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"bandwidth":{"name":"shared-bw-prod","size":50}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['bandwidth']['id'])")

# 3b. Apply for EIP (to be bound to ELB)
EIP_ID=$(curl -s -X POST https://vpc.${REGION}.myhuaweicloud.com/v1/${PROJECT_ID}/publicips \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d '{"publicip":{"type":"5_bgp"},"bandwidth":{"name":"bw-elb","size":50,"share_type":"PER","charge_mode":"bandwidth"}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['publicip']['id'])")
```

---

## Phase 4: Create RDS MySQL Primary/Standby

```bash
RDS_ID=$(curl -s -X POST https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances \
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
echo "RDS instance_id=${RDS_ID}"

# Wait for RDS to become available (poll ~5-10 min)
while true; do
  S=$(curl -s "https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances/${RDS_ID}" \
    -H "X-Auth-Token: ${TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['instance']['status'])")
  [ "$S" = "available" ] && break
  [ "$S" = "error" ] || [ "$S" = "failed" ] && { echo "RDS failed: $S"; exit 1; }
  echo "  RDS status=$S, waiting..."; sleep 30
done

# Create application database account
curl -s -X POST https://rds.${REGION}.myhuaweicloud.com/v3/${PROJECT_ID}/instances/${RDS_ID}/db_user \
  -H "Content-Type: application/json" -H "X-Auth-Token: ${TOKEN}" \
  -d "{\"name\":\"appuser\",\"password\":\"${DB_USER_PASS}\",
       \"databases\":[{\"name\":\"appdb\",\"readonly\":false}]}"
```

---

## Phase 5: ELB Configuration

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

# 5d. Add 3 ECS instances to backend
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

---

## Phase 6: Deploy Application

```bash
# Run on each ECS (app-01 shown as example, via SSH)
ssh root@${ECS_IP_01} << EOF
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

---

## Validation Checklist

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
