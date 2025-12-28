#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EKS_CLUSTER_NAME="churn-prediction-cluster"
AWS_REGION="us-east-1"
NAMESPACE="churn-prediction"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Churn Prediction EKS Deployment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

command -v kubectl >/dev/null 2>&1 || {
    echo -e "${RED}kubectl is required but not installed. Aborting.${NC}" >&2
    exit 1
}

command -v aws >/dev/null 2>&1 || {
    echo -e "${RED}aws CLI is required but not installed. Aborting.${NC}" >&2
    exit 1
}

echo -e "${GREEN}✓ Prerequisites check passed${NC}\n"

# Update kubeconfig
echo -e "${YELLOW}Updating kubeconfig for EKS cluster...${NC}"
aws eks update-kubeconfig --name $EKS_CLUSTER_NAME --region $AWS_REGION

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to update kubeconfig. Please check:${NC}"
    echo -e "${RED}1. AWS credentials are configured${NC}"
    echo -e "${RED}2. EKS cluster exists${NC}"
    echo -e "${RED}3. You have proper IAM permissions${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kubeconfig updated${NC}\n"

# Verify cluster connection
echo -e "${YELLOW}Verifying cluster connection...${NC}"
kubectl cluster-info >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Cannot connect to cluster. Aborting.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Connected to cluster${NC}\n"

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✓ Namespace ready${NC}\n"

# Deploy API
echo -e "${YELLOW}Deploying API service...${NC}"
kubectl apply -f k8s/api.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to deploy API${NC}"
    exit 1
fi

echo -e "${GREEN}✓ API deployed${NC}\n"

# Deploy Streamlit
echo -e "${YELLOW}Deploying Streamlit service...${NC}"
kubectl apply -f k8s/streamlit.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to deploy Streamlit${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Streamlit deployed${NC}\n"

# Wait for deployments
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
echo -e "${BLUE}This may take 2-3 minutes...${NC}\n"

kubectl rollout status deployment/api -n $NAMESPACE --timeout=5m
kubectl rollout status deployment/streamlit -n $NAMESPACE --timeout=5m

echo -e "${GREEN}✓ All deployments ready${NC}\n"

# Show deployment status
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE -o wide

echo -e "\n${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

# Get LoadBalancer URLs
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Getting LoadBalancer URLs${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Waiting for LoadBalancers to be provisioned (this may take 2-3 minutes)...${NC}"
sleep 30

API_LB=""
STREAMLIT_LB=""

# Try to get LoadBalancer URLs with timeout
for i in {1..20}; do
    API_LB=$(kubectl get svc api-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
    STREAMLIT_LB=$(kubectl get svc streamlit-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)

    if [ ! -z "$API_LB" ] && [ ! -z "$STREAMLIT_LB" ]; then
        break
    fi

    echo -e "${YELLOW}Attempt $i/20: Waiting for LoadBalancers...${NC}"
    sleep 10
done

# Display results
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  Access URLs${NC}"
echo -e "${BLUE}========================================${NC}\n"

if [ ! -z "$API_LB" ]; then
    echo -e "${GREEN}API Service:${NC}"
    echo -e "  URL: ${BLUE}http://$API_LB${NC}"
    echo -e "  Health: ${BLUE}http://$API_LB/health${NC}\n"
else
    echo -e "${YELLOW}API LoadBalancer URL not ready yet. Run this command to check:${NC}"
    echo -e "  kubectl get svc api-service -n $NAMESPACE\n"
fi

if [ ! -z "$STREAMLIT_LB" ]; then
    echo -e "${GREEN}Streamlit Service:${NC}"
    echo -e "  URL: ${BLUE}http://$STREAMLIT_LB${NC}\n"
else
    echo -e "${YELLOW}Streamlit LoadBalancer URL not ready yet. Run this command to check:${NC}"
    echo -e "  kubectl get svc streamlit-service -n $NAMESPACE\n"
fi

# Test API health
if [ ! -z "$API_LB" ]; then
    echo -e "${YELLOW}Testing API health endpoint...${NC}"
    for i in {1..10}; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$API_LB/health 2>/dev/null)
        if [ "$HTTP_CODE" == "200" ]; then
            echo -e "${GREEN}✓ API is healthy!${NC}"
            curl -s http://$API_LB/health | jq . 2>/dev/null || curl -s http://$API_LB/health
            break
        else
            echo -e "${YELLOW}Attempt $i/10: API not ready (HTTP $HTTP_CODE), waiting...${NC}"
            sleep 10
        fi
    done
    echo ""
fi

# Useful commands
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Useful Commands${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}View logs:${NC}"
echo -e "  kubectl logs -f -n $NAMESPACE -l app=api"
echo -e "  kubectl logs -f -n $NAMESPACE -l app=streamlit\n"

echo -e "${YELLOW}Check status:${NC}"
echo -e "  kubectl get all -n $NAMESPACE\n"

echo -e "${YELLOW}Restart deployments:${NC}"
echo -e "  kubectl rollout restart deployment/api -n $NAMESPACE"
echo -e "  kubectl rollout restart deployment/streamlit -n $NAMESPACE\n"

echo -e "${YELLOW}Get URLs again:${NC}"
echo -e "  kubectl get svc -n $NAMESPACE\n"

echo -e "${YELLOW}Delete deployment:${NC}"
echo -e "  kubectl delete namespace $NAMESPACE\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete! 🚀${NC}"
echo -e "${GREEN}========================================${NC}\n"
