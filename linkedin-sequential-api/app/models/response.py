"""
Response models for Sequential Search API
"""
from pydantic import BaseModel
from typing import List, Any, Dict, Optional

class PaginationInfo(BaseModel):
    """Pagination information"""
    current_page: int
    page_size: int
    total_results: int
    total_pages: int
    has_next: bool
    has_previous: bool
    session_token: str  # For consistent pagination
    next_cursor: Optional[str] = None  # For deep pagination (pages >20)

class QueryMetadata(BaseModel):
    """Metadata about the query execution"""
    companies_matched: int
    companies_used: int
    company_filter_applied: int  # Actual unique companies in filter
    profiles_matched: int
    query_time_ms: int
    search_mode: str  # "sequential" or "direct"
    suggestion: Optional[str] = None  # Refinement suggestions

class SequentialSearchResponse(BaseModel):
    """
    Production response from sequential search

    Includes:
    - Search results
    - Rich metadata
    - Pagination info with session token
    - Refinement suggestions
    """
    status: str = "success"
    results: List[Dict[str, Any]]
    pagination: PaginationInfo
    metadata: QueryMetadata
