# RDS Database

Create and manage relational database instances (MySQL, PostgreSQL, SQL Server).

## API Base

```
https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/
Auth: X-Auth-Token: {TOKEN}
```

## Create MySQL 8.0 Primary/Standby Instance

```bash
curl -s -X POST https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{
    "name": "rds-prod",
    "datastore": {"type": "MySQL", "version": "8.0"},
    "ha": {"mode": "Ha", "replication_mode": "semisync"},
    "password": "{ADMIN_PASSWORD}",
    "flavor_ref": "rds.mysql.c2.large.ha",
    "volume": {"type": "ULTRAHIGH", "size": 100},
    "region": "{REGION}",
    "availability_zone": "{AZ1},{AZ2}",
    "vpc_id": "{VPC_ID}",
    "subnet_id": "{SUBNET_ID}",
    "security_group": {"id": "{RDS_SG_ID}"}
  }'
```

> **⚠️ SECURITY**: Replace `{ADMIN_PASSWORD}` with a strong password from your secrets manager. Never commit real passwords to version control.

### HA Modes

| Mode | Description |
|------|-------------|
| `Ha` | Primary/standby (recommended for production) |
| `Single` | Standalone instance |
| `Replica` | Read replica |

### Replication Modes

| Database | Mode |
|----------|------|
| MySQL | `semisync` |
| PostgreSQL | `async` |
| SQL Server | `sync` |

## Common Operations

```bash
# List instances
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances" \
  -H "X-Auth-Token: {TOKEN}"

# Get instance details
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}" \
  -H "X-Auth-Token: {TOKEN}"

# Restart instance
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/action" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"restart":{}}'

# Change flavor
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/action" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"resize_flavor":{"spec_code":"rds.mysql.c3.xlarge.ha"}}'

# Expand disk
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/action" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"enlarge_volume":{"size":200}}'
```

## Account Management

```bash
# Create database account
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/db_user" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"name":"appuser","password":"{DB_USER_PASS}","databases":[{"name":"appdb","readonly":false}]}'

# List accounts
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/db_user/detail?page=1&limit=100" \
  -H "X-Auth-Token: {TOKEN}"

# Grant database access
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/db_user/privilege" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"user_name":"appuser","databases":[{"name":"newdb","readonly":false}]}'

# Reset password
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/db_user/resetpwd" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"user_name":"appuser","new_password":"{NEW_PASSWORD}"}'
```

> **Password Rules** (MySQL): 8-32 chars, must contain at least 3 of: uppercase, lowercase, digits, special chars (`!@#$%^*-_=+?,`). Cannot contain the account name.

## Backup and Restore

```bash
# Create manual backup
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/backups" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"instance_id":"{ID}","name":"backup-2026-07-16"}'

# List backups
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/backups?instance_id={ID}" \
  -H "X-Auth-Token: {TOKEN}"

# Query restorable time range
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/restore-time?date=2026-07-16" \
  -H "X-Auth-Token: {TOKEN}"

# PITR restore (creates a NEW instance at specified time)
curl -s -X POST "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"name":"rds-restored","source":{"type":"timestamp","instance_id":"{ID}","restore_time":1721000000000}}'
```

> PITR `restore_time` is a millisecond timestamp. Example: `date -d 'yesterday 22:00' +%s%3N`

## Logs and Parameters

```bash
# Query slow logs
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/slowlog?start_date=2026-07-15T00:00:00%2B0800&end_date=2026-07-16T00:00:00%2B0800&offset=1&limit=20" \
  -H "X-Auth-Token: {TOKEN}"

# Query parameters
curl -s "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/configurations" \
  -H "X-Auth-Token: {TOKEN}"

# Modify parameters
curl -s -X PUT "https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}/instances/{ID}/configurations" \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"values":{"max_connections":"500"}}'
```

> Slow log `start_date` format: `yyyy-MM-ddTHH:mm:ss+0800` (URL-encode `+` as `%2B`). Max query range: 30 days.
> If response contains `restart_required:true`, restart the instance for changes to take effect.

## Common MySQL Parameters

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `max_connections` | Max connections | 1 GB→150, 4 GB→500, 8 GB→800 |
| `long_query_time` | Slow query threshold (seconds) | 1-2 for production |
| `innodb_buffer_pool_size` | InnoDB buffer pool (bytes) | 70% of available RAM |
| `character_set_server` | Character set | utf8mb4 |
| `time_zone` | Timezone | +08:00 |

See `references/rds-api.md` for the complete API reference table.
