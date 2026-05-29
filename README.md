# Multi-Environment CI/CD Pipeline

A production-grade DevOps project demonstrating a complete automated deployment system with self-healing infrastructure, auto-scaling, and real-time monitoring on AWS.

**Live Demo:** http://multi-env-prod-1281641858.us-east-1.elb.amazonaws.com

---

## What This Project Demonstrates

This project solves the core problem every software company faces — how do you ship code updates quickly and safely without breaking things for users?

The answer is a fully automated pipeline that tests every change, deploys through multiple environments with approval gates, monitors itself 24/7, and recovers automatically from failures.

---

## Architecture
Developer pushes code to GitHub
→ GitHub Actions runs automated tests
→ Docker image built and pushed to ECR
→ Deploys to DEV automatically
→ Manual approval gate
→ Deploys to STAGING
→ Manual approval gate
→ Deploys to PRODUCTION

Bad code never reaches production. The pipeline blocks any push that fails tests.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Application | Python / Flask | REST API with 6 endpoints |
| Database | AWS DynamoDB | Persistent NoSQL storage |
| Containerization | Docker | Consistent environments everywhere |
| Registry | AWS ECR | Container image storage |
| Hosting | AWS ECS + Fargate | Serverless container orchestration |
| Networking | AWS ALB | Load balancing and traffic routing |
| Scaling | AWS Auto Scaling | 1-5 containers based on CPU |
| Monitoring | AWS CloudWatch | Dashboards, alarms, logs |
| Alerting | AWS SNS | Email notifications on incidents |
| Self-Healing | AWS Lambda | Automatic restart on failure |
| IaC | Terraform | All infrastructure defined as code |
| CI/CD | GitHub Actions | Automated test and deploy pipeline |

---

## Three Environments

Each environment is identical infrastructure, managed independently with Terraform workspaces.

| Environment | Purpose | Deployment Trigger |
|-------------|---------|-------------------|
| Development | Developer testing | Automatic on every push |
| Staging | Pre-production verification | Manual approval required |
| Production | Live traffic | Manual approval required |

Each environment has its own:
- ECS cluster and Fargate service
- DynamoDB table
- Application Load Balancer
- CloudWatch dashboard
- Auto scaling policies
- Lambda self-healing function
- SNS alert topic

---

## CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push to main:

Test        → pytest suite with mocked DynamoDB (no AWS needed)
Deploy Dev  → build Docker image, push to ECR, update ECS service
Deploy Staging → requires manual approval in GitHub
Deploy Prod    → requires manual approval in GitHub


Nothing reaches production without passing tests and two approval gates.

---

## Infrastructure as Code

Every AWS resource is defined in Terraform — nothing was clicked in the console.
terraform/
├── main.tf              # Provider config and ECS cluster
├── ecs.tf               # ECS task definition and service
├── dynamo.tf            # DynamoDB table
├── loadbalancer.tf      # Application load balancer
├── autoscaling.tf       # Auto scaling policies
├── monitoring.tf        # CloudWatch dashboards and SNS alerts
└── lambda_healing.tf    # Self-healing Lambda function

Deploy any environment from scratch:
```bash
terraform workspace select prod
terraform apply -var="environment=prod"
```

---

## Auto Scaling
CPU > 70% for 2 minutes  →  scale UP by 2 containers
CPU < 30% for 3 minutes  →  scale DOWN by 1 container
Minimum                  →  1 container
Maximum                  →  5 containers

---

## Self-Healing System
App goes down
→ CloudWatch detects zero running tasks (within 60 seconds)
→ Triggers Lambda automatically
→ Lambda forces new ECS deployment
→ Sends email alert via SNS
→ App recovers without human intervention

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Live status page |
| GET | /health | Health check |
| GET | /products | List all products |
| POST | /products | Create a product |
| GET | /products/:id | Get one product |
| PUT | /products/:id | Update stock level |
| DELETE | /products/:id | Remove a product |

---

## Load Test Results

Tested with [hey](https://github.com/rakyll/hey) load testing tool:

| Test | Requests | Concurrent | Success Rate | Avg Response | Throughput |
|------|----------|-----------|-------------|-------------|-----------|
| Test 1 | 1,000 | 50 | 100% | 120ms | 410 req/sec |
| Test 2 | 5,000 | 100 | 100% | 222ms | 445 req/sec |

Zero failures across 6,000 total requests.

---

## Project Structure
multi-env-pipeline/
├── app.py                         # Flask REST API
├── Dockerfile                     # Container definition
├── requirements.txt               # Python dependencies
├── templates/
│   └── status.html                # Live status and demo page
├── lambda/
│   └── heal.py                    # Self-healing Lambda function
├── tests/
│   └── test_app.py                # Pytest suite with DynamoDB mocking
└── terraform/
├── main.tf
├── ecs.tf
├── dynamo.tf
├── loadbalancer.tf
├── autoscaling.tf
├── monitoring.tf
└── lambda_healing.tf

---

## Key Engineering Decisions

**Why Fargate over EC2?**
No server management. AWS handles patching, scaling the underlying infrastructure, and availability. Pay only for what you use.

**Why DynamoDB over RDS?**
Serverless, scales automatically, no connection pooling issues with containers, and fits the simple key-value access patterns of product inventory.

**Why mock DynamoDB in tests?**
Unit tests should test logic, not infrastructure. Mocking makes tests fast, free, and runnable anywhere without AWS credentials. Integration tests would use real AWS in a separate test account.

**Why Terraform workspaces over separate directories?**
One set of infrastructure code that creates identical environments. Changes to infrastructure apply everywhere consistently — no drift between environments.

---

## Resume Bullet Points

- Architected multi-environment CI/CD pipeline deploying containerized Flask API across dev, staging, and production on AWS ECS Fargate using Terraform IaC and GitHub Actions
- Implemented auto-scaling policies that scale containers from 1 to 5 under CPU load, reducing cost at idle while maintaining 445 req/sec throughput under load testing
- Built automated incident response system using CloudWatch alarms, Lambda self-healing, and SNS escalation — achieving automatic recovery without human intervention
- Provisioned all AWS infrastructure as code using Terraform workspaces, enabling repeatable environment creation and eliminating manual console configuration