# Security Groups

Manage VPC security groups and rules for controlling network access.

## API Base

```
https://vpc.{REGION}.myhuaweicloud.com/v2.0/
Auth: X-Auth-Token: {TOKEN}
```

## Create Security Group

```bash
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-groups \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"security_group": {"name": "sg-web-app", "description": "Web application security group"}}'
```

## Add Inbound Rule

```bash
# Open HTTP port 80 from anywhere
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "security_group_rule": {
      "security_group_id": "{SG_ID}", "direction": "ingress",
      "protocol": "tcp", "port_range_min": 80, "port_range_max": 80,
      "remote_ip_prefix": "0.0.0.0/0"
    }
  }'

# Allow another security group (recommended for ECS→RDS)
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "security_group_rule": {
      "security_group_id": "{RDS_SG_ID}", "direction": "ingress",
      "protocol": "tcp", "port_range_min": 3306, "port_range_max": 3306,
      "remote_group_id": "{ECS_SG_ID}"
    }
  }'
```

## Common Port Reference

| Port | Service | Notes |
|------|---------|-------|
| 22 | SSH | Linux remote access |
| 80 | HTTP | Web traffic |
| 443 | HTTPS | Encrypted web traffic |
| 3306 | MySQL | Database |
| 3389 | RDP | Windows remote access |
| 5432 | PostgreSQL | Database |
| 8080 | Custom | Common app port |
| 8443 | Custom | Secure app port |

## Key Points

- **Security group mutual access** (`remote_group_id`) is more secure than `remote_ip_prefix` (CIDR)
- ECS to RDS: use `remote_group_id={ECS_SG_ID}` instead of `0.0.0.0/0`
- Each security group can have up to 100 rules
