#!/bin/bash
# Deployment script for Sequential Search API

set -e

echo "="*60
echo "Deploying Sequential Search API to AWS Lambda"
echo "="*60
echo ""

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="linkedin-sequential-api"
LAMBDA_FUNCTION_NAME="linkedin-sequential-search"
IMAGE_TAG="latest"

echo "Configuration:"
echo "  Region: $AWS_REGION"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  ECR Repo: $ECR_REPO_NAME"
echo "  Lambda: $LAMBDA_FUNCTION_NAME"
echo ""

# Step 1: Create ECR repository if doesn't exist
echo "Step 1: Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION 2>/dev/null || echo "Repository already exists"

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
echo "ECR URI: $ECR_URI"
echo ""

# Step 2: Build Docker image
echo "Step 2: Building Docker image..."
cd "$(dirname "$0")/.."
docker build -t $ECR_REPO_NAME:$IMAGE_TAG -f deployment/Dockerfile .
echo "✅ Image built"
echo ""

# Step 3: Login to ECR
echo "Step 3: Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI
echo "✅ Logged in"
echo ""

# Step 4: Tag and push image
echo "Step 4: Pushing image to ECR..."
docker tag $ECR_REPO_NAME:$IMAGE_TAG $ECR_URI:$IMAGE_TAG
docker push $ECR_URI:$IMAGE_TAG
echo "✅ Image pushed"
echo ""

# Step 5: Create or update Lambda function
echo "Step 5: Creating/updating Lambda function..."

# Check if function exists
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --image-uri $ECR_URI:$IMAGE_TAG \
        --region $AWS_REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$ECR_URI:$IMAGE_TAG \
        --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-opensearch-role \
        --timeout 29 \
        --memory-size 1024 \
        --region $AWS_REGION \
        --environment Variables="{
            OPENSEARCH_ENDPOINT=il674y001legt8k99rt0.us-east-1.aoss.amazonaws.com,
            AWS_REGION=us-east-1,
            COMPANIES_INDEX=linkedin-prod-companies,
            PROFILES_INDEX=linkedin_profiles_enriched_*
        }"
fi

echo "✅ Lambda function deployed"
echo ""

# Step 6: Create Function URL (for testing)
echo "Step 6: Creating Function URL..."
FUNCTION_URL=$(aws lambda create-function-url-config \
    --function-name $LAMBDA_FUNCTION_NAME \
    --auth-type AWS_IAM \
    --region $AWS_REGION \
    --query 'FunctionUrl' \
    --output text 2>/dev/null || aws lambda get-function-url-config \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $AWS_REGION \
    --query 'FunctionUrl' \
    --output text)

echo "Function URL: $FUNCTION_URL"
echo ""

echo "="*60
echo "✅ DEPLOYMENT COMPLETE"
echo "="*60
echo ""
echo "Next steps:"
echo "  1. Test Lambda function directly"
echo "  2. Configure API Gateway"
echo "  3. Add rate limiting and API keys"
echo "  4. Production testing"
echo ""
echo "Function URL: $FUNCTION_URL"
