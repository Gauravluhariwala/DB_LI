# Production Dockerfile for AWS Lambda
# Optimized for FastAPI with OpenSearch and Chroma Cloud

FROM public.ecr.aws/lambda/python:3.11

# Install build dependencies for chromadb (numpy, etc.)
RUN yum install -y gcc gcc-c++ make

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# CRITICAL: Set cache directories to /tmp for Lambda (read-only filesystem)
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/transformers
ENV XDG_CACHE_HOME=/tmp/cache
ENV HOME=/tmp

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Set Lambda handler
CMD ["app.main.handler"]
