# Elastic Public IP (EIP)

Apply for and manage elastic public IP addresses.

## API Base

```
https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/
Auth: X-Auth-Token: {TOKEN}
```

## Apply for Dedicated EIP

```bash
# 5 BGP, billed by bandwidth (5 Mbps)
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "publicip": {"type": "5_bgp"},
    "bandwidth": {"name": "bw-app", "size": 5, "share_type": "PER", "charge_mode": "bandwidth"}
  }'
# Returns: publicip.id and public_ip_address
```

## Bind EIP to ECS

```bash
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID}/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"publicip": {"port_id": "{PORT_ID}"}}'
```

> **⚠️ PITFALL**: `port_id` is the ECS NIC's port ID, NOT the server ID. Get it from `OS-EXT-IPS:port_id` in the ECS details `addresses` field.

## Bind EIP to ELB

```bash
# First get ELB vip_port_id
VIP_PORT=$(curl -s "https://elb.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/elb/loadbalancers/{LB_ID}" \
  -H "X-Auth-Token: {TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['loadbalancer']['vip_port_id'])")

# Then bind
curl -s -X PUT https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID} \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d "{\"publicip\":{\"port_id\":\"${VIP_PORT}\"}}"
```

## Unbind EIP

```bash
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}/publicips/{EIP_ID}/action \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"publicip": {"port_id": null}}'
```
