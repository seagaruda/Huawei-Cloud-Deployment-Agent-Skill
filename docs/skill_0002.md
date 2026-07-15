# 示例2：查询 RDS 实例列表

本示例演示如何通过 RDS v3 API 获取当前账号下所有数据库实例的信息。

## 前提条件

- 已获取 IAM Token（获取方式参见示例1）
- 已知目标区域的 Endpoint 和 project_id

## 操作步骤

**步骤1：** 查询所有实例（不带过滤条件）。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

**步骤2：** 按数据库类型过滤查询。

```bash
# 仅查询 MySQL 实例
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances?datastore_type=MySQL" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

**步骤3：** 按实例类型过滤查询。

```bash
# 仅查询主备实例
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances?type=Ha" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

> `type` 可选值：`Single`（单机）、`Ha`（主备）、`Replica`（只读）、`Enterprise`（企业版）

**步骤4：** 分页查询。

```bash
# 从第 0 条开始，每页取 10 条
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances?offset=0&limit=10" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

**步骤5：** 解读响应结果。

```json
{
  "instances": [
    {
      "id": "instance-id-xxx",
      "name": "my-rds-mysql",
      "status": "ACTIVE",
      "type": "Ha",
      "datastore": {
        "type": "MySQL",
        "version": "8.0"
      },
      "flavor_ref": "rds.mysql.c2.large.ha",
      "volume": {
        "type": "ULTRAHIGH",
        "size": 100,
        "used": 12.5
      },
      "region": "cn-north-4",
      "availability_zone": "cn-north-4a",
      "private_ips": ["192.168.1.100"],
      "public_ips": [],
      "port": 3306,
      "nodes": [
        {
          "id": "node-xxx",
          "name": "my-rds-mysql_node0",
          "role": "master",
          "status": "ACTIVE",
          "availability_zone": "cn-north-4a"
        },
        {
          "id": "node-yyy",
          "name": "my-rds-mysql_node1",
          "role": "slave",
          "status": "ACTIVE",
          "availability_zone": "cn-north-4b"
        }
      ],
      "created": "2024-01-01T00:00:00+0800"
    }
  ],
  "total_count": 1
}
```

> **关键字段说明：**
> - `status`：`ACTIVE`（运行中）、`FAILED`（失败）、`BUILD`（创建中）、`STORAGE FULL`（磁盘满）
> - `nodes`：主备实例含 master 和 slave 两个节点
> - `private_ips`：实例内网 IP，应用程序通过此 IP 连接数据库
> - `volume.used`：已使用磁盘空间（GB）

----End

## 注意事项

- `limit` 最大值为 100，超出会报参数错误
- 单次查询返回最多 100 条，如实例数量超过 100 需配合 `offset` 分页
- `private_ips` 仅在同 VPC 内可访问；跨 VPC 访问需配置对等连接或 VPN

父主题：[华为云 RDS 技能实战](../README.md)
