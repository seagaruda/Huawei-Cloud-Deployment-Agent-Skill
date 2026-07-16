# Bandwidth API Quick Reference

Base: `https://vpc.{REGION}.myhuaweicloud.com/v1/{PROJECT_ID}`
Auth: `X-Auth-Token: {TOKEN}`

## Dedicated Bandwidth Management

| Operation | Method | Path |
|-----------|--------|------|
| Create dedicated bandwidth | POST | `/vpc/dedicated-bandwidths` |
| List dedicated bandwidths | GET | `/vpc/dedicated-bandwidths?limit=1000` |
| Get details | GET | `/vpc/dedicated-bandwidths/{dedicated_bandwidth_id}` |
| Update | PUT | `/vpc/dedicated-bandwidths/{dedicated_bandwidth_id}` |
| Delete | DELETE | `/vpc/dedicated-bandwidths/{dedicated_bandwidth_id}` |

Create request body:
```json
{
  "dedicated_bandwidth": {
    "name": "dedicated-bw-01",
    "size": 100,
    "charge_mode": "bandwidth",
    "isp": "CHINAUNICOM"
  }
}
```

## Associate EIP to Dedicated Bandwidth

| Operation | Method | Path |
|-----------|--------|------|
| Associate | POST | `/vpc/dedicated-bandwidths/{dedicated_bandwidth_id}/add` |
| Disassociate | POST | `/vpc/dedicated-bandwidths/{dedicated_bandwidth_id}/remove` |

Associate body:
```json
{
  "publicips": [
    {
      "publicip_id": "{eip_id}"
    }
  ]
}
```

## Shared Bandwidth (VPC Bandwidth)

| Operation | Method | Path |
|-----------|--------|------|
| Create | POST | `/vpc/bandwidths` |
| List | GET | `/vpc/bandwidths?limit=1000` |
| Add EIP to shared bandwidth | POST | `/vpc/bandwidths/{bandwidth_id}/add` |
| Remove EIP from shared bandwidth | POST | `/vpc/bandwidths/{bandwidth_id}/remove` |
| Delete | DELETE | `/vpc/bandwidths/{bandwidth_id}` |

## Bandwidth Comparison

| Feature | Shared Bandwidth | Dedicated Bandwidth |
|---------|-----------------|-------------------|
| Max size | 200 Mbps | 20000 Mbps |
| EIP limit | 50 EIPs | 200 EIPs |
| Use case | 小型业务，共享带宽 | 大型业务，独享带宽 |
| Cost | 按共享带宽计费 | 按专线带宽计费 |
| ISP selection | 不支持 | 支持（电信/联通/移动/BGP） |

## ISP Options

| ISP Code | Name | Coverage |
|----------|------|----------|
| `CHINATELECOM` | 中国电信 | 南方地区 |
| `CHINAUNICOM` | 中国联通 | 北方地区 |
| `CHINAMOBILE` | 中国移动 | 全国 |
| `BGP` | BGP 多线 | 全国（推荐） |

## Common Scenarios

| Scenario | Approach |
|----------|----------|
| 多个 EIP 共享带宽 | 创建 shared bandwidth → 添加 EIPs |
| 大带宽需求（>200Mbps） | 创建 dedicated bandwidth → 关联 EIPs |
| 弹性伸缩 | 使用 shared bandwidth，按需添加/移除 EIP |
| 跨国业务 | dedicated bandwidth + BGP ISP |
