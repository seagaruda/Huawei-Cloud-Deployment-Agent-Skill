# 示例1：通过 API 创建 RDS MySQL 主备实例

本示例演示如何通过华为云 RDS v3 API，创建一个 MySQL 8.0 主备高可用实例。

## 前提条件

- 已注册华为云账户并开通 RDS 服务
- 已创建 VPC、子网、安全组
- 已获取 IAM Token 或配置 AK/SK 签名
- 已确认目标区域的 Endpoint 地址（参见 [地区和终端节点](https://developer.huaweicloud.com/endpoint?RDS)）

## 操作步骤

**步骤1：** 获取 IAM Token（以 Token 鉴权为例）。

```bash
curl -s -X POST https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "YOUR_IAM_USERNAME",
            "password": "YOUR_PASSWORD",
            "domain": { "name": "YOUR_ACCOUNT_NAME" }
          }
        }
      },
      "scope": {
        "project": { "name": "cn-north-4" }
      }
    }
  }' -i | grep -i x-subject-token | awk '{print $2}'
```

> 响应头中的 `X-Subject-Token` 即为 Token，有效期 24 小时。

**步骤2：** 准备创建实例的请求体。

```json
{
  "name": "my-rds-mysql",
  "datastore": {
    "type": "MySQL",
    "version": "8.0"
  },
  "ha": {
    "mode": "Ha",
    "replication_mode": "semisync"
  },
  "password": "Test@12345678",
  "flavor_ref": "rds.mysql.c2.large.ha",
  "volume": {
    "type": "ULTRAHIGH",
    "size": 100
  },
  "region": "cn-north-4",
  "availability_zone": "cn-north-4a,cn-north-4b",
  "vpc_id": "YOUR_VPC_ID",
  "subnet_id": "YOUR_SUBNET_ID",
  "security_group": {
    "id": "YOUR_SECURITY_GROUP_ID"
  }
}
```

> **参数说明：**
> - `ha.mode`：`Ha` 为主备，`Single` 为单机
> - `ha.replication_mode`：MySQL 推荐 `semisync`（半同步），PostgreSQL 使用 `async`
> - `flavor_ref`：规格码，可通过 [查询数据库规格](https://support.huaweicloud.com/api-rds/rds_06_0004.html) 接口获取
> - `volume.type`：`ULTRAHIGH`（SSD）或 `LOCALSSD`（本地 SSD）
> - `availability_zone`：主备实例需填两个 AZ，用英文逗号分隔

**步骤3：** 发送创建请求。

```bash
curl -s -X POST \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances \
  -H "Content-Type: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d @request.json
```

**步骤4：** 检查创建任务状态。

创建接口返回 `job_id`，通过以下接口轮询任务进度：

```bash
curl -s -X GET \
  https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/jobs?id={job_id} \
  -H "X-Auth-Token: YOUR_TOKEN"
```

预期响应（创建中）：

```json
{
  "job": {
    "id": "job-xxx",
    "name": "CreateInstance",
    "status": "Running",
    "progress": "30%"
  }
}
```

**步骤5：** 验证实例创建成功。

```bash
curl -s -X GET \
  "https://rds.cn-north-4.myhuaweicloud.com/v3/{project_id}/instances?name=my-rds-mysql" \
  -H "X-Auth-Token: YOUR_TOKEN" | python3 -m json.tool
```

预期结果中 `status` 为 `ACTIVE` 即表示实例创建成功。

----End

## 注意事项

- 实例名称规则：4-64 个字符，字母开头，可含字母、数字、中划线、下划线
- 管理员密码必须包含大写字母、小写字母、数字、特殊字符中的至少 3 类，长度 8-32 位
- 主备实例需跨两个可用区部署，以实现故障自动切换
- 创建完成通常需要 5-15 分钟，请通过 job_id 轮询状态，勿重复提交

父主题：[华为云 RDS 技能实战](../README.md)
