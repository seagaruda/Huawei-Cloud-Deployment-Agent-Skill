# OBS API Quick Reference

Base: `https://obs.{REGION}.myhuaweicloud.com`
Auth: Signature-based (Access Key + Secret Key) or SAS token

> OBS uses RESTful API with HMAC-SHA256 signature authentication, different from other Huawei Cloud services.

## Bucket Management

| Operation | Method | Path |
|-----------|--------|------|
| Create bucket | PUT | `/{bucket-name}` |
| List buckets | GET | `/` |
| Get bucket info | GET | `/{bucket-name}` |
| Get bucket location | GET | `/{bucket-name}?location` |
| Delete bucket | DELETE | `/{bucket-name}` (must be empty) |
| Set storage policy | PUT | `/{bucket-name}?storageInfo` |
| Get storage policy | GET | `/{bucket-name}?storageInfo` |

Create bucket request:
```
PUT /{bucket-name} HTTP/1.1
Host: {bucket-name}.obs.{REGION}.myhuaweicloud.com
x-obs-acl: private
x-obs-storage-class: Standard

<BucketConfiguration>
  <Location>cn-north-4</Location>
</BucketConfiguration>
```

## Object Management

| Operation | Method | Path |
|-----------|--------|------|
| Upload object | PUT | `/{bucket-name}/{object-key}` |
| Download object | GET | `/{bucket-name}/{object-key}` |
| Delete object | DELETE | `/{bucket-name}/{object-key}` |
| List objects | GET | `/{bucket-name}?list-type=2&max-keys=1000` |
| Copy object | COPY | `/{bucket-name}/{dest-key}` Header: `x-obs-copy-source: /{src-bucket}/{src-key}` |
| Get object info | HEAD | `/{bucket-name}/{object-key}` |

Upload request:
```
PUT /{bucket-name}/{object-key} HTTP/1.1
Host: {bucket-name}.obs.{REGION}.myhuaweicloud.com
Content-Type: application/octet-stream
x-obs-storage-class: Standard
x-obs-acl: private

{object data}
```

## Storage Classes

| Class | Description | Retrieval Time | Cost Level |
|-------|-------------|----------------|------------|
| `Standard` | 标准存储 | 即时 | ★★★ |
| `WARM` | 低频访问存储 | 即时 | ★★ |
| `COLD` | 深度冷存储 | 分钟级 | ★ |
| `GLACIER` | 归档存储 | 小时级 | ★ |

## Lifecycle Rules

| Operation | Method | Path |
|-----------|--------|------|
| Set lifecycle | PUT | `/{bucket-name}?lifecycle` |
| Get lifecycle | GET | `/{bucket-name}?lifecycle` |
| Delete lifecycle | DELETE | `/{bucket-name}?lifecycle` |

Lifecycle configuration:
```xml
<LifecycleConfiguration>
  <Rule>
    <ID>archive-old-files</ID>
    <Status>Enabled</Status>
    <Prefix>logs/</Prefix>
    <Transition>
      <Days>30</Days>
      <StorageClass>WARM</StorageClass>
    </Transition>
    <Transition>
      <Days>90</Days>
      <StorageClass>GLACIER</StorageClass>
    </Transition>
    <Expiration>
      <Days>365</Days>
    </Expiration>
  </Rule>
</LifecycleConfiguration>
```

## CORS Configuration

| Operation | Method | Path |
|-----------|--------|------|
| Set CORS | PUT | `/{bucket-name}?cors` |
| Get CORS | GET | `/{bucket-name}?cors` |
| Delete CORS | DELETE | `/{bucket-name}?cors` |

## Bucket Policies

| Operation | Method | Path |
|-----------|--------|------|
| Set policy | PUT | `/{bucket-name}?policy` |
| Get policy | GET | `/{bucket-name}?policy` |
| Delete policy | DELETE | `/{bucket-name}?policy` |

Public read policy example:
```json
{
  "Version": "2.0",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": ["*"],
      "Action": ["obs:GetObject"],
      "Resource": ["urn:obs:bucket:mybucket/*"]
    }
  ]
}
```

## Multipart Upload

| Operation | Method | Path |
|-----------|--------|------|
| Initiate | POST | `/{bucket-name}/{object-key}?uploads` |
| Upload part | PUT | `/{bucket-name}/{object-key}?partNumber={N}&uploadId={id}` |
| List parts | GET | `/{bucket-name}/{object-key}?uploadId={id}` |
| Complete | POST | `/{bucket-name}/{object-key}?uploadId={id}` |
| Abort | DELETE | `/{bucket-name}/{object-key}?uploadId={id}` |

## SDK Recommendation

推荐使用华为云 OBS SDK（Python）：
```bash
pip install esdk-obs-python
```

```python
from obs import ObsClient
client = ObsClient(access_key_id="...", secret_access_key="...", server="obs.{REGION}.myhuaweicloud.com")
resp = client.putContent("bucket", "key", b"content")
```
