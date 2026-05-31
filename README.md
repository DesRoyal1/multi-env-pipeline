# Multi-Environment CI/CD Pipeline
### Production-grade serverless DevOps project — built in a single day

**Live Demo:** https://q1wkih2prc.execute-api.us-east-1.amazonaws.com

---

## What This Is

A complete cloud infrastructure project demonstrating end-to-end DevOps engineering — from infrastructure as code to automated deployments to real-time observability. The live dashboard shows every system component working in real time with glass wall transparency.

**Cost: $0/month** — built entirely on AWS free tier using serverless architecture.

---

## Live Glass Wall Dashboard

Visit the live URL to see the system operating in real time:

- **Environment Health** — all 3 environments monitored live
- **Lambda Metrics** — invocations, duration, error rate from CloudWatch
- **Live Graphs** — 30-minute rolling charts updating every 20 seconds
- **DynamoDB Stats** — record count, active table, monthly cost ($0.00)
- **Log Terminal** — real CloudWatch logs streaming to the browser
- **Interactive Controls** — buttons that cause real AWS actions

### What Each Button Does

| Button | What Happens in AWS |
|--------|-------------------|
| Fire Test Request | Real HTTP request hits API Gateway → Lambda invokes → appears in log terminal |
| Write Test Record | Lambda writes to DynamoDB → record count increments → log entry appears |
| Stress Test (100 req) | 100 real requests fire → invocations spike on graph → cost: $0.00002 |
| Inject Error | CloudWatch error metric injected → error graph spikes → proves monitoring works |

---

## Architecture
GitHub push
→ GitHub Actions runs pytest
→ Terraform packages Lambda + dependencies
→ Deploys to DEV automatically
→ Manual approval gate
→ Deploys to STAGING
→ Manual approval gate
→ Deploys to PRODUCTION
→ API Gateway routes traffic
→ Lambda handles requests
→ DynamoDB stores data
→ CloudWatch monitors everything

---

## Tech Stack

| Technology | Purpose | Cost |
|-----------|---------|------|
| AWS Lambda | Serverless API hosting | FREE (1M req/month) |
| AWS API Gateway | Public HTTPS endpoint | FREE (1M calls/month) |
| AWS DynamoDB | Persistent NoSQL database | FREE (25GB forever) |
| AWS CloudWatch | Metrics, logs, alarms | FREE (5GB/month) |
| AWS SNS | Incident alerts | FREE (1M notifications) |
| Terraform | Infrastructure as Code | FREE |
| GitHub Actions | CI/CD pipeline | FREE (2000 min/month) |
| Python / Flask | REST API application | FREE |

**Total monthly cost: $0.00**

---

## Three Environments

Managed with Terraform workspaces — one codebase, three isolated deployments.

| Environment | URL | Deployment |
|-------------|-----|-----------|
| Development | Auto-deployed on every push | Immediate |
| Staging | Approval-gated | Manual approval required |
| Production | Approval-gated | Manual approval required |

---

## CI/CD Pipeline

Every push to main triggers the full pipeline:

Test    — pytest with mocked AWS (no credentials needed)
Dev     — Terraform packages and deploys Lambda automatically
Staging — requires manual approval in GitHub
Prod    — requires manual approval in GitHub


18+ documented pipeline runs visible in GitHub Actions.

---

## Reliability System
CloudWatch monitors Lambda error rate
→ Errors spike above threshold
→ Alarm triggers healing Lambda
→ Healing Lambda health-checks the API
→ SNS sends email alert
→ System recovers automatically

---

## Infrastructure as Code

Every AWS resource defined in Terraform — nothing clicked in the console.
terraform/
├── main.tf            # Provider config
├── lambda.tf          # Lambda functions and IAM
├── apigateway.tf      # API Gateway routes
├── dynamo.tf          # DynamoDB tables
├── monitoring.tf      # CloudWatch alarms and SNS
└── lambda_healing.tf  # Self-healing system

Rebuild entire infrastructure from scratch:
```bash
terraform workspace select prod
terraform apply -var="environment=prod" -auto-approve
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Glass wall dashboard |
| GET | /health | Health check |
| GET | /products | List inventory |
| POST | /products | Create item |
| DELETE | /products/:id | Remove item |
| GET | /api/metrics | Live Lambda metrics |
| GET | /api/logs | CloudWatch log stream |
| GET | /api/db | DynamoDB stats |
| POST | /api/test-transaction | Rate-limited write demo |
| POST | /api/loadtest | Rate-limited stress test |
| POST | /api/trigger-error | Rate-limited error injection |

---

## Security

- All interactive endpoints rate-limited per IP
- Stress test: once per 2 minutes
- Write test: once per 30 seconds  
- Error injection: once per 60 seconds
- HTTPS enforced via API Gateway
- IAM least-privilege policies on all Lambda functions

---

## Load Test Results

| Metric | Result |
|--------|--------|
| Total requests | 5,000 |
| Success rate | 100% |
| Average response | 222ms |
| Peak throughput | 445 req/sec |
| Cost for 5,000 requests | $0.001 |

---

## Project Structure
multi-env-pipeline/
├── app.py                    # Flask REST API + glass wall endpoints
├── lambda_handler.py         # API Gateway → Flask adapter
├── build.sh                  # Packages dependencies for Lambda
├── Dockerfile                # Local development container
├── requirements.txt          # Python dependencies
├── templates/
│   └── status.html           # Glass wall dashboard
├── lambda/
│   └── heal.py               # Self-healing Lambda function
├── tests/
│   └── test_app.py           # pytest suite with mocked AWS
└── terraform/
├── main.tf
├── lambda.tf
├── apigateway.tf
├── dynamo.tf
├── monitoring.tf
└── lambda_healing.tf

---

## Engineering Decisions

**Why Lambda over ECS?**
Serverless eliminates idle compute cost. ECS costs ~$40/month running 24/7. Lambda costs $0 at portfolio traffic levels. For this workload serverless is the correct architectural choice.

**Why Terraform workspaces?**
One set of infrastructure code creates three identical isolated environments. Changes propagate consistently — no environment drift.

**Why mock AWS in tests?**
Unit tests validate logic not infrastructure. Mocking makes tests fast, free, and runnable without AWS credentials. The pipeline tests run in under 15 seconds.

**Why rate limit public buttons?**
The dashboard URL appears on a public resume. Rate limiting prevents abuse while keeping the demo interactive and safe.

---

## Resume Bullets

- Architected serverless REST API using AWS Lambda and API Gateway across dev, staging, and production environments — achieving zero infrastructure cost through serverless design
- Provisioned all AWS infrastructure as code using Terraform workspaces enabling repeatable isolated environment deployments from a single configuration
- Built multi-stage CI/CD pipeline with GitHub Actions featuring automated pytest, Terraform deployments, and approval-gated production releases
- Implemented automated incident response using CloudWatch alarms and Lambda self-healing achieving automatic recovery without human intervention
- Built real-time operations dashboard pulling live metrics from CloudWatch, DynamoDB, and API Gateway — demonstrating end-to-end system observability
