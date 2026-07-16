# ECS Cloud Servers

Create and manage Elastic Cloud Server instances.

## API Base

```
https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/
Auth: X-Auth-Token: {TOKEN}
```

## Create ECS Instance

```bash
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "server": {
      "name": "app-server-01",
      "imageRef": "{IMAGE_ID}",
      "flavorRef": "c3.xlarge.2",
      "availability_zone": "{AZ}",
      "vpcid": "{VPC_ID}",
      "nics": [{"subnet_id": "{SUBNET_ID}"}],
      "security_groups": [{"id": "{SG_ID}"}],
      "root_volume": {"volumetype": "SSD", "size": 50},
      "adminPass": "{PASSWORD}"
    }
  }'
```

> **⚠️ SECURITY**: Set `PASSWORD` from environment variable. Never hardcode.

### Important: Job Polling Required

ECS creation returns a `job_id`, NOT a `server_id` directly. You must poll:

```bash
# Poll until status=SUCCESS
while true; do
  STATUS=$(curl -s "https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/jobs/{JOB_ID}" \
    -H "X-Auth-Token: {TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  [ "$STATUS" = "SUCCESS" ] && break
  echo "waiting... $STATUS"; sleep 10
done
# Then read entities.server_id from the job response
```

## Batch Operations

```bash
# Start servers
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"os-start": {"servers": [{"id": "{SERVER_ID}"}]}}'

# Stop servers (SOFT = graceful shutdown)
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"os-stop": {"type":"SOFT","servers":[{"id":"{SERVER_ID}"}]}}'

# Reboot servers
curl -s -X POST https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"reboot": {"type":"SOFT","servers":[{"id":"{SERVER_ID}"}]}}'
```

## Query Instances

```bash
curl -s "https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/cloudservers/detail?limit=20&offset=1" \
  -H "X-Auth-Token: {TOKEN}"
```

### Instance Status

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Running |
| `SHUTOFF` | Stopped |
| `BUILD` | Creating |
| `ERROR` | Abnormal |

### Flavor Reference

| Flavor | vCPU | Memory | Type |
|--------|------|--------|------|
| `s6.large.2` | 2 | 4 GB | General |
| `c3.xlarge.2` | 4 | 8 GB | Compute |
| `m3.xlarge.8` | 4 | 32 GB | Memory |
