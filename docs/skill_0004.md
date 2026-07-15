# 示例4：为 MySQL 实例创建数据库账号并授权

本示例演示如何通过 API 为 RDS for MySQL 实例创建数据库账号，并为其授权访问指定数据库。

## 前提条件

- 已有运行中的 RDS for MySQL 实例
- 已获取 IAM Token 和实例 ID
- 目标数据库已存在（如需新建，需先通过控制台或 SQL 语句创建）

## 操作步骤

**步骤1：** 创建数据库账号。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/db_user \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "name": "app_user",
    "password": "App@12345678",
    "comment": "应用程序使用的数据库账号"
  }'
```

> **密码规则：** 至少 8 位，包含大写字母、小写字母、数字、特殊字符中的至少 3 类。特殊字符支持 `!@#$%^*-_=+?,`

**步骤2：** 查询账号列表，确认创建成功。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/db_user/detail?page=1&limit=100" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

预期响应：

```json
{
  "users": [
    {
      "name": "app_user",
      "comment": "应用程序使用的数据库账号",
      "hosts": []
    }
  ],
  "total_count": 1
}
```

**步骤3：** 授予账号对指定数据库的权限。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/db_user/privilege \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d '{
    "user_name": "app_user",
    "databases": [
      {
        "name": "myapp_db",
        "readonly": false
      }
    ]
  }'
```

> - `readonly: false`：读写权限
> - `readonly: true`：只读权限

**步骤4：** 验证授权结果，查询账号的数据库权限。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances/{instance_id}/db_user/database?user-name=app_user&page=1&limit=100" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

**步骤5：** 使用账号连接数据库（需在同 VPC 内的 ECS 上执行）。

```bash
mysql -h 192.168.1.100 -P 3306 -u app_user -p myapp_db
```

输入密码后，成功进入 MySQL 提示符即表示连接正常：

```
mysql>
```

----End

## 注意事项

- 账号名不能使用 MySQL 系统保留名（如 `root`、`mysql`、`information_schema`）
- 不支持创建超级管理员（SUPER 权限）账号，高权限操作请通过控制台使用管理员账号执行
- 修改账号密码使用 PUT 接口：`PUT /v3/{project_id}/instances/{instance_id}/db_user/resetpwd`
- 删除账号前请确认没有应用程序正在使用该账号，否则会导致连接失败

父主题：[华为云 RDS 技能实战](../README.md)
