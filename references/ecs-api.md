# ECS API Quick Reference

Base: `https://ecs.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}`
Auth: `X-Auth-Token: {TOKEN}`

## Server Management

| Operation | Method | Path |
|-----------|--------|------|
| Create server | POST | `/cloudservers` |
| List servers | GET | `/cloudservers?limit=1000` |
| Get server details | GET | `/cloudservers/{server_id}` |
| Start | POST | `/cloudservers/{server_id}/OS-EXT-STS:start` |
| Stop (soft) | POST | `/cloudservers/{server_id}/OS-EXT-STS:stop` |
| Reboot (soft) | POST | `/cloudservers/{server_id}/OS-EXT-SRV-ATTR:reboot` type: `SOFT` |
| Force reboot | POST | `/cloudservers/{server_id}/OS-EXT-SRV-ATTR:reboot` type: `HARD` |
| Delete | DELETE | `/cloudservers/{server_id}` |

Create request body:
```json
{
  "server": {
    "name": "ecs-web-01",
    "imageRef": "{image_id}",
    "flavorRef": "{flavor_id}",
    "key_pair": "{keypair_name}",
    "networks": [
      {
        "uuid": "{network_id}"
      }
    ],
    "vpcid": "{vpc_id}",
    "security_groups": [
      {"id": "{sg_id}"}
    ],
    "availability_zone": "{az}",
    "root_volume": {
      "volumetype": "SSD",
      "size": 40
    },
    "data_volumes": [
      {
        "volumetype": "SSD",
        "size": 100
      }
    ],
    "auto_recovery": true,
    "auto_renew": false
  }
}
```

## Server Parameters

| Field | Description | Notes |
|-------|-------------|-------|
| `imageRef` | 镜像 ID | 通过镜像服务 API 获取 |
| `flavorRef` | 规格 ID | 通过 flavor 列表 API 获取 |
| `key_pair` | SSH 密钥对名称 | Linux 必需 |
| `admin_pass` | 管理员密码 | Windows 必需，8-16 位，含大小写+数字 |
| `auto_recovery` | 自动恢复 | 推荐设为 `true` |
| `availability_zone` | 可用区 | 格式：`{region}-{az}`，如 `cn-north-4a` |

## Volume Management

| Operation | Method | Path |
|-----------|--------|------|
| Attach volume | POST | `/cloudservers/{server_id}/os-volumes` body: `{"volumeId":"{volume_id}"}` |
| Detach volume | DELETE | `/cloudservers/{server_id}/os-volumes/{volume_id}` |

## Resize / Change Flavor

| Operation | Method | Path |
|-----------|--------|------|
| Change flavor | PUT | `/cloudservers/{server_id}/changeFlavor` |
| Confirm resize | POST | `/cloudservers/{server_id}/OS-EXT-SRV-ATTR:confirmResize` |
| Revert resize | POST | `/cloudservers/{server_id}/OS-EXT-SRV-ATTR:revertResize` |

Change flavor body:
```json
{
  "changeFlavor": {
    "flavorRef": "{new_flavor_id}",
    "OS-EXT-SRV-ATTR:adminPass": "{password}"
  }
}
```

## Flavor Query

GET `/flavors` — 查询可用规格

| Filter | Example |
|--------|---------|
| `flavorRam` | `flavorRam=4096` (MB) |
| `flavorVcpus` | `flavorVcpus=2` |
| `availability_zone` | `availability_zone=cn-north-4a` |

## Image Query

GET `/os-images/ext-images?limit=1000` — 查询外部镜像

常用镜像名称关键字：
- `CentOS 7.9`
- `Ubuntu 22.04`
- `Windows Server 2022`
- `EulerOS 2.0`

## Server Tags

| Operation | Method | Path |
|-----------|--------|------|
| Add tags | POST | `/cloudservers/{server_id}/tags` body: `{"tags":[{"key":"env","value":"prod"}]}` |
| List tags | GET | `/cloudservers/{server_id}/tags` |
| Delete tag | DELETE | `/cloudservers/{server_id}/tags/{tag_name}` |

## Common Errors

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| `QuotaExceeded` | 配额不足 | 申请提升配额 |
| `FlavorNotFound` | 规格不存在 | 检查 flavor ID 和可用区 |
| `ImageNotFound` | 镜像不存在 | 检查 image ID |
| `NetworkNotFound` | 网络不存在 | 检查 VPC 和子网 |
