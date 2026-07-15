# 示例3：RDS 备份与按时间点恢复（PITR）

本示例演示如何创建手动备份，并通过按时间点恢复（PITR）将数据恢复到新实例。

## 前提条件

- 已有运行中的 RDS 实例（`status: ACTIVE`）
- 已开启自动备份策略（PITR 依赖自动备份）
- 已获取 IAM Token

## 操作步骤

**步骤1：** 创建手动备份。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/backups \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "instance_id": "YOUR_INSTANCE_ID",
    "name": "manual-backup-20240101",
    "description": "重要变更前手动备份"
  }'
```

预期响应：

```json
{
  "backup": {
    "id": "backup-id-xxx",
    "name": "manual-backup-20240101",
    "status": "BUILDING",
    "instance_id": "YOUR_INSTANCE_ID",
    "type": "manual",
    "created": "2024-01-01T10:00:00+0800"
  }
}
```

**步骤2：** 查询备份状态。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/backups?instance_id=YOUR_INSTANCE_ID" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

当 `status` 变为 `COMPLETED` 时备份完成。

**步骤3：** 查询可恢复时间段（PITR 前必做）。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/YOUR_INSTANCE_ID/restore-time?date=2024-01-01" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

预期响应：

```json
{
  "restore_time": [
    {
      "start_time": 1704038400000,
      "end_time": 1704124800000
    }
  ]
}
```

> `start_time` 和 `end_time` 为 Unix 时间戳（毫秒），表示可恢复的时间范围。

**步骤4：** 按时间点恢复到新实例（PITR）。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "name": "pitr-restored-instance",
    "source": {
      "instance_id": "YOUR_INSTANCE_ID",
      "type": "timestamp",
      "restore_time": 1704067200000
    },
    "target": {
      "flavor_ref": "rds.mysql.c2.large",
      "volume": {
        "type": "ULTRAHIGH",
        "size": 100
      },
      "availability_zone": "cn-north-4a",
      "vpc_id": "YOUR_VPC_ID",
      "subnet_id": "YOUR_SUBNET_ID",
      "security_group": { "id": "YOUR_SG_ID" }
    }
  }'
```

**步骤5：** 按备份文件恢复到新实例。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "name": "backup-restored-instance",
    "source": {
      "instance_id": "YOUR_INSTANCE_ID",
      "type": "backup",
      "backup_id": "backup-id-xxx"
    },
    "target": {
      "flavor_ref": "rds.mysql.c2.large",
      "volume": {
        "type": "ULTRAHIGH",
        "size": 100
      },
      "availability_zone": "cn-north-4a",
      "vpc_id": "YOUR_VPC_ID",
      "subnet_id": "YOUR_SUBNET_ID",
      "security_group": { "id": "YOUR_SG_ID" }
    }
  }'
```

----End

## 注意事项

- PITR 仅支持 MySQL 和 PostgreSQL 引擎
- `restore_time` 必须在步骤3查询到的可恢复时间段内，否则返回 400 错误
- 恢复操作不影响原实例，数据恢复到新建实例上
- 自动备份默认保留 7 天，手动备份永久保留（按量计费）直到手动删除
- 备份文件所在地域必须与恢复目标 Endpoint 一致，跨区域恢复需先做备份复制

父主题：[华为云 RDS 技能实战](../README.md)
