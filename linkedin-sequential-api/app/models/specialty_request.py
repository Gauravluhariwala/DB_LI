"""
Request/Response models for Specialty Semantic Search
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SpecialtySearchRequest(BaseModel):
    """
    Request for semantic specialty search

    Example:
    {
      "query": "artificial intelligence",
      "n_results": 10,
      "min_count": 10
    }
    """
    query: str = Field(..., description="Search query for semantic similarity")
    n_results: int = Field(3, ge=1, le=50, description="Number of results to return (default: 3)")
    min_count: int = Field(None, ge=1, description="Optional: Minimum company count filter")
    sort_by_count: bool = Field(True, description="Sort results by company count (default: True)")

class SpecialtySearchResponse(BaseModel):
    """
    Response from specialty search

    Example:
    {
      "query": "AI",
      "results": [
        {
          "specialty": "AI",
          "count": 79,
          "rank": 23,
          "similarity_score": 1.0
        },
        ...
      ],
      "total_results": 10
    }
    """
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    metadata: Dict[str, Any]

class SpecialtyExpansionRequest(BaseModel):
    """
    Request for query expansion

    Example:
    {
      "query": "blockchain",
      "expansion_count": 5
    }
    """
    query: str = Field(..., description="Term to expand")
    expansion_count: int = Field(5, ge=1, le=20, description="How many similar terms (1-20)")

class SpecialtyExpansionResponse(BaseModel):
    """
    Response with expanded terms

    Example:
    {
      "original_query": "AI",
      "expanded_terms": [
        "AI",
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Data Science"
      ],
      "count": 5
    }
    """
    original_query: str
    expanded_terms: List[str]
    count: int
