# OBS Object Storage

Create buckets and upload/download objects. OBS uses AK/SK signing, NOT IAM Token.

## Authentication

OBS uses **AK/SK** (Access Key / Secret Key) with HMAC-SHA1 signing. Create an access key in the Huawei Cloud console first.

> **⚠️ SECURITY**: Store AK/SK in environment variables. Never hardcode.

## Create Bucket (via curl — manual signing)

```bash
curl -s -X PUT https://{BUCKET_NAME}.obs.{REGION}.myhuaweicloud.com \
  -H "Authorization: OBS {AK}:{SIGNATURE}" \
  -H "Date: {GMT_DATE}" \
  -H "x-obs-acl: private"
```

## Upload File (via curl — manual signing)

```bash
curl -s -X PUT \
  https://{BUCKET_NAME}.obs.{REGION}.myhuaweicloud.com/{OBJECT_KEY} \
  -H "Authorization: OBS {AK}:{SIGNATURE}" \
  -H "Date: {GMT_DATE}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/your/image.tar.gz
```

## Recommended: Use obsutil CLI

Manually computing OBS signatures is error-prone. Use the official `obsutil` CLI instead:

```bash
# Install obsutil
wget https://obs-community.obs.cn-north-1.myhuaweicloud.com/obsutil/current/linux_amd64/obsutil_linux_amd64.tar.gz
tar -xzf obsutil_linux_amd64.tar.gz && chmod +x obsutil

# Configure AK/SK (stores credentials locally)
./obsutil config -i={AK} -k={SK} -e=obs.{REGION}.myhuaweicloud.com

# Upload
./obsutil cp /local/image.tar.gz obs://{BUCKET_NAME}/images/image.tar.gz

# Download
./obsutil cp obs://{BUCKET_NAME}/images/image.tar.gz /local/

# List objects
./obsutil ls obs://{BUCKET_NAME}/
```

> **⚠️ PITFALL**: OBS does NOT use IAM Token. Other services (ECS, VPC, ELB, RDS) use `X-Auth-Token`, but OBS uses AK/SK signing only.
