# Shared Bandwidth Package

Create and manage shared bandwidth packages for multiple EIPs.

## API Base

```
https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/
Auth: X-Auth-Token: {TOKEN}
```

## Create Shared Bandwidth

```bash
curl -s -X POST https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"name": "shared-bw-prod", "size": 50}}'
# Returns: bandwidth.id
```

## Add EIP to Shared Bandwidth

```bash
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths/{BW_ID}/insert \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"publicip_info": [{"publicip_id": "{EIP_ID}", "publicip_type": "5_bgp"}]}}'
```

## Remove EIP from Shared Bandwidth

```bash
curl -s -X POST \
  https://vpc.{REGION}.myhuaweicloud.com/v2.0/{PROJECT_ID}/bandwidths/{BW_ID}/remove \
  -H "Content-Type: application/json" -H "X-Auth-Token: {TOKEN}" \
  -d '{"bandwidth": {"publicip_info": [{"publicip_id": "{EIP_ID}", "publicip_type": "5_bgp"}], "size": 5, "charge_mode": "bandwidth"}}'
```

> **⚠️ PITFALL**: When removing an EIP from shared bandwidth, you MUST specify `size` and `charge_mode` — these define the EIP's standalone bandwidth config after leaving the shared pool.
