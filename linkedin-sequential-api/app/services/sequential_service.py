"""
Sequential Search Orchestration Service
Coordinates company → people sequential queries
"""

import time
import asyncio
from typing import Dict, Any
from app.services import company_service, people_service
from app.config import settings

async def execute_sequential_search(
    company_criteria: dict,
    people_criteria: dict,
    page: int = 1,
    page_size: int = 25
) -> Dict[str, Any]:
    """
    Execute sequential company → people search

    Process:
    1. Query companies with company_criteria
    2. Extract company names
    3. Query people with people_criteria AND company names
    4. Return combined results

    Args:
        company_criteria: Filters for company query
        people_criteria: Filters for people query
        page: Page number
        page_size: Results per page

    Returns:
        {
            'status': 'success',
            'results': [...profiles...],
            'metadata': {
                'companies_matched': 847,
                'profiles_matched': 12453,
                'query_time_ms': 384,
                'page': 1,
                'page_size': 25,
                'total_pages': 498
            }
        }
    """
    start_time = time.time()

    # STEP 1: Query companies
    # Run in executor to make it async-compatible
    loop = asyncio.get_event_loop()
    company_names, companies_count = await loop.run_in_executor(
        None,
        company_service.search_companies,
        company_criteria,
        settings.max_companies_filter
    )

    # If no companies match, return empty result
    if not company_names:
        query_time_ms = int((time.time() - start_time) * 1000)
        return {
            'status': 'success',
            'results': [],
            'metadata': {
                'companies_matched': 0,
                'profiles_matched': 0,
                'query_time_ms': query_time_ms,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
        }

    # STEP 2: Query people at those companies
    people_results = await loop.run_in_executor(
        None,
        people_service.search_people_at_companies,
        people_criteria,
        company_names,
        page,
        page_size
    )

    # Extract profiles
    profiles = [hit['_source'] for hit in people_results['hits']['hits']]
    total_profiles = people_results['hits']['total']['value']
    total_pages = (total_profiles + page_size - 1) // page_size

    query_time_ms = int((time.time() - start_time) * 1000)

    return {
        'status': 'success',
        'results': profiles,
        'metadata': {
            'companies_matched': companies_count,
            'profiles_matched': total_profiles,
            'query_time_ms': query_time_ms,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'company_filter_applied': len(company_names)  # Actual companies used in filter
        }
    }
