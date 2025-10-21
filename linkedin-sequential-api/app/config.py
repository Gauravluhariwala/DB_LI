"""
Configuration for Sequential Search API
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenSearch
    opensearch_endpoint: str = "il674y001legt8k99rt0.us-east-1.aoss.amazonaws.com"
    aws_region: str = "us-east-1"

    # Index names
    companies_index: str = "linkedin-prod-companies"
    profiles_index: str = "linkedin_profiles_enriched_*"

    # Query limits
    max_companies_filter: int = 1000
    default_page_size: int = 25
    max_page_size: int = 100

    # API
    api_title: str = "LinkedIn Sequential Search API"
    api_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
