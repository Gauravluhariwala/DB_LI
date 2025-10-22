"""
Request models for Sequential Search API
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class CompanyCriteria(BaseModel):
    """Company filter criteria"""
    # Basic filters
    industry: Optional[List[str]] = Field(None, description="Industry names")
    size: Optional[List[str]] = Field(None, description="Company size ranges, e.g., ['11_50', '51_200']")
    founded_after: Optional[int] = Field(None, description="Founded year (>=)")
    founded_before: Optional[int] = Field(None, description="Founded year (<=)")

    # Location filters
    location_country: Optional[str] = Field(None, description="Country code")
    location_contains: Optional[str] = Field(None, description="Location search term")
    hq_city: Optional[List[str]] = Field(None, description="Headquarter city names (OR logic)")

    # Financial
    revenue_min: Optional[int] = Field(None, description="Minimum revenue")

    # Company identification
    company_name: Optional[List[str]] = Field(None, description="Company names (OR logic, fuzzy match)")
    specialties: Optional[List[str]] = Field(None, description="Company specialties/tags (OR logic)")

class PeopleCriteria(BaseModel):
    """People filter criteria"""
    # Job & Title
    job_title: Optional[List[str]] = Field(None, description="Job titles (OR logic, fuzzy match)")
    current_title_extracted: Optional[List[str]] = Field(None, description="Extracted current titles (more accurate)")
    job_description_contains: Optional[str] = Field(None, description="Keyword search in job descriptions")

    # Name search
    name: Optional[List[str]] = Field(None, description="Names to search (OR logic, fuzzy match)")

    # Location
    location: Optional[List[str]] = Field(None, description="Location names (OR logic)")
    location_country: Optional[List[str]] = Field(None, description="Country codes (OR logic)")
    job_location: Optional[List[str]] = Field(None, description="Job location (from position, may differ from person location)")

    # Experience & Seniority
    seniority: Optional[List[str]] = Field(None, description="Seniority levels")
    years_of_experience: Optional[List[str]] = Field(None, description="Experience ranges")
    years_in_current_role: Optional[List[str]] = Field(None, description="Current role duration ranges")

    # Employment
    employment_type: Optional[List[str]] = Field(None, description="Employment types: Full-time, Part-time, Contract, Freelance")
    started_current_job_after: Optional[int] = Field(None, description="Started current job after year (for finding new hires)")

    # Skills & Industry
    skills: Optional[List[str]] = Field(None, description="Skills (OR logic)")
    industry: Optional[List[str]] = Field(None, description="Industry")

    # Education
    education_school: Optional[List[str]] = Field(None, description="School/university names (OR logic, fuzzy match)")
    education_degree: Optional[List[str]] = Field(None, description="Degree types (OR logic, fuzzy match)")
    education_field: Optional[List[str]] = Field(None, description="Fields of study (OR logic, fuzzy match)")
    graduated_after: Optional[int] = Field(None, description="Graduated after year (for recent grads)")
    graduated_before: Optional[int] = Field(None, description="Graduated before year")

    # Work History
    previous_company: Optional[List[str]] = Field(None, description="Previous employer names (OR logic, fuzzy match)")

    # Profile Content
    summary_contains: Optional[str] = Field(None, description="Keyword search in profile summary/bio")

    # Certifications
    certifications: Optional[List[str]] = Field(None, description="Certification names (OR logic, fuzzy match)")

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
