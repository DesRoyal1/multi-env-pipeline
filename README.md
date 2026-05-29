# Multi-Environment CI/CD Pipeline

A production-grade DevOps project built in a single day demonstrating 
a complete CI/CD pipeline with multi-environment deployments, 
auto-scaling, self-healing, and real-time monitoring on AWS.

## 🌐 Live Demo
**Status Page:** http://multi-env-prod-1281641858.us-east-1.elb.amazonaws.com

## 🏗 Architecture
Developer pushes code to GitHub
→ GitHub Actions runs automated tests (mocked DynamoDB)
→ Docker image built and pushed to ECR
→ Deploys to DEV automatically
→ Manual approval gate
→ Deploys to STAGING
→ Manual approval gate
→ Deploys to PRODUCTION
## ⚡ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python/Flask | REST API application |
| Docker | Container packaging |
| AWS ECR | Container registry |
| AWS ECS + Fargate | Serverless container hosting |
| AWS DynamoDB | Persistent NoSQL database |
| AWS ALB | Load balancing and traffic routing |
| AWS Lambda | Self-healing incident response |
| AWS CloudWatch | Monitoring, dashboards, and alerts |
| AWS SNS | Alert notifications |
| AWS Auto Scaling | Automatic container scaling |
| Terraform | Infrastructure as Code |
| GitHub Actions | CI/CD pipeline automation |

## 🌍 Environments

Three identical environments managed with Terraform workspaces:

| Environment | Purpose | Deployment |
|-------------|---------|------------|
| dev | Developer testing | Automatic on every push |
| staging | Pre-production verification | Manual approval required |
| production | Live user traffic | Manual approval required |

## 📊 Load Test Results

| Metric | 1K Requests | 5K Requests |
|--------|-------------|-------------|
| Success Rate | 100% | 100% |
| Avg Response | 120ms | 222ms |
| Throughput | 410 req/sec | 445 req/sec |
| Failures | 0 | 0 |

## 🔧 Infrastructure Per Environment

Each environment contains:
- ECS Cluster (Fargate) — serverless containers
- Application Load Balancer — traffic routing
- DynamoDB Table — persistent product storage
- Auto Scaling (1-5 containers) — handles traffic spikes
- CloudWatch Dashboard — CPU and memory monitoring
- CloudWatch Alarms — CPU high/low triggers
- Lambda Self-Healing — auto-restarts on failure
- SNS Email Alerts — instant incident notifications

## 🛡 Self-Healing System
App goes down
→ CloudWatch detects zero running tasks
→ Triggers Lambda automatically
→ Lambda forces new ECS deployment
→ Sends email alert
→ App recovers without human intervention
## 📈 Auto Scaling
CPU > 70% for 2 minutes → scales UP by 2 containers
CPU < 30% for 3 minutes → scales DOWN by 1 container
Minimum containers      → 1
Maximum containers      → 5
## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Live status page |
| GET | /health | Health check |
| GET | /products | List all products |
| POST | /products | Create a product |
| GET | /products/:id | Get one product |
| PUT | /products/:id | Update stock |
| DELETE | /products/:id | Delete a product |

## 🚀 CI/CD Pipeline

```yaml
Push to main
  → Test (pytest with mocked DynamoDB)
    → Deploy Dev (automatic)
      → Deploy Staging (manual approval)
        → Deploy Production (manual approval)
```

Bad code never reaches production.
The pipeline blocks any push that fails tests.

## 📁 Project Structure
multi-env-pipeline/
├── app.py                          # Flask REST API
├── Dockerfile                      # Container definition
├── requirements.txt                # Python dependencies
├── templates/
│   └── status.html                 # Live status page
├── lambda/
│   └── heal.py                     # Self-healing function
├── tests/
│   └── test_app.py                 # Pytest suite (mocked)
└── terraform/
├── main.tf                     # Provider and cluster
├── ecs.tf                      # ECS service and tasks
├── dynamo.tf                   # DynamoDB tables
├── loadbalancer.tf             # Application load balancer
├── autoscaling.tf              # Auto scaling policies
├── monitoring.tf               # CloudWatch and SNS
├── lambda_healing.tf           # Self-healing Lambda
└── variables.tf                # Input variables
## 🔑 What This Demonstrates

- **IaC** — entire AWS infrastructure defined in Terraform
- **CI/CD** — automated testing and multi-stage deployments
- **Containerization** — Docker with ECR registry
- **Reliability** — auto-scaling and self-healing
- **Observability** — CloudWatch dashboards and alerts
- **Security** — least privilege IAM, approval gates
- **Performance** — 445 req/sec, 100% uptime under load
