# Deployment Information

## Current Production Deployment

**Status:** 🟢 LIVE
**Last Deployed:** October 19, 2025

### AWS Lambda
- **Function Name:** linkedin-sequential-api
- **Region:** us-east-1
- **Runtime:** Docker container (Python 3.11)
- **Memory:** 1024 MB
- **Timeout:** 29 seconds
- **IAM Role:** lambda-sequential-search-role

### Endpoint
```
POST https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential
```

### ECR Image
```
715841330409.dkr.ecr.us-east-1.amazonaws.com/linkedin-sequential-api:final
```

### OpenSearch
- **Endpoint:** il674y001legt8k99rt0.us-east-1.aoss.amazonaws.com
- **Collection:** linkedin-prod
- **Network Policy:** Public access enabled
- **Data Access:** IAM-based (lambda-sequential-search-role has access)

### IAM Permissions Required
Lambda role needs:
- `aoss:APIAccessAll`
- `aoss:BatchGetCollection`
- CloudWatch Logs permissions

The role ARN must be added to OpenSearch data access policy:
- Policy name: linkedin-prod-access
- Type: data
- Principal: arn:aws:iam::715841330409:role/lambda-sequential-search-role

---

## Redeployment Instructions

See deployment/README.md for complete deployment guide.

Quick redeploy:
```bash
cd deployment
./deploy.sh
```

---

## Monitoring

**CloudWatch Logs:**
```bash
aws logs tail /aws/lambda/linkedin-sequential-api --follow
```

**Function Status:**
```bash
aws lambda get-function --function-name linkedin-sequential-api --region us-east-1
```

---

## Cost

**Current monthly cost:**
- Lambda: $0-20 (based on usage, first 1M requests free)
- OpenSearch: ~$1,000 (for 54M companies + 826M profiles)

**Total:** ~$1,000-1,020/month
