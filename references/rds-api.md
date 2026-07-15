# RDS v3 API Quick Reference

Base: `https://rds.{REGION}.myhuaweicloud.com/v3/{PROJECT_ID}`
Auth: `X-Auth-Token: {TOKEN}`

## Instance Management

| Operation | Method | Path |
|-----------|--------|------|
| Create instance | POST | `/instances` |
| List instances | GET | `/instances?datastore_type=MySQL&type=Ha` |
| Get instance details | GET | `/instances/{id}` |
| Restart | POST | `/instances/{id}/action` body: `{"restart":{}}` |
| Change flavor | POST | `/instances/{id}/action` body: `{"resize_flavor":{"spec_code":"..."}}` |
| Expand disk | POST | `/instances/{id}/action` body: `{"enlarge_volume":{"size":200}}` |
| Delete | DELETE | `/instances/{id}` |

Instance `ha.mode`: `Ha` primary/standby / `Single` standalone / `Replica` read replica
Replication mode: MySQL=`semisync`, PG=`async`, SQLServer=`sync`

## Backup and Restore

| Operation | Method | Path |
|-----------|--------|------|
| Set auto-backup policy | PUT | `/instances/{id}/backups/policy` |
| Create manual backup | POST | `/backups` body: `{"instance_id":"...","name":"..."}` |
| List backups | GET | `/backups?instance_id={id}` |
| Query restorable time range | GET | `/instances/{id}/restore-time?date=YYYY-MM-DD` |
| PITR restore (new instance) | POST | `/instances` body with `source.type=timestamp` |
| Restore from backup (new instance) | POST | `/instances` body with `source.type=backup` |
| Delete manual backup | DELETE | `/backups/{backup_id}` |

PITR `restore_time` is a millisecond timestamp: `date -d "yesterday 22:00" +%s%3N`

## Account Management (MySQL)

| Operation | Method | Path |
|-----------|--------|------|
| Create account | POST | `/instances/{id}/db_user` |
| List accounts | GET | `/instances/{id}/db_user/detail?page=1&limit=100` |
| Grant database access | POST | `/instances/{id}/db_user/privilege` body: `{"user_name":"...","databases":[{"name":"...","readonly":false}]}` |
| Reset password | POST | `/instances/{id}/db_user/resetpwd` |
| Delete account | DELETE | `/instances/{id}/db_user/{user_name}` |

Password rules: 8–32 chars, must contain at least 3 of: uppercase, lowercase, digits, special chars (`!@#$%^*-_=+?,`). Cannot contain the account name.

## Logs and Parameters

| Operation | Method | Path |
|-----------|--------|------|
| Query slow logs | GET | `/instances/{id}/slowlog?start_date=...&end_date=...&offset=1&limit=20` |
| Query error logs | GET | `/instances/{id}/errorlog?level=WARNING&...` |
| Query parameters | GET | `/instances/{id}/configurations` |
| Modify parameters | PUT | `/instances/{id}/configurations` body: `{"values":{"max_connections":"500"}}` |

Slow log `start_date` format: `yyyy-MM-ddTHH:mm:ss+0800` (URL-encode `+` as `%2B`). Max query range: 30 days.
If the response contains `restart_required:true`, restart the instance for the change to take effect.

## Common MySQL Parameters

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| `max_connections` | Max connections | 1 GB RAM→150, 4 GB→500, 8 GB→800 |
| `long_query_time` | Slow query threshold (seconds) | 1–2 for production |
| `innodb_buffer_pool_size` | InnoDB buffer pool (bytes) | 70% of available RAM |
| `character_set_server` | Character set | utf8mb4 |
| `time_zone` | Timezone | +08:00 |
