# Deployment Guide - Sequential Search API

## Prerequisites

1. AWS CLI configured
2. Docker installed
3. IAM role for Lambda with OpenSearch permissions

## Quick Deploy

```bash
cd /Users/gauravluhariwala/linkedin-sequential-api/deployment
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment Steps

### 1. Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name linkedin-sequential-api \
    --region us-east-1
```

### 2. Build Docker Image

```bash
cd /Users/gauravluhariwala/linkedin-sequential-api
docker build -t linkedin-sequential-api -f deployment/Dockerfile .
```

### 3. Push to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

docker tag linkedin-sequential-api <ECR_URI>:latest
docker push <ECR_URI>:latest
```

### 4. Create Lambda Function

```bash
aws lambda create-function \
    --function-name linkedin-sequential-search \
    --package-type Image \
    --code ImageUri=<ECR_URI>:latest \
    --role arn:aws:iam::<ACCOUNT_ID>:role/lambda-opensearch-role \
    --timeout 29 \
    --memory-size 1024 \
    --environment Variables="{
        OPENSEARCH_ENDPOINT=il674y001legt8k99rt0.us-east-1.aoss.amazonaws.com
    }"
```

### 5. Configure API Gateway

```bash
# Create HTTP API
aws apigatewayv2 create-api \
    --name linkedin-sequential-api \
    --protocol-type HTTP \
    --target arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:linkedin-sequential-search
```

## IAM Role Requirements

Lambda needs:
- `aoss:APIAccessAll`
- `aoss:BatchGetCollection`
- CloudWatch Logs permissions

## Testing

```bash
# Local test
python3 test_api.py

# Lambda test
aws lambda invoke \
    --function-name linkedin-sequential-search \
    --payload file://test_payload.json \
    response.json
```

## Monitoring

- CloudWatch Logs: `/aws/lambda/linkedin-sequential-search`
- Metrics: Invocations, Duration, Errors
- X-Ray: Enable for distributed tracing

## Cost Estimate

- Lambda: ~$10/month (10K requests)
- API Gateway: ~$3.50 per 1M requests
- OpenSearch: $1,000/month (existing)

Total: ~$1,013/month
