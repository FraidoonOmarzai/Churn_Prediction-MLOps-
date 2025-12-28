# Why Multi-Stage Builds vs Normal Dockerfiles

🔴 Traditional Single-Stage Dockerfile (The Old Way)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install build tools AND runtime dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libgomp1 \
    curl

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

❌ Problems with Single-Stage:

1. Bloated Image: Final image contains unnecessary build tools (gcc, g++, make)
2. Larger Size: ~800MB - 1.2GB for a simple app
3. Security Risk: More packages = more potential vulnerabilities
4. Slower Deployment: Larger images take longer to push/pull

🟢 Multi-Stage Dockerfile (Modern Way)
Stage 1: Builder

```
dockerfileFROM python:3.10-slim AS builder
# Purpose: Compile and build dependencies
```

What happens here:

- Installs build tools (gcc, make, compilers)
- Compiles Python packages with C extensions (numpy, pandas, scikit-learn)
- Creates wheel files and compiled binaries
- This stage is DISCARDED after use!

Stage 2: Runtime

```dockerfile
FROM python:3.10-slim
# Purpose: Run the application


# **What happens here:**
# - Starts with a FRESH, clean base image
# - Copies ONLY the compiled packages from builder
# - Installs ONLY runtime dependencies
# - No build tools included
# - **This becomes your final image**


## 📊 Size Comparison Example

| Type | Size | Contains |
|------|------|----------|
| **Single-Stage** | 1.2 GB | App + Build tools + Runtime deps |
| **Multi-Stage** | 450 MB | App + Runtime deps only |
| **Savings** | **~60% smaller!** | ✅ |



## 🎯 Real-World Analogy

Imagine building a house:

### Single-Stage = Building + Living in Construction Site

🏗️ Construction tools (hammers, saws, cement mixers)
🏠 Your house
🛋️ Your furniture
👷 Construction workers still there

Everything stays forever, even after construction is done!

### Multi-Stage = Construction Site → Clean House

Stage 1 (Builder):
🏗️ Construction site with all tools
👷 Workers build the house
✅ House is completed

Stage 2 (Runtime):
🏠 Only the finished house is moved to final location
🛋️ Your furniture
❌ All construction tools left behind
❌ Workers go home
```

Only the finished product moves forward!

🔍 Step-by-Step: What Happens in Your Dockerfile
Builder Stage (Temporary):

```dockerfile
FROM python:3.10-slim AS builder
# Installs: gcc, g++, make (needed to compile packages)

RUN pip install -r requirements.txt
# Compiles packages like:
# - numpy (needs C compiler)
# - pandas (needs C++ compiler)
# - scikit-learn (needs gcc)
```

Result: Compiled .so files (Linux binaries) in /usr/local/lib/python3.10/site-packages

Runtime Stage (Final):

```dockerfile
FROM python:3.10-slim  # ← Fresh start, builder is gone!

# Copy ONLY the compiled packages
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

**Result:** You get the compiled packages WITHOUT the compilers!


## 💡 Key Benefits Breakdown

### 1. **Smaller Images**
Builder stage: 1.5 GB (with all build tools)
                ↓
Runtime stage: 450 MB (only essentials)


### 2. **Faster Deployments**
- Pulling 450 MB vs 1.2 GB from Docker registry
- Faster container startup
- Less bandwidth usage

### 3. **Better Security**
Single-stage: 200+ packages (including build tools)
Multi-stage: 80 packages (only runtime)

Fewer packages = fewer security vulnerabilities

### 4. **Cleaner Containers**

Single-stage: ps aux shows gcc, make processes
Multi-stage: Only your app processes
```

5. Layer Caching

```dockerfile
# Builder stage runs only when requirements.txt changes
# Runtime stage can use cached layers if app code changes


## 🛠️ When to Use Each Approach

### Use **Single-Stage** when:
- ✅ Quick prototyping/development
- ✅ No compiled dependencies
- ✅ Pure Python packages only
- ✅ Image size doesn't matter

### Use **Multi-Stage** when:
- ✅ Production deployments
- ✅ Packages with C/C++ extensions (numpy, pandas, pillow)
- ✅ Need smaller images
- ✅ Security is important
- ✅ Deploying to cloud (bandwidth costs)


## 📝 Visual Flow of Your Dockerfile

┌─────────────────────────────────────┐
│     STAGE 1: BUILDER                │
│  (python:3.10-slim + build tools)   │
├─────────────────────────────────────┤
│ 1. Install gcc, g++, make           │
│ 2. Copy requirements.txt            │
│ 3. pip install (compiles packages)  │
│ 4. Creates compiled binaries        │
└──────────────┬──────────────────────┘
               │
               │ COPY --from=builder
               │ (only compiled packages)
               ↓
┌─────────────────────────────────────┐
│     STAGE 2: RUNTIME                │
│     (fresh python:3.10-slim)        │
├─────────────────────────────────────┤
│ 1. Install only runtime deps       │
│ 2. Copy compiled packages           │
│ 3. Copy application code            │
│ 4. Configure & run app              │
└─────────────────────────────────────┘
               │
               ↓
        FINAL IMAGE (450 MB)
```

🎓 Summary

- Normal Dockerfile = Kitchen with all cooking equipment left out forever
- Multi-Stage = Kitchen after meal prep (only plates and food remain, all pots/pans put away)
- The multi-stage approach is the modern, production-ready way to build Docker images because it creates smaller, faster, and more secure containers by separating the build environment from the runtime environment.

## 📝 Detailed Commands for Docker

### **Building Images**

```bash
# Build all images
./scripts/build_images.sh

# Build with specific version
./scripts/build_images.sh v1.0.0

# Build individual image
docker build -t username/churn-prediction-api:latest -f docker/Dockerfile.api .
```

### **Running Containers**

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### **Managing Services**

```bash
# Check status
docker-compose ps

# Restart service
docker-compose restart api

# Scale service (if needed)
docker-compose up -d --scale api=3

# Execute command in container
docker-compose exec api bash
```

### **Using Helper Script**

```bash
# Start services
./scripts/run_docker.sh start

# Stop services
./scripts/run_docker.sh stop

# Restart services
./scripts/run_docker.sh restart

# View logs
./scripts/run_docker.sh logs

# View status
./scripts/run_docker.sh status

# Run training
./scripts/run_docker.sh train

# Cleanup
./scripts/run_docker.sh cleanup
```

---

---

---

## 🔧 Test Configuration

### **pytest.ini**

```ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    data: Data quality tests
    model: Model performance tests
    api: API tests
    slow: Slow tests
addopts = -v --strict-markers --cov-fail-under=70
```

### **.coveragerc**

```ini
[run]
source = src,api
omit = */tests/*, */venv/*

[report]
precision = 2
show_missing = True
```

---

## 🧩 Test Fixtures

Located in `tests/conftest.py`, available to all tests:

### **Configuration Fixtures**

- `test_config` - Test configuration
- `temp_dir` - Temporary directory

### **Data Fixtures**

- `sample_customer_data` - Single customer dict
- `sample_dataframe` - DataFrame with 5 customers
- `sample_csv_file` - Temporary CSV file

### **Model Fixtures**

- `mock_model` - Trained model mock
- `mock_preprocessor` - Preprocessor mock
- `prediction_pipeline_mock` - Complete pipeline mock

### **API Fixtures**

- `api_client` - FastAPI test client

### **Utility Fixtures**

- `mock_logger` - Suppress log output
- `mock_mlflow` - Mock MLflow tracking

---

## 🎨 Writing New Tests

### **Example Unit Test**

```python
import pytest

@pytest.mark.unit
def test_my_function(sample_dataframe):
    """Test my function works correctly."""
    result = my_function(sample_dataframe)
    assert result is not None
    assert len(result) > 0
```

### **Example Integration Test**

```python
@pytest.mark.integration
@pytest.mark.api
def test_api_endpoint(api_client):
    """Test API endpoint."""
    response = api_client.get("/health")
    assert response.status_code == 200
```

### **Example Parametrized Test**

```python
@pytest.mark.parametrize("input,expected", [
    (0.1, 'Low'),
    (0.5, 'High'),
    (0.8, 'Critical'),
])
def test_risk_levels(input, expected):
    """Test risk level calculation."""
    assert calculate_risk(input) == expected
```

---

## 🔍 Debugging Tests

### **Run with Debug Info**

```bash
pytest -vv --tb=long
```

### **Show Print Statements**

```bash
pytest -s
```

### **Drop into Debugger on Failure**

```bash
pytest --pdb
```

### **Show Fixtures**

```bash
pytest --fixtures
```

### **Collect Tests Without Running**

```bash
pytest --collect-only
```

---

## 🚀 CI/CD Integration

### **GitHub Actions Example**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov=api --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

---

---

---

## <h1 align=center>Deploy to AWS</h1>

`Guide you through deploying a Docker image from Docker Hub to AWS ECS using ECR, Fargate, and GitHub Actions.`

## The process involves:

- Setting up AWS infrastructure (ECR, ECS cluster, task definition, service)
- Configuring AWS credentials in GitHub
- Creating a GitHub Actions workflow to automate deployment

### Step 1: Set up AWS ECR Repository

- First, create an ECR repository to store your Docker images:

```bash
aws ecr create-repository --repository-name your-app-name --region us-east-1
```

`Note` the repository URI (you'll need this later): <account-id>.dkr.ecr.us-east-1.amazonaws.com/your-app-name

### Step 2: Create ECS Cluster

- Create an ECS cluster that will run your containers:

```bash
aws ecs create-cluster --cluster-name your-cluster-name --region us-east-1
```

### Step 3: Create Task Execution Role

- Create an IAM role for ECS task execution:

```
Go to IAM Console → Roles → Create Role
Select "Elastic Container Service" → "Elastic Container Service Task"
Attach the policy: AmazonECSTaskExecutionRolePolicy
Name it: ecsTaskExecutionRole
```

`Note` the role ARN for later use.

### Step 4: Create ECS Task Definition

- Create a file task-definition.json:

```json
{
  "family": "your-app-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "your-app-container",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/your-app-name:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/your-app-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

- Create CloudWatch log group:

```bash
aws logs create-log-group --log-group-name /ecs/your-app-task --region us-east-1
```

- Register the task definition:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

```bash
# In My PC
aws ecs register-task-definition --cli-input-json file://C:\Users\44787\Desktop\Chunk_Prediction-MLOps-\.github\workflows\task_defination1.json
```

### Step 5: Create ECS Service

- First, you'll need a VPC with subnets and a security group. If you don't have them:

```bash
# Get your default VPC and subnets
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"
aws ec2 describe-subnets --filters "Name=vpc-id,Values=<your-vpc-id>" # i created on aws

# Create security group
aws ec2 create-security-group \
  --group-name ecs-service-sg \
  --description "Security group for ECS service" \
  --vpc-id <your-vpc-id>

# Allow inbound traffic on port 80
aws ec2 authorize-security-group-ingress \
  --group-id <security-group-id> \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

- Create the ECS service:

```bash
aws ecs create-service \
  --cluster your-cluster-name \
  --service-name your-service-name \
  --task-definition your-app-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Step 6: Configure AWS Credentials in GitHub

- Create an IAM user with programmatic access
- Attach these policies:

```
AmazonEC2ContainerRegistryPowerUser
AmazonECS_FullAccess
```

- Save the Access Key ID and Secret Access Key

- In your GitHub repository:

```
Go to Settings → Secrets and variables → Actions
```

- Add these secrets:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### Step 7: Create GitHub Actions Workflow

- Create .github/workflows/deploy.yml:

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches:
      - main

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: your-app-name
  ECS_SERVICE: your-service-name
  ECS_CLUSTER: your-cluster-name
  ECS_TASK_DEFINITION: task-definition.json
  CONTAINER_NAME: your-app-container

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Pull image from Docker Hub
        run: |
          docker pull your-dockerhub-username/your-image:latest

      - name: Tag and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker tag your-dockerhub-username/your-image:latest $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag your-dockerhub-username/your-image:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Download task definition
        run: |
          aws ecs describe-task-definition --task-definition your-app-task --query taskDefinition > task-definition.json

      - name: Fill in the new image ID in the Amazon ECS task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ${{ env.ECS_TASK_DEFINITION }}
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}

      - name: Deploy Amazon ECS task definition
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```

### Step 8: Commit and Deploy

- Add the task-definition.json file to your repository root
- Update all placeholder values in the workflow file
- Commit and push to the main branch

```bash
git add .github/workflows/deploy.yml task-definition.json
git commit -m "Add ECS deployment workflow"
git push origin main
```

#### Workflow Explanation

The GitHub Actions workflow does the following:

- Checks out your code
- Configures AWS credentials
- Logs into Amazon ECR
- Pulls your image from Docker Hub
- Tags and pushes it to ECR
- Updates the ECS task definition with the new image
- Deploys the updated task definition to your ECS service

#### Verification

- After deployment, check your service:

```bash
aws ecs describe-services --cluster your-cluster-name --services your-service-name
```

- Get the public IP of your running task:

```bash
aws ecs list-tasks --cluster your-cluster-name --service-name your-service-name
aws ecs describe-tasks --cluster your-cluster-name --tasks <task-arn>
```

`Open the app:`

```
ECS cluster -> ECS services -> click on Tasks -> Click on Public ID -> add 8000 ---> the app will be running...
```

---

---

---

<h1 aling=center>Running Kubernetes Locally & Deploying to AWS EKS </h1>

`Guide you through running your churn prediction application locally, then setting up AWS deployment with CI/CD.`

## Part 1: Running Locally
#### Prerequisites
- Install these tools first:
##### Option A: Minikube (Recommended for beginners)
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (with Chocolatey)
choco install minikube
```
##### Option B: Kind (Kubernetes in Docker)
```bash
# macOS/Linux
brew install kind
# or
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
##### Option C: Docker Desktop (Easiest if you have it)

- Enable Kubernetes in Docker Desktop settings

- Also install kubectl:
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Step-by-Step Local Deployment
1. Start your local Kubernetes cluster
```bash
# If using Minikube
minikube start --memory=4096 --cpus=2

# If using Kind
kind create cluster --name churn-prediction

# If using Docker Desktop - just ensure Kubernetes is enabled
```

2. Verify cluster is running
```bash
kubectl cluster-info
kubectl get nodes
```
3. Apply your Kubernetes manifests
```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy API
kubectl apply -f api.yaml

# Deploy Streamlit frontend
kubectl apply -f streamlit.yaml
```
4. Check deployment status

```bash
# Watch pods starting up
kubectl get pods -n churn-prediction -w

# Check services
kubectl get svc -n churn-prediction

# Check deployment details
kubectl get deployments -n churn-prediction
```
5. Access your applications locally
- Since you're using LoadBalancer services locally, you need to expose them:
For Minikube:
```bash
# In separate terminal windows, run:
minikube tunnel

# Then get the external IPs
kubectl get svc -n churn-prediction
```
- For Kind or Docker Desktop:

```bash
# Port forward the services instead
kubectl port-forward -n churn-prediction svc/streamlit-service 8501:80
kubectl port-forward -n churn-prediction svc/api-service 8000:80
```
6. Access your app

```
Streamlit UI: http://localhost:8501
API: http://localhost:8000
API Health: http://localhost:8000/health
```
- Troubleshooting Local Setup

```bash
# View pod logs
kubectl logs -n churn-prediction -l app=api
kubectl logs -n churn-prediction -l app=streamlit

# Describe pod for issues
kubectl describe pod -n churn-prediction <pod-name>

# Restart deployment
kubectl rollout restart deployment/api -n churn-prediction
kubectl rollout restart deployment/streamlit -n churn-prediction

# Delete and reapply
kubectl delete -f api.yaml
kubectl apply -f api.yaml
```

## Part 2: AWS(EKS) Deployment with CI/CD
🏗️ Architecture
```
┌─────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │         churn-prediction namespace           │   │
│  │                                              │   │
│  │  ┌────────────────┐    ┌─────────────────┐   │   │
│  │  │  API Service   │    │ Streamlit App   │   │   │
│  │  │  (2 replicas)  │◄───┤  (2 replicas)   │   │   │
│  │  │                │    │                 │   │   │
│  │  │  Port: 8000    │    │   Port: 8501    │   │   │
│  │  └────────┬───────┘    └────────┬────────┘   │   │
│  │           │                      │           │   │
│  │  ┌────────▼───────┐    ┌────────▼────────┐   │   │
│  │  │ LoadBalancer   │    │  LoadBalancer   │   │   │
│  │  │  (AWS NLB)     │    │   (AWS NLB)     │   │   │
│  │  └────────────────┘    └─────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                       │
            ┌──────────▼──────────┐
            │   Docker Hub        │
            │                     │
            │  - API Image        │
            │  - Streamlit Image  │
            └─────────────────────┘
```
📦 Components
API Service: FastAPI backend for churn prediction
Streamlit App: Interactive web interface
Docker Hub: Container image registry
AWS EKS: Managed Kubernetes service
GitHub Actions: CI/CD automation

📁 Repository Structure
```
.
├── .github/
│   └── workflows/
│       └── eks_deploy.yml      # GitHub Actions CI/CD pipeline
├── k8s/
│   ├── namespace.yaml          # Kubernetes namespace
│   ├── api.yaml                # API deployment and service
│   └── streamlit.yaml          # Streamlit deployment and service
├── eks-cluster.yaml            # EKS cluster configuration
├── k8s/
│   ├── eks_deploy.sh           # Manual deployment script
└── README.md                   # This file
```
#### AWS EKS Deployment
##### Prerequisites
 - AWS Account
 - AWS CLI configured
 - kubectl installed
 - eksctl installed

1. Create EKS Cluster
```bash
eksctl create cluster -f eks-cluster.yaml
```
2. Deploy Application
- Option A: Using GitHub Actions (Automated)
```bash
#1. Fork this repository
#2. Add GitHub Secrets (see Configuration section)
#3. Push to main branch
#4. GitHub Actions will automatically deploy
```
- Option B: Using Deploy Script (Manual)
```bash
chmod +x deploy.sh
./deploy.sh
```
- Option C: Using kubectl (Manual)
```bash
aws eks update-kubeconfig --name churn-prediction-cluster --region us-east-1
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/streamlit.yaml
```
