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
from app.models.profile_response import ProfileResponse, BatchProfileRequest, BatchProfileResponse
from app.services import sequential_service_optimized as sequential_service
from app.services import profile_service
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
        "version": "1.3.0",
        "status": "active",
        "endpoints": {
            "sequential_search": "/v1/search/sequential",
            "profile_by_id": "/v1/profiles/{publicId}",
            "profiles_batch": "/v1/profiles/batch",
            "search_by_name": "/v1/profiles/search/by-name/{fullName}",
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

# ============================================================
# Individual Profile Lookup Endpoints
# ============================================================

@app.get("/v1/profiles/{public_id}", response_model=ProfileResponse)
async def get_profile(public_id: str, include_fields: str = None):
    """
    Fetch a single LinkedIn profile by publicId

    **Path Parameter:**
    - public_id: LinkedIn public ID (e.g., "john-smith-12345")

    **Query Parameter:**
    - include_fields: Comma-separated list of fields to return (optional)

    **Example:**
    ```
    GET /v1/profiles/john-smith-12345
    GET /v1/profiles/john-smith-12345?include_fields=publicId,fullName,headline
    ```

    **Returns:** Complete profile data or 404 if not found

    **Use Cases:**
    - Get full profile details for a specific person
    - Enrich existing data with LinkedIn profile
    - Build profile detail pages
    """
    # Parse include_fields if provided
    fields_list = None
    if include_fields:
        fields_list = [f.strip() for f in include_fields.split(',')]

    try:
        profile = profile_service.get_profile_by_id(public_id, include_fields=fields_list)

        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail=f"Profile not found: {public_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile fetch error: {str(e)}")


@app.post("/v1/profiles/batch", response_model=BatchProfileResponse)
async def get_profiles_batch(request: BatchProfileRequest):
    """
    Fetch multiple LinkedIn profiles by publicIds (batch lookup)

    **Request:**
    ```json
    {
      "public_ids": ["john-smith-12345", "jane-doe-67890"],
      "include_fields": ["publicId", "fullName", "headline"]
    }
    ```

    **Limits:**
    - Max 100 profiles per request
    - Profiles not found are listed in "not_found" array

    **Returns:**
    ```json
    {
      "profiles": [
        {"publicId": "john-smith-12345", "fullName": "John Smith", ...},
        {"publicId": "jane-doe-67890", "fullName": "Jane Doe", ...}
      ],
      "total_found": 2,
      "total_requested": 2,
      "not_found": []
    }
    ```

    **Use Cases:**
    - Bulk profile enrichment
    - Fetch profiles for a list of IDs
    - Build contact lists with full details
    """
    try:
        profiles = profile_service.get_profiles_batch(
            public_ids=request.public_ids,
            include_fields=request.include_fields
        )

        # Find which IDs weren't found
        found_ids = {p['publicId'] for p in profiles}
        not_found = [pid for pid in request.public_ids if pid not in found_ids]

        return {
            "profiles": profiles,
            "total_found": len(profiles),
            "total_requested": len(request.public_ids),
            "not_found": not_found
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch fetch error: {str(e)}")


@app.get("/v1/profiles/search/by-name/{full_name}")
async def search_by_name(full_name: str, limit: int = 10):
    """
    Search profiles by exact full name (for name disambiguation)

    **Path Parameter:**
    - full_name: Full name to search (e.g., "John Smith")

    **Query Parameter:**
    - limit: Max results (default: 10, max: 50)

    **Example:**
    ```
    GET /v1/profiles/search/by-name/John%20Smith
    GET /v1/profiles/search/by-name/John%20Smith?limit=20
    ```

    **Returns:** List of profiles with matching names

    **Use Case:**
    - When multiple people have the same name
    - Name disambiguation
    - "Which John Smith did you mean?"
    """
    try:
        limit = min(limit, 50)  # Cap at 50
        profiles = profile_service.search_profiles_by_name_exact(full_name, limit=limit)

        return {
            "query": full_name,
            "results": profiles,
            "total_found": len(profiles)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Name search error: {str(e)}")

