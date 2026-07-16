# VPC Security Groups API Quick Reference

Base: `https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}`
Auth: `X-Auth-Token: {TOKEN}`

## Security Group Management

| Operation | Method | Path |
|-----------|--------|------|
| Create security group | POST | `/vpc/security-groups` |
| List security groups | GET | `/vpc/security-groups?limit=1000` |
| Get security group details | GET | `/vpc/security-groups/{security_group_id}` |
| Update security group | PUT | `/vpc/security-groups/{security_group_id}` |
| Delete security group | DELETE | `/vpc/security-groups/{security_group_id}` |

Create request body:
```json
{
  "security_group": {
    "name": "sg-web",
    "description": "Web server security group",
    "vpc_id": "{vpc_id}"
  }
}
```

## Security Group Rules

| Operation | Method | Path |
|-----------|--------|------|
| Add rule | POST | `/vpc/security-groups/{security_group_id}/security-group-rules` |
| List rules | GET | `/vpc/security-groups/{security_group_id}/security-group-rules?limit=1000` |
| Delete rule | DELETE | `/vpc/security-groups/{security_group_id}/security-group-rules/{rule_id}` |

Add rule request body:
```json
{
  "security_group_rule": {
    "direction": "ingress",
    "ethertype": "IPv4",
    "protocol": "tcp",
    "port_range_min": 80,
    "port_range_max": 80,
    "remote_ip_prefix": "0.0.0.0/0",
    "description": "Allow HTTP"
  }
}
```

### Rule Parameters

| Field | Values | Description |
|-------|--------|-------------|
| `direction` | `ingress` / `egress` | 方向 |
| `ethertype` | `IPv4` / `IPv6` | IP 版本 |
| `protocol` | `tcp` / `udp` / `icmp` / `-1`(all) | 协议 |
| `port_range_min` | 1–65535 | 起始端口（protocol=-1 时不填） |
| `port_range_max` | 1–65535 | 结束端口 |
| `remote_ip_prefix` | CIDR | 远端 IP 段 |
| `remote_security_group_id` | UUID | 远端安全组 ID（二选一） |

## Associate/Disassociate Instances

| Operation | Method | Path |
|-----------|--------|------|
| Associate instance | POST | `/vpc/security-groups/{security_group_id}/add_instance` body: `{"instance_id":"{server_id}"}` |
| Disassociate instance | POST | `/vpc/security-groups/{security_group_id}/remove_instance` body: `{"instance_id":"{server_id}"}` |

## Common Port Rules

| Service | Protocol | Port | Direction |
|---------|----------|------|-----------|
| SSH | tcp | 22 | ingress |
| HTTP | tcp | 80 | ingress |
| HTTPS | tcp | 443 | ingress |
| RDP | tcp | 3389 | ingress |
| MySQL | tcp | 3306 | ingress |
| PostgreSQL | tcp | 5432 | ingress |
| Redis | tcp | 6379 | ingress |

## Query Security Groups by Tag

GET `/vpc/security-groups?tags.key={key}&tags.value={value}`
