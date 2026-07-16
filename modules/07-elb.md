# ELB Load Balancing

Create and configure Elastic Load Balancer for multi-node deployments.

## API Base

```
https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/
Auth: X-Auth-Token: {TOKEN}
```

## Full Setup Flow

### Step 1: Create Load Balancer

```bash
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/loadbalancers \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "loadbalancer": {
      "name": "lb-prod",
      "vpc_id": "{VPC_ID}",
      "vip_subnet_cidr_id": "{SUBNET_ID}",
      "availability_zone_list": ["{AZ}"],
      "guaranteed": false
    }
  }'
# guaranteed=false = shared type (free tier)
# guaranteed=true = dedicated type (requires l4_flavor_id or l7_flavor_id)
# Returns: loadbalancer.id
```

### Step 2: Create Listener

```bash
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/listeners \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "listener": {
      "name": "listener-http-80",
      "loadbalancer_id": "{LB_ID}",
      "protocol": "HTTP",
      "protocol_port": 80
    }
  }'
# Protocol options: TCP / UDP / HTTP / HTTPS / TERMINATED_HTTPS
# Returns: listener.id
```

### Step 3: Create Backend Server Group

```bash
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/pools \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "pool": {
      "name": "pool-app",
      "protocol": "HTTP",
      "lb_algorithm": "ROUND_ROBIN",
      "listener_id": "{LISTENER_ID}"
    }
  }'
# lb_algorithm: ROUND_ROBIN / LEAST_CONNECTIONS / SOURCE_IP
# Returns: pool.id
```

### Step 4: Add Backend Members

```bash
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/pools/{POOL_ID}/members \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "member": {
      "name": "member-ecs-01",
      "address": "{ECS_PRIVATE_IP}",
      "protocol_port": 8080,
      "subnet_cidr_id": "{SUBNET_ID}",
      "weight": 1
    }
  }'
```

> **⚠️ PITFALL**: `address` = ECS **private** IP. `protocol_port` = actual app listening port (e.g., 8080), NOT the LB listener port (80).

### Step 5: Configure Health Check

```bash
curl -s -X POST https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/healthmonitors \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "healthmonitor": {
      "pool_id": "{POOL_ID}",
      "type": "HTTP",
      "monitor_port": 8080,
      "url_path": "/health",
      "delay": 5,
      "timeout": 3,
      "max_retries": 3
    }
  }'
# type: TCP / HTTP / HTTPS; url_path only valid for HTTP/HTTPS
```

### Step 6: Bind EIP to ELB

```bash
# Get ELB vip_port_id
VIP_PORT=$(curl -s "https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/loadbalancers/{LB_ID}" \
  -H "X-Auth-Token: {TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['loadbalancer']['vip_port_id'])")

# Bind EIP using vip_port_id
curl -s -X PUT https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID} \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d "{\"publicip\":{\"port_id\":\"${VIP_PORT}\"}}"
```

> **⚠️ PITFALL**: ELB has no direct "bind EIP" API. You must query the LB details to get `vip_port_id`, then use the EIP binding API.

## Verify Backend Health

```bash
curl -s "https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/pools/{POOL_ID}/members" \
  -H "X-Auth-Token: {TOKEN}" | python3 -c \
  "import sys,json; [print(m['address'], m['operating_status']) for m in json.load(sys.stdin)['members']]"
# Expected: ONLINE for healthy members
```
