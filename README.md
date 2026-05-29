# Multi-Environment CI/CD Pipeline

A production-grade DevOps project demonstrating a complete CI/CD pipeline with multi-environment deployments on AWS.

## Live Demo
- **Production:** http://multi-env-prod-1281641858.us-east-1.elb.amazonaws.com/health

## Architecture

Developer pushes code to GitHub
→ GitHub Actions runs automated tests
→ Docker image built and pushed to ECR
→ Deploys to DEV automatically
→ Manual approval gate
→ Deploys to STAGING
→ Manual approval gate
→ Deploys to PRODUCTION

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python/Flask | REST API application |
| Docker | Container packaging |
| AWS ECR | Container registry |
| AWS ECS + Fargate | Serverless container hosting |
| AWS ALB | Load balancing and traffic routing |
| AWS CloudWatch | Monitoring, dashboards, and alerts |
| AWS SNS | Alert notifications |
| Terraform | Infrastructure as Code |
| GitHub Actions | CI/CD pipeline automation |

## Environments

Three identical environments managed with Terraform workspaces:

| Environment | Purpose |
|-------------|---------|
| dev | Automatic deployments on every push |
| staging | Manual approval required |
| production | Manual approval required |

## Infrastructure

Each environment contains:
- ECS Cluster (Fargate)
- Application Load Balancer
- CloudWatch Dashboard
- CPU and task count alarms
- SNS email alerts

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /items | Get all items |
| POST | /items | Create an item |

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push to main:

1. **Test** — runs pytest suite automatically
2. **Deploy Dev** — builds Docker image, pushes to ECR, deploys to dev
3. **Deploy Staging** — requires manual approval
4. **Deploy Production** — requires manual approval

Bad code never reaches production — the pipeline blocks any push that fails tests.

## Infrastructure as Code

All AWS infrastructure is defined in Terraform:

```bash
# Deploy an environment
terraform workspace select dev
terraform apply -var="environment=dev"

# Tear down an environment  
terraform workspace select dev
terraform destroy -var="environment=dev"
```

## Project Structure
multi-env-pipeline/
├── app.py                          # Flask API
├── Dockerfile                      # Container definition
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline
├── tests/
│   └── test_app.py                 # Pytest test suite
└── terraform/
├── main.tf                     # Provider and cluster config
├── ecs.tf                      # ECS service and task definition
├── monitoring.tf               # CloudWatch and SNS alerts
├── loadbalancer.tf             # Application load balancer
└── variables.tf                # Input variables

## What I Learned

- Infrastructure as Code with Terraform and workspace-based environment management
- Containerizing applications with Docker and pushing to AWS ECR
- Building multi-stage CI/CD pipelines with GitHub Actions
- Deploying containerized workloads on AWS ECS with Fargate
- Setting up monitoring, alerting, and observability with CloudWatch
- Implementing approval gates to protect production deployments
