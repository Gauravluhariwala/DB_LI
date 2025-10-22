"""
Response models for individual profile lookup
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProfileResponse(BaseModel):
    """
    Individual profile response - Returns ALL 36 fields from OpenSearch

    Includes ALL available LinkedIn profile fields dynamically.
    Extra fields from OpenSearch are automatically included.
    """
    model_config = {"extra": "allow"}  # Pydantic v2 syntax for allowing extra fields

    # Core fields (always present)
    publicId: str

    # Basic info
    fullName: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    pronoun: Optional[str] = None
    urn: Optional[str] = None
    logoUrl: Optional[str] = None
    lastUpdated: Optional[str] = None

    # Location
    locationName: Optional[str] = None
    locationCountry: Optional[str] = None

    # Industry & Company
    industry: Optional[str] = None
    current_company_extracted: Optional[str] = None
    current_title_extracted: Optional[str] = None

    # Experience & Seniority
    seniority_level: Optional[str] = None
    total_experience_years: Optional[int] = None
    total_experience_range: Optional[List[str]] = None
    years_in_current_role: Optional[int] = None
    years_in_current_role_range: Optional[List[str]] = None

    # Network
    connectionsCount: Optional[int] = None
    followersCount: Optional[int] = None

    # Skills & Credentials
    skills: Optional[List[str]] = []
    certifications: Optional[List[Dict[str, Any]]] = []
    courses: Optional[List[Any]] = []

    # Education & Work History
    educations: Optional[List[Dict[str, Any]]] = []
    currentCompanies: Optional[List[Dict[str, Any]]] = []
    previousCompanies: Optional[List[Dict[str, Any]]] = []

    # Professional Activities
    languages: Optional[List[Dict[str, Any]]] = []
    projects: Optional[List[Dict[str, Any]]] = []
    publications: Optional[List[Dict[str, Any]]] = []
    patents: Optional[List[Dict[str, Any]]] = []
    honors: Optional[List[Dict[str, Any]]] = []
    recommendations: Optional[List[Dict[str, Any]]] = []
    organizations: Optional[List[Dict[str, Any]]] = []
    volunteerExperiences: Optional[List[Dict[str, Any]]] = []


class BatchProfileRequest(BaseModel):
    """
    Batch profile lookup request

    Example:
    {
      "public_ids": ["john-smith-12345", "jane-doe-67890"],
      "include_fields": ["publicId", "fullName", "headline"]
    }
    """
    public_ids: List[str] = Field(..., max_length=100, description="List of LinkedIn publicIds (max 100)")
    include_fields: Optional[List[str]] = Field(None, description="Fields to include (None = all fields)")


class BatchProfileResponse(BaseModel):
    """
    Batch profile lookup response

    Example:
    {
      "profiles": [...],
      "total_found": 2,
      "total_requested": 2,
      "not_found": []
    }
    """
    profiles: List[Dict[str, Any]]
    total_found: int
    total_requested: int
    not_found: List[str] = Field(default_factory=list, description="publicIds that weren't found")
