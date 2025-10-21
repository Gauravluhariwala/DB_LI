"""
LinkedIn Sequential Search API
FastAPI application for company → people sequential queries
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import time

from app.models.request import SequentialSearchRequest
from app.models.response import SequentialSearchResponse
from app.services import sequential_service_optimized as sequential_service
from app.config import settings

# Initialize FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Sequential search API: Query companies first, then find people at those companies"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "api": settings.api_title,
        "version": settings.api_version,
        "status": "active",
        "endpoints": {
            "sequential_search": "/v1/search/sequential",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test OpenSearch connection
        from app.services.opensearch_client import opensearch_client
        opensearch_client.client.ping()
        opensearch_status = "connected"
    except:
        opensearch_status = "disconnected"

    return {
        "status": "healthy" if opensearch_status == "connected" else "degraded",
        "opensearch": opensearch_status,
        "timestamp": time.time()
    }

@app.post("/v1/search/sequential", response_model=SequentialSearchResponse)
async def sequential_search(request: SequentialSearchRequest):
    """
    Sequential Company → People Search

    Process:
    1. Query companies with company_criteria
    2. Get matching company names
    3. Query people with people_criteria AND company filter
    4. Return matching profiles

    Example Request:
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
        "seniority": ["senior"]
      },
      "page": 1,
      "page_size": 25
    }

    Returns:
    {
      "status": "success",
      "results": [...],
      "metadata": {
        "companies_matched": 547,
        "profiles_matched": 8234,
        "query_time_ms": 387,
        ...
      }
    }
    """
    try:
        # Execute sequential search with production features
        results = await sequential_service.execute_sequential_search(
            company_criteria=request.company_criteria.model_dump(exclude_none=True),
            people_criteria=request.people_criteria.model_dump(exclude_none=True),
            page=request.page,
            page_size=request.page_size,
            session_token=request.session_token,
            cursor=request.cursor
        )

        return results  # Already matches SequentialSearchResponse structure

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )

# AWS Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    # For local testing
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
