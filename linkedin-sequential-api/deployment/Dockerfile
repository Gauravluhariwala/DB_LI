# Production Dockerfile for AWS Lambda
# Optimized for FastAPI with OpenSearch

FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Set Lambda handler
CMD ["app.main.handler"]
