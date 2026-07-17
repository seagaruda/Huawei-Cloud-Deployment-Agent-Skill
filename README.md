# Huawei Cloud Deployment Agent Skill

A complete Huawei Cloud deployment skill for all AI platforms, enabling any AI Agent to handle full-stack cloud deployments — from basic networking to databases — using natural language.

## Features Covered

| Module | Operations |
|--------|------------|
| **Security Groups** | Create, add inbound/outbound rules, common port reference, security group interconnection |
| **ECS Cloud Servers** | Create, bulk start/stop, query status, job polling, flavor reference |
| **EIP Elastic Public IP** | Apply for dedicated EIP, bind to ECS/ELB, unbind |
| **Shared Bandwidth Package** | Create shared bandwidth, add/remove EIPs |
| **OBS Object Storage** | Create Bucket, AK/SK signed upload, obsutil CLI recommended usage |
| **ECS ↔ RDS Connection** | Security group setup, private network connection strings (MySQL/PG/JDBC) |
| **ELB Load Balancer** | Create LB → Listener → Backend Server Group → Add nodes → Health check → Bind EIP |
| **RDS Database** | Create primary/standby instances, backup & restore, account management, slow logs, parameter configuration |
| **End-to-End Scenario** | Complete script for a 3-node Web app + MySQL from scratch to production |

Supported Huawei Cloud regions: `cn-north-4`, `cn-east-3`, `cn-south-1`, and all other commercial regions  
API versions: ECS v1, VPC v2.0, ELB v3, RDS v3, OBS v1

## File Structure

```
Huawei-Cloud-Deployment-Agent-Skill/
├── SKILL.md                          # Main entry (overview + module index)
├── modules/                          # Modular skill files (load by intent)
│   ├── 01-security-groups.md         # Security groups & rules
│   ├── 02-ecs.md                     # ECS cloud servers
│   ├── 03-eip.md                     # Elastic Public IP
│   ├── 04-bandwidth.md               # Shared bandwidth packages
│   ├── 05-obs.md                     # OBS object storage
│   ├── 06-ecs-rds.md                 # ECS ↔ RDS connectivity
│   ├── 07-elb.md                     # ELB load balancing
│   ├── 08-rds.md                     # RDS database management
│   └── 09-end-to-end.md             # Full deployment scenario
├── references/
│   └── rds-api.md                    # RDS v3 API quick reference
├── scripts/                          # CI validation scripts
│   ├── validate_api_commands.py      # Validate JSON in curl payloads
│   ├── validate_links.py            # Check internal cross-references
│   ├── check_secrets.py             # Detect hardcoded secrets
│   ├── extract_endpoints.py          # Extract API endpoint patterns
│   └── validate_endpoints.py         # Verify endpoint URL formats
├── .github/workflows/
│   └── validate.yml                  # GitHub Actions CI pipeline
├── LICENSE                           # Apache License 2.0
└── README.md                        # This file
```

## Supported AI Platforms

| Platform | Usage |
|----------|-------|
| **Claude Projects** | Paste the contents of `SKILL.md` into Project Instructions |
| **Cursor** | Save as `.cursor/rules/huaweicloud-deploy.mdc` |
| **GitHub Copilot** | Save as `.github/copilot-instructions.md` |
| **ChatGPT / Custom GPT** | Paste into System Prompt or Instructions |
| **Dify / FastGPT / Coze** | Import as system prompt or knowledge base document |
| **Hermes Agent** | Place at `~/.hermes/skills/devops/huaweicloud-deploy/SKILL.md` |
| **Any Platform** | Paste the full `SKILL.md` content as the System Prompt |

## CI/CD Pipeline

This repository includes a GitHub Actions workflow (`.github/workflows/validate.yml`) that:

- **Validates JSON syntax** in all curl command payloads
- **Checks internal cross-references** between SKILL.md and module files
- **Scans for hardcoded secrets** (passwords, tokens, AK/SK)
- **Extracts and validates API endpoint patterns**
- **Runs weekly** (Monday 02:00 UTC) to catch API changes

## Quick Start

### Claude Projects

1. Open [Claude Projects](https://claude.ai/projects)
2. Go to project settings → Instructions
3. Copy the full contents of `SKILL.md` and paste it in
4. Example prompt:
   > "Deploy a 3-node web app in cn-north-4 with 4 vCPU / 8 GB, connected to a MySQL primary/standby setup"

### Cursor

```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/huaweicloud-deploy.mdc \
  https://raw.githubusercontent.com/seagaruda/Huawei-Cloud-Deployment-Agent-Skill/main/SKILL.md
```

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills/devops/huaweicloud-deploy
curl -o ~/.hermes/skills/devops/huaweicloud-deploy/SKILL.md \
  https://raw.githubusercontent.com/seagaruda/Huawei-Cloud-Deployment-Agent-Skill/main/SKILL.md
# Optional: sync module files
mkdir -p ~/.hermes/skills/devops/huaweicloud-deploy/modules
for f in 01-security-groups 02-ecs 03-eip 04-bandwidth 05-obs 06-ecs-rds 07-elb 08-rds 09-end-to-end; do
  curl -o ~/.hermes/skills/devops/huaweicloud-deploy/modules/${f}.md \
    https://raw.githubusercontent.com/seagaruda/Huawei-Cloud-Deployment-Agent-Skill/main/modules/${f}.md
done
```

## Conversation Examples

```
User: Create a security group and open ports 80, 443, and 22
User: Spin up 3 ECS instances with 4 vCPU / 8 GB, using the Ubuntu 22.04 image
User: Apply for a public IP and bind it to the ELB
User: Help me configure the connection from ECS to RDS — how do I set up the security group?
User: Create an ELB, add these 3 ECS instances to it, health check path is /health
User: Create a MySQL 8.0 primary/standby instance with 100 GB SSD, in the same VPC as the ECS
User: Restore the production database to 10:00 AM this morning
User: Check my slow SQL queries — recent queries have been running slow
User: Deploy a 3-node web app with MySQL from scratch and give me the complete script
```

## Official Documentation

- [ECS API Reference](https://support.huaweicloud.com/api-ecs/zh-cn_topic_0020212668.html)
- [VPC / Security Group API Reference](https://support.huaweicloud.com/api-vpc/vpc_sg01_0001.html)
- [ELB API Reference](https://support.huaweicloud.com/api-elb/elb_jd_0001.html)
- [RDS API Reference](https://support.huaweicloud.com/api-rds/rds_01_0001.html)
- [OBS API Reference](https://support.huaweicloud.com/api-obs/obs_04_0001.html)

## License

Apache License 2.0 — See [LICENSE](LICENSE) for details.

## Contact
www.seagaruda.com
