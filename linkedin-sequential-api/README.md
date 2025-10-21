# LinkedIn Sequential Search API

Sequential search API that filters companies first, then finds people working at those companies.

## Features

✅ **Two-stage search:** Companies → People
✅ **54M companies** + **826M profiles**
✅ **Sub-500ms queries**
✅ **VPC endpoint access**
✅ **AWS Lambda ready**

## Example Query

**Find Engineers in SF at mid-sized tech companies founded after 2010:**

```python
POST /v1/search/sequential
{
  "company_criteria": {
    "industry": ["Technology"],
    "size": ["11_50", "51_200"],
    "founded_after": 2010,
    "location_contains": "San Francisco"
  },
  "people_criteria": {
    "job_title": "Engineer",
    "location": "San Francisco",
    "seniority": ["senior", "mid_level"]
  },
  "page": 1,
  "page_size": 25
}
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "fullName": "John Smith",
      "headline": "Senior Software Engineer",
      "current_company_extracted": "Stripe",
      "locationName": "San Francisco",
      "seniority_level": "senior"
    }
  ],
  "metadata": {
    "companies_matched": 547,
    "profiles_matched": 8234,
    "query_time_ms": 387,
    "page": 1,
    "total_pages": 330
  }
}
```

## Quick Start

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run test
python test_api.py

# Run local server
python -m app.main
# Access: http://localhost:8000/docs
```

### Test with curl

```bash
curl -X POST http://localhost:8000/v1/search/sequential \
  -H "Content-Type: application/json" \
  -d '{
    "company_criteria": {
      "industry": ["Technology"],
      "size": ["11_50"]
    },
    "people_criteria": {
      "job_title": "Engineer",
      "location": "San Francisco"
    }
  }'
```

## API Endpoints

### POST /v1/search/sequential
Sequential company → people search

### GET /health
Health check and OpenSearch connectivity

### GET /
API info and available endpoints

### GET /docs
Interactive API documentation (Swagger UI)

## Architecture

```
1. Query linkedin-prod-companies (54M companies)
   ↓
2. Extract company names (limit 1000)
   ↓
3. Query linkedin_profiles_enriched_* (826M profiles)
   Filter: current_company_extracted IN [company_names]
   ↓
4. Return matching profiles
```

## Configuration

**Environment Variables:**
- `OPENSEARCH_ENDPOINT`: OpenSearch endpoint
- `AWS_REGION`: AWS region
- `COMPANIES_INDEX`: Company index name
- `PROFILES_INDEX`: Profiles index pattern
- `MAX_COMPANIES_FILTER`: Max companies to use in filter (default: 1000)

## Performance

**Expected:**
- Company query: 100-150ms
- People query: 200-350ms
- Total: <500ms (p95)

**Optimizations:**
- Connection pooling (singleton pattern)
- Only fetch needed fields
- Filter clauses (not scored)
- Async/await for I/O

## Deployment

### AWS Lambda Deployment

See `deployment/` folder for:
- Dockerfile (Lambda container)
- Serverless configuration
- Deployment instructions

**Requirements:**
- Lambda in same VPC as OpenSearch
- VPC endpoint access configured
- IAM role with OpenSearch permissions

## Project Structure

```
linkedin-sequential-api/
├── app/
│   ├── main.py                   # FastAPI app
│   ├── config.py                 # Settings
│   ├── models/                   # Request/Response models
│   ├── services/                 # Business logic
│   │   ├── opensearch_client.py # Client singleton
│   │   ├── company_service.py   # Company queries
│   │   ├── people_service.py    # People queries
│   │   └── sequential_service.py # Orchestration
│   └── utils/                    # Utilities
├── deployment/                   # Lambda deployment
├── tests/                        # Tests
├── test_api.py                   # Quick test script
└── requirements.txt
```

## Development

Built following AWS best practices 2025:
- OpenSearch multi-index queries
- FastAPI async/await patterns
- Lambda VPC deployment
- Connection pooling for performance

## Success Criteria

✅ Query time: <500ms
✅ Handles up to 1000 companies in filter
✅ Accurate sequential filtering
✅ Works with 54M companies + 826M profiles
✅ Production-ready error handling

---

**Created:** October 19, 2025
**Status:** Ready for testing and deployment
