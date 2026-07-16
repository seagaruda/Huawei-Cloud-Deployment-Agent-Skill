# ECS to RDS Connectivity

Configure secure private network connectivity between ECS instances and RDS databases.

## Prerequisites

- ECS and RDS must be in the **same VPC**
- Cross-VPC access requires a VPC peering connection first

## Step 1: Security Group Setup

Add an inbound rule to the RDS security group that allows the ECS security group to access the database port:

```bash
# Allow ECS SG → RDS SG on MySQL port 3306
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/security-group-rules \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "security_group_rule": {
      "security_group_id": "{RDS_SG_ID}",
      "direction": "ingress",
      "protocol": "tcp",
      "port_range_min": 3306,
      "port_range_max": 3306,
      "remote_group_id": "{ECS_SG_ID}"
    }
  }'
```

> **Best Practice**: Use `remote_group_id` (security group mutual access) instead of `remote_ip_prefix` (CIDR). This is more secure because it automatically tracks ECS instances.

## Step 2: Get RDS Private IP

Query the RDS instance details to get the private IP:

```bash
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{RDS_ID}" \
  -H "X-Auth-Token: {TOKEN}"
# Read from response: private_ips[0]
```

The private IP is reachable within the same VPC only.

## Step 3: Connection Strings

### MySQL

```bash
# CLI
mysql -h {RDS_PRIVATE_IP} -P 3306 -u {DB_USER} -p {DB_NAME}

# Application config (JDBC)
jdbc:mysql://{RDS_PRIVATE_IP}:3306/{DB_NAME}?useSSL=true
```

### PostgreSQL

```bash
# CLI
psql -h {RDS_PRIVATE_IP} -p 5432 -U {DB_USER} -d {DB_NAME}

# Application config (JDBC)
jdbc:postgresql://{RDS_PRIVATE_IP}:5432/{DB_NAME}
```

### Environment Variable Configuration

```bash
# Recommended: use environment variables for all credentials
export DB_HOST="${RDS_PRIVATE_IP}"
export DB_PORT=3306
export DB_NAME="appdb"
export DB_USER="appuser"
export DB_PASS="${DB_USER_PASS}"
```
