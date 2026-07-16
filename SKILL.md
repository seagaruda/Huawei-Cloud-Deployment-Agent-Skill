# Huawei Cloud Deployment Skill

Helps deploy monolithic or distributed applications to Huawei Cloud, covering the complete infrastructure chain.

## When to Use

- User says "deploy my app to Huawei Cloud", "create an ECS", "configure a security group"
- User says "apply for a public IP", "set up load balancing for ECS", "multi-node deployment"
- User says "upload image to OBS", "how does ECS connect to RDS"
- Not applicable for: GaussDB, DCS, DDS and other database products; K8s/CCE container deployments

## Security Best Practices

> **⚠️ IMPORTANT**: All examples use placeholder variables. Never hardcode real credentials.

| Credential | How to Handle |
|-----------|---------------|
| `TOKEN` (IAM) | Store in env var; valid 24h, rotate regularly |
| `PASSWORD` / `DB_ADMIN_PASS` | Use a secrets manager (e.g., Huawei Cloud CSS); never commit to Git |
| `AK` / `SK` (OBS) | Store in env vars; restrict IAM user permissions to minimum required |
| `DB_USER_PASS` | Generate strong passwords; rotate periodically |

**Before running any script:**
```bash
export TOKEN="your-iam-token"
export REGION="cn-north-4"
export PROJECT_ID="your-project-id"
export PASSWORD="your-ecs-password"
export DB_ADMIN_PASS="your-rds-admin-password"
export DB_USER_PASS="your-app-db-password"
export AK="your-access-key"
export SK="your-secret-key"
```

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

## Module Index

Each module is a standalone file. Load the relevant module(s) based on user intent.

| # | Module | File | Description |
|---|--------|------|-------------|
| 1 | Security Groups | [`modules/01-security-groups.md`](modules/01-security-groups.md) | Create SGs, add rules, port reference, SG mutual access |
| 2 | ECS Cloud Servers | [`modules/02-ecs.md`](modules/02-ecs.md) | Create instances, batch start/stop, job polling, flavors |
| 3 | EIP | [`modules/03-eip.md`](modules/03-eip.md) | Apply EIP, bind to ECS/ELB, unbind |
| 4 | Shared Bandwidth | [`modules/04-bandwidth.md`](modules/04-bandwidth.md) | Create shared bandwidth, add/remove EIPs |
| 5 | OBS | [`modules/05-obs.md`](modules/05-obs.md) | Create buckets, AK/SK upload, obsutil CLI |
| 6 | ECS ↔ RDS | [`modules/06-ecs-rds.md`](modules/06-ecs-rds.md) | Security group setup, connection strings |
| 7 | ELB | [`modules/07-elb.md`](modules/07-elb.md) | LB → Listener → Pool → Members → Health check → Bind EIP |
| 8 | RDS | [`modules/08-rds.md`](modules/08-rds.md) | Create instances, backup/restore, accounts, slow logs, parameters |
| 9 | End-to-End | [`modules/09-end-to-end.md`](modules/09-end-to-end.md) | Complete 3-node Web app + MySQL deployment script |

See `references/rds-api.md` for the RDS v3 API quick reference table.

---

## Common Pitfalls

1. **EIP binding requires port_id, not server_id**: Get it from `OS-EXT-IPS:port_id` in the ECS details `addresses` field.

2. **ELB backend address is ECS private IP; port is the app port**: `member.address` = ECS private IP, `protocol_port` = actual app listening port (e.g. 8080), not the LB listener port (80).

3. **Removing EIP from shared bandwidth requires specifying new dedicated bandwidth size**: `size` and `charge_mode` are required fields on removal.

4. **OBS does not use IAM Token**: OBS uses AK/SK signing (HMAC-SHA1), not the token used by other services. Use `obsutil` CLI.

5. **ECS creation returns job_id, not server_id directly**: Must poll `GET /v1/{PROJECT_ID}/jobs/{JOB_ID}` until `status=SUCCESS`, then read `entities.server_id`.

6. **RDS and ECS must be in the same VPC**: Cross-VPC RDS access requires a VPC peering connection first.

7. **Bind EIP to ELB via vip_port_id**: ELB has no direct "bind EIP" API. Query LB details to get `vip_port_id`, then use the EIP binding API.

---

## Verification Checklist

- [ ] TOKEN obtained and not expired (valid 24h)
- [ ] ECS and RDS are in the same VPC and same region
- [ ] RDS security group inbound rule references ECS security group ID (not a CIDR)
- [ ] ELB member `address` = ECS private IP, `protocol_port` = application port
- [ ] ECS creation: poll job_id until SUCCESS before reading server_id
- [ ] OBS upload uses AK/SK, not IAM Token
- [ ] EIP binding uses port_id, not server_id

---

## GitHub Repository

This skill is hosted at: **https://github.com/seagaruda/Huawei-Cloud-Deployment-Agent-Skill**
