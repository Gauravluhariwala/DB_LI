"""
Request models for Sequential Search API
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class CompanyCriteria(BaseModel):
    """Company filter criteria"""
    industry: Optional[List[str]] = Field(None, description="Industry names")
    size: Optional[List[str]] = Field(None, description="Company size ranges, e.g., ['11_50', '51_200']")
    founded_after: Optional[int] = Field(None, description="Founded year (>=)")
    founded_before: Optional[int] = Field(None, description="Founded year (<=)")
    location_country: Optional[str] = Field(None, description="Country code")
    location_contains: Optional[str] = Field(None, description="Location search term")
    revenue_min: Optional[int] = Field(None, description="Minimum revenue")

class PeopleCriteria(BaseModel):
    """People filter criteria"""
    job_title: Optional[str] = Field(None, description="Job title search")
    location: Optional[str] = Field(None, description="Location name")
    seniority: Optional[List[str]] = Field(None, description="Seniority levels")
    years_of_experience: Optional[List[str]] = Field(None, description="Experience ranges")
    years_in_current_role: Optional[List[str]] = Field(None, description="Current role duration")
    skills: Optional[List[str]] = Field(None, description="Skills")
    industry: Optional[List[str]] = Field(None, description="Industry")

class SequentialSearchRequest(BaseModel):
    """
    Sequential search request: Company filters → People filters

    Production Features:
    - Session tokens for consistent pagination
    - Cursor-based deep pagination (pages >20)
    - Configurable page size (10-50)

    Example:
    {
      "company_criteria": {
        "industry": ["Technology"],
        "size": ["11_50", "51_200"],
        "founded_after": 2010
      },
      "people_criteria": {
        "job_title": "Engineer",
        "location": "San Francisco",
        "seniority": ["senior"]
      },
      "page": 1,
      "page_size": 25,
      "session_token": null,  // For pages 2+, use token from page 1
      "cursor": null          // For pages >20, use cursor from previous page
    }
    """
    company_criteria: CompanyCriteria
    people_criteria: PeopleCriteria

    # Pagination
    page: int = Field(1, ge=1, le=20, description="Page number (1-20 for offset-based)")
    page_size: int = Field(25, ge=10, le=50, description="Results per page (10-50)")

    # Consistency & Performance
    session_token: Optional[str] = Field(None, description="Token from page 1 for consistent pagination")

    # Deep pagination (pages >20)
    cursor: Optional[str] = Field(None, description="Cursor for pages >20 (from previous response)")
