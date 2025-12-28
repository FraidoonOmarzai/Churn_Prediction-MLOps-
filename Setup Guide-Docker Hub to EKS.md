# Complete Setup Guide: Docker Hub Images → EKS via GitHub Actions

## Prerequisites Checklist

- [ ] AWS Account with billing enabled
- [ ] GitHub repository with your code
- [ ] Docker Hub account with your images pushed
- [ ] AWS CLI installed locally
- [ ] kubectl installed locally
- [ ] eksctl installed locally

---

## Step 1: Prepare Your Docker Hub Images

### If you haven't pushed images yet:

```bash
# Login to Docker Hub
docker login

# Build and tag your images
docker build -t fraidoonjan/churn-prediction-api:latest ./api
docker build -t fraidoonjan/churn-prediction-streamlit:latest ./streamlit

# Push to Docker Hub
docker push fraidoonjan/churn-prediction-api:latest
docker push fraidoonjan/churn-prediction-streamlit:latest

# Verify images are on Docker Hub
# Visit: https://hub.docker.com/u/fraidoonjan
```

### For Private Docker Hub Images (Optional):

If your images are private, you'll need to create a Docker Hub access token:

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name it (e.g., "github-actions")
4. Save the token - you'll need it for GitHub secrets

---

## Step 2: Setup AWS Infrastructure

### A. Create EKS Cluster

```bash
# Create eks-cluster.yaml file (see artifacts above)
# Then run:
eksctl create cluster -f eks-cluster.yaml

# This takes 15-20 minutes
# Wait for completion...
```

### B. Verify Cluster

```bash
# Check cluster is running
eksctl get cluster --region us-east-1

# Verify nodes
kubectl get nodes

# Should show 2 nodes in Ready state
```

---

## Step 3: Setup AWS IAM for GitHub Actions

### Create IAM User with Required Permissions

```bash
# Create IAM user
aws iam create-user --user-name github-actions-eks-deploy

# Create policy document
cat > github-actions-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create and attach policy
aws iam create-policy \
    --policy-name GitHubActionsEKSDeploy \
    --policy-document file://github-actions-policy.json

# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Attach policy to user
aws iam attach-user-policy \
    --user-name github-actions-eks-deploy \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/GitHubActionsEKSDeploy

# Create access keys
aws iam create-access-key --user-name github-actions-eks-deploy

# IMPORTANT: Save the AccessKeyId and SecretAccessKey output!
```

### Add User to EKS Cluster

```bash
# Edit aws-auth ConfigMap
kubectl edit configmap aws-auth -n kube-system

# Add this to the mapUsers section:
# - userarn: arn:aws:iam::YOUR_ACCOUNT_ID:user/github-actions-eks-deploy
#   username: github-actions
#   groups:
#     - system:masters
```

Or use this command:

```bash
eksctl create iamidentitymapping \
  --cluster churn-prediction-cluster \
  --region us-east-1 \
  --arn arn:aws:iam::YOUR_ACCOUNT_ID:user/github-actions-eks-deploy \
  --username github-actions \
  --group system:masters
```

---

## Step 4: Configure GitHub Repository

### A. Add GitHub Secrets

Go to: **Your Repository → Settings → Secrets and variables → Actions**

Click **"New repository secret"** and add:

| Secret Name             | Value                 | Description                  |
| ----------------------- | --------------------- | ---------------------------- |
| `AWS_ACCESS_KEY_ID`     | Your AWS Access Key   | From IAM user creation       |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Key   | From IAM user creation       |
| `DOCKER_HUB_USERNAME`   | fraidoonjan           | Your Docker Hub username     |
| `DOCKER_HUB_TOKEN`      | Your Docker Hub token | Only if using private images |

### B. Repository Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions workflow
├── k8s/
│   ├── namespace.yaml
│   ├── api.yaml
│   └── streamlit.yaml
├── eks-cluster.yaml            # EKS cluster config
└── README.md
```

### C. Create Workflow File

Create `.github/workflows/deploy.yml` with the content from the first artifact above.

---

## Step 5: Update Kubernetes Manifests

Replace your existing manifests with the ones in the second artifact above, or make these changes:

### Key Changes:

1. **imagePullPolicy: Always** - Ensures latest image is pulled
2. **imagePullSecrets** - Uncomment if using private Docker Hub images
3. **AWS LoadBalancer annotations** - For proper AWS integration

---

## Step 6: Deploy!

### Initial Deployment (Manual)

```bash
# Apply manifests directly first time
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/streamlit.yaml

# Check deployment
kubectl get pods -n churn-prediction
kubectl get svc -n churn-prediction
```

### Automated Deployment via GitHub Actions

```bash
# Commit and push your code
git add .
git commit -m "Add CI/CD pipeline for EKS deployment"
git push origin main

# GitHub Actions will automatically:
# 1. Connect to your EKS cluster
# 2. Deploy/update your applications
# 3. Show you the LoadBalancer URLs
```

---

## Step 7: Monitor Deployment

### In GitHub:

1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. Watch the deployment progress
4. Check the summary for URLs

### From Command Line:

```bash
# Watch pods starting
kubectl get pods -n churn-prediction -w

# Check logs
kubectl logs -f -n churn-prediction -l app=api
kubectl logs -f -n churn-prediction -l app=streamlit

# Get services
kubectl get svc -n churn-prediction

# Describe service to see events
kubectl describe svc api-service -n churn-prediction
```

---

## Step 8: Access Your Application

### Get LoadBalancer URLs:

```bash
# Wait 2-3 minutes for LoadBalancers to provision
kubectl get svc -n churn-prediction

# You'll see output like:
# NAME                TYPE           EXTERNAL-IP
# api-service         LoadBalancer   a1b2c3d4-xxx.elb.us-east-1.amazonaws.com
# streamlit-service   LoadBalancer   e5f6g7h8-xxx.elb.us-east-1.amazonaws.com
```

### Access URLs:

- **API**: `http://<api-loadbalancer-url>`
- **API Health**: `http://<api-loadbalancer-url>/health`
- **Streamlit**: `http://<streamlit-loadbalancer-url>`

---

## Updating Your Application

### When you update Docker Hub images:

```bash
# 1. Build and push new images to Docker Hub
docker build -t fraidoonjan/churn-prediction-api:latest ./api
docker push fraidoonjan/churn-prediction-api:latest

# 2. Two options to deploy:

# Option A: Let GitHub Actions handle it (recommended)
git commit -m "Update application" --allow-empty
git push origin main

# Option B: Manual restart
kubectl rollout restart deployment/api -n churn-prediction
kubectl rollout restart deployment/streamlit -n churn-prediction
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n churn-prediction

# Describe pod for errors
kubectl describe pod <pod-name> -n churn-prediction

# Check logs
kubectl logs <pod-name> -n churn-prediction

# Common issues:
# - Image pull errors: Check image name and Docker Hub access
# - Health check failures: Check /health endpoint in your app
# - Resource issues: Check if nodes have enough resources
```

### LoadBalancer Pending

```bash
# Check service
kubectl describe svc api-service -n churn-prediction

# Common issues:
# - AWS service quotas
# - VPC/subnet configuration
# - Security group rules

# Wait up to 5 minutes for AWS to provision
```

### GitHub Actions Failing

```bash
# Check workflow logs in GitHub Actions tab

# Common issues:
# - AWS credentials incorrect
# - EKS cluster name mismatch
# - IAM permissions missing
# - kubectl not finding cluster

# Test AWS access locally:
aws eks describe-cluster --name churn-prediction-cluster --region us-east-1
```

### Can't Pull Docker Hub Images

```bash
# For public images: should work automatically

# For private images:
# 1. Verify secret exists
kubectl get secret dockerhub-secret -n churn-prediction

# 2. Recreate secret
kubectl delete secret dockerhub-secret -n churn-prediction
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=churn-prediction

# 3. Uncomment imagePullSecrets in your manifests
```

---

## Cost Management

### Monitor Costs

```bash
# Check running resources
kubectl get nodes
kubectl get pods --all-namespaces

# EKS cluster costs approximately:
# - Control plane: ~$0.10/hour ($73/month)
# - 2x t3.medium nodes: ~$0.0832/hour each (~$120/month total)
# - LoadBalancers: ~$0.025/hour each (~$36/month total)
# Total: ~$230/month
```

### Stop/Start Cluster

```bash
# Scale down (save node costs, keep cluster)
kubectl scale deployment --all --replicas=0 -n churn-prediction
eksctl scale nodegroup --cluster=churn-prediction-cluster --nodes=0 --name=churn-prediction-nodes

# Scale back up
eksctl scale nodegroup --cluster=churn-prediction-cluster --nodes=2 --name=churn-prediction-nodes
kubectl scale deployment --all --replicas=2 -n churn-prediction
```

### Delete Everything

```bash
# Delete cluster (to stop all charges)
eksctl delete cluster --name churn-prediction-cluster --region us-east-1

# This will delete:
# - EKS cluster
# - All nodes
# - All deployments
# - LoadBalancers
# - Associated AWS resources
```

---

## Next Steps

1. **Add SSL/TLS**: Use cert-manager for HTTPS
2. **Custom Domain**: Route53 + ALB Ingress
3. **Monitoring**: Install Prometheus + Grafana
4. **Logging**: Setup CloudWatch or ELK stack
5. **Secrets Management**: Use AWS Secrets Manager
6. **Auto-scaling**: Configure HPA and cluster autoscaler
7. **Multiple Environments**: Setup dev/staging/prod

---

## Quick Reference Commands

```bash
# Check everything
kubectl get all -n churn-prediction

# Get URLs
kubectl get svc -n churn-prediction -o wide

# View logs
kubectl logs -f -n churn-prediction -l app=api

# Restart deployment
kubectl rollout restart deployment/api -n churn-prediction

# Check rollout status
kubectl rollout status deployment/api -n churn-prediction

# Access pod shell
kubectl exec -it <pod-name> -n churn-prediction -- /bin/bash

# Port forward (for testing)
kubectl port-forward -n churn-prediction svc/api-service 8000:80
```

---

## Support

If you encounter issues:

1. Check GitHub Actions logs
2. Check kubectl logs: `kubectl logs -n churn-prediction -l app=api`
3. Check AWS CloudWatch logs
4. Verify IAM permissions
5. Ensure EKS cluster version compatibility

Happy deploying! 🚀
