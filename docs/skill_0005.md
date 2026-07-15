# 示例5：查询 RDS 慢日志，定位性能问题

本示例演示如何通过 RDS v3 API 查询数据库慢日志，找出执行时间长的 SQL 语句，进而优化数据库性能。

## 前提条件

- 已有运行中的 RDS 实例
- 已获取 IAM Token 和实例 ID
- 实例已开启慢日志记录（MySQL 默认开启，慢查询阈值 `long_query_time` 默认 10 秒）

## 操作步骤

**步骤1：** 调整慢查询阈值（可选，建议生产环境设为 1-2 秒）。

通过修改实例参数调整 `long_query_time`：

```bash
curl -s -X PUT \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/configurations \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "values": {
      "long_query_time": "1"
    }
  }'
```

**步骤2：** 查询慢日志列表（v3 接口）。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/slowlog?start_date=2024-01-01T00:00:00+0800&end_date=2024-01-02T00:00:00+0800&offset=1&limit=10&type=SELECT" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

> **查询参数说明：**
> - `start_date` / `end_date`：时间范围，格式为 `yyyy-mm-ddThh:mm:ssZ`（UTC+8 即 `+0800`）
> - `type`：SQL 类型，可选 `INSERT`、`UPDATE`、`SELECT`、`DELETE`、`CREATE`
> - `offset`：起始页码，从 1 开始
> - `limit`：每页条数，最大 100

**步骤3：** 解读慢日志响应。

```json
{
  "slow_log_list": [
    {
      "count": "5",
      "time": "3.21s",
      "lock_time": "0.01s",
      "rows_sent": "1000",
      "rows_examined": "500000",
      "database": "myapp_db",
      "users": "app_user",
      "query_sample": "SELECT * FROM orders WHERE created_at > '2024-01-01' AND status = 'pending'",
      "type": "SELECT",
      "start_time": "2024-01-01T10:00:00",
      "client_ip": "192.168.1.50"
    }
  ],
  "total_record": 15,
  "long_query_time": "1"
}
```

> **关键指标说明：**
> - `rows_examined`：扫描行数，远大于 `rows_sent` 说明缺少合适索引
> - `lock_time`：锁等待时间，值大说明存在锁竞争
> - `count`：该 SQL 在统计周期内的执行次数

**步骤4：** 查询慢日志（v3.1 接口，支持更精细筛选）。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3.1/{project_id}/instances/{instance_id}/slowlog?start_date=2024-01-01T00:00:00+0800&end_date=2024-01-02T00:00:00+0800&offset=1&limit=10" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

**步骤5：** 查询错误日志（辅助排查异常）。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/errorlog?start_date=2024-01-01T00:00:00+0800&end_date=2024-01-02T00:00:00+0800&offset=1&limit=10&level=WARNING" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

> `level` 可选：`ALL`、`INFO`、`WARNING`、`ERROR`、`FATAL`

----End

## 注意事项

- 慢日志查询时间范围最长 30 天
- 生产环境建议将 `long_query_time` 设为 1~2 秒，过低（如 0.1 秒）会产生大量日志，影响性能
- `rows_examined / rows_sent` 比值高（>100）通常意味着需要优化索引
- 慢日志只记录超过阈值的 SQL，全量 SQL 审计需开启 [SQL 审计](https://support.huaweicloud.com/usermanual-rds/rds_mysql_0100.html) 功能（额外收费）
- 通过云监控（CES）可配置慢日志数量告警，及时发现性能劣化

父主题：[华为云 RDS 技能实战](../README.md)
