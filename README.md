# 华为云业务上云 Agent Skill

一个面向所有 AI 平台的华为云完整部署技能文件，让任何 AI Agent 通过自然语言完成从基础网络到数据库的全链路云上部署。

## 覆盖功能

| 模块 | 操作 |
|------|------|
| **安全组** | 创建、添加入/出方向规则、常用端口速查、安全组互通 |
| **ECS 云服务器** | 创建、批量启停、查询状态、job 轮询、规格速查 |
| **EIP 弹性公网 IP** | 申请独享 EIP、绑定到 ECS/ELB、解绑 |
| **共享带宽包** | 创建共享带宽、加入/移出 EIP |
| **OBS 对象存储** | 创建 Bucket、AK/SK 签名上传、obsutil CLI 推荐用法 |
| **ECS ↔ RDS 连接** | 安全组打通、内网连接字符串（MySQL/PG/JDBC） |
| **ELB 负载均衡** | 创建 LB → 监听器 → 后端服务器组 → 添加节点 → 健康检查 → 绑 EIP |
| **RDS 数据库** | 创建主备实例、备份恢复、账号管理、慢日志、参数配置 |
| **端到端场景** | 3节点 Web 应用 + MySQL 从零到上线完整脚本 |

支持华为云区域：`cn-north-4`、`cn-east-3`、`cn-south-1` 等所有商业区域  
API 版本：ECS v1、VPC v2.0、ELB v3、RDS v3、OBS v1

## 支持的 AI 平台

| 平台 | 使用方式 |
|------|---------|
| **Claude Projects** | 将 `SKILL.md` 内容粘贴到 Project Instructions |
| **Cursor** | 保存为 `.cursor/rules/huaweicloud-deploy.mdc` |
| **GitHub Copilot** | 保存为 `.github/copilot-instructions.md` |
| **ChatGPT / Custom GPT** | 粘贴到 System Prompt 或 Instructions |
| **Dify / FastGPT / Coze** | 作为系统提示词或知识库文档导入 |
| **Hermes Agent** | 放入 `~/.hermes/skills/devops/huaweicloud-deploy/SKILL.md` |
| **任意平台** | 将 `SKILL.md` 全文粘贴为 System Prompt 即可 |

## 快速使用

### Claude Projects

1. 打开 [Claude Projects](https://claude.ai/projects)
2. 进入项目设置 → Instructions
3. 复制 `SKILL.md` 全文粘贴进去
4. 对话示例：
   > "帮我在 cn-north-4 部署 3 节点 Web 应用，4核8G，接 MySQL 主备"

### Cursor

```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/huaweicloud-deploy.mdc \
  https://raw.githubusercontent.com/seagaruda/huaweicloud-rds-skill/main/SKILL.md
```

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills/devops/huaweicloud-deploy
curl -o ~/.hermes/skills/devops/huaweicloud-deploy/SKILL.md \
  https://raw.githubusercontent.com/seagaruda/huaweicloud-rds-skill/main/SKILL.md
# 可选：同步 RDS API 参考
mkdir -p ~/.hermes/skills/devops/huaweicloud-deploy/references
curl -o ~/.hermes/skills/devops/huaweicloud-deploy/references/rds-api.md \
  https://raw.githubusercontent.com/seagaruda/huaweicloud-rds-skill/main/references/rds-api.md
```

## 对话示例

```
用户：帮我创建一个安全组，开放 80、443、22 端口
用户：建 3 台 4核8G 的 ECS，镜像用 Ubuntu 22.04
用户：申请一个公网 IP 绑到 ELB 上
用户：帮我配一下 ECS 到 RDS 的连接，安全组怎么打通？
用户：创建一个 ELB，把这 3 台 ECS 加进去，健康检查路径是 /health
用户：创建 MySQL 8.0 主备实例，100G SSD，和 ECS 在同一个 VPC
用户：把生产库恢复到今天上午 10 点
用户：帮我查一下慢 SQL，最近查询变慢了
用户：从零开始部署一个 3 节点 Web 应用加 MySQL，给我完整脚本
```

## 文件结构

```
huaweicloud-rds-skill/
├── SKILL.md                  # 主技能文档（直接用于 AI 提示词）
└── references/
    └── rds-api.md            # RDS v3 API 快速参考表
```

## 官方文档

- [ECS API 参考](https://support.huaweicloud.com/api-ecs/zh-cn_topic_0020212668.html)
- [VPC/安全组 API 参考](https://support.huaweicloud.com/api-vpc/vpc_sg01_0001.html)
- [ELB API 参考](https://support.huaweicloud.com/api-elb/elb_jd_0001.html)
- [RDS API 参考](https://support.huaweicloud.com/api-rds/rds_01_0001.html)
- [OBS API 参考](https://support.huaweicloud.com/api-obs/obs_04_0001.html)
