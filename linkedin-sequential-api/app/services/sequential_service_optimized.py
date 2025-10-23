"""
Sequential Search Orchestration Service - Production Optimized
Coordinates company → people sequential queries with session management
"""

import time
import asyncio
import base64
import json
from typing import Dict, Any
from app.services import company_service, people_service
from app.utils.session_token import generate_session_token, decode_session_token, validate_token_matches_criteria
from app.config import settings

async def execute_sequential_search(
    company_criteria: dict,
    people_criteria: dict,
    page: int = 1,
    page_size: int = 25,
    session_token: str = None,
    cursor: str = None
) -> Dict[str, Any]:
    """
    Execute production-grade sequential company → people search

    FEATURES:
    - Session tokens for pagination consistency
    - Hybrid pagination (offset 1-20, cursor 20+)
    - Smart fallback to direct search
    - Field filtering for performance
    - Comprehensive metadata

    Process:
    1. Check for session token (reuse company list)
    2. If no token, query companies and generate token
    3. Query people with company filter
    4. Return results with pagination info

    Args:
        company_criteria: Filters for company query
        people_criteria: Filters for people query
        page: Page number (1-20)
        page_size: Results per page (10-50)
        session_token: Token from previous page (for consistency)
        cursor: Cursor for pages >20

    Returns:
        {
            'status': 'success',
            'results': [...profiles...],
            'pagination': {
                'current_page': 1,
                'page_size': 25,
                'total_results': 10000,
                'total_pages': 400,
                'has_next': true,
                'session_token': 'sess_abc...'
            },
            'metadata': {
                'companies_matched': 795324,
                'companies_used': 200,
                'search_mode': 'sequential',
                'query_time_ms': 645
            }
        }
    """
    start_time = time.time()
    loop = asyncio.get_event_loop()

    # OPTIMIZATION 1: Check if session token provided (pagination)
    if session_token:
        try:
            # Decode token to get cached company list
            token_payload = decode_session_token(session_token)

            # Validate token matches current criteria
            if not validate_token_matches_criteria(token_payload, company_criteria, people_criteria):
                return {
                    'status': 'error',
                    'error': 'token_mismatch',
                    'message': 'Search criteria changed. Please restart from page 1.'
                }

            # Use company list from token (skip company query!)
            company_names = token_payload['cnames']
            companies_count = len(company_names)
            search_mode = 'sequential_cached'

        except ValueError as e:
            # Token invalid/expired
            return {
                'status': 'error',
                'error': 'invalid_token',
                'message': str(e)
            }

    else:
        # No token - first page, execute full sequential search

        # Check if company criteria is empty (smart fallback)
        has_company_filters = any([
            company_criteria.get('industry'),
            company_criteria.get('size'),
            company_criteria.get('location_country'),
            company_criteria.get('founded_after'),
            company_criteria.get('founded_before'),
            company_criteria.get('location_contains'),
            company_criteria.get('revenue_min'),
            company_criteria.get('company_name'),
            company_criteria.get('specialties'),
            company_criteria.get('hq_city'),
            company_criteria.get('domain'),             # NEW
            company_criteria.get('funding_round'),      # NEW
            company_criteria.get('lead_investor'),      # NEW
            company_criteria.get('min_funding_rounds')  # NEW
        ])

        if not has_company_filters:
            # FALLBACK: Direct people search (no company filtering)
            search_mode = 'direct'
            company_names = []
            companies_count = 0
        else:
            # STEP 1: Query companies (TESTING: increased limit)
            search_mode = 'sequential'
            company_names, companies_count = await loop.run_in_executor(
                None,
                company_service.search_companies,
                company_criteria,
                10000  # NO LIMIT: Get ALL matching companies
            )

            if not company_names:
                # No companies matched
                return {
                    'status': 'success',
                    'results': [],
                    'pagination': {
                        'current_page': page,
                        'page_size': page_size,
                        'total_results': 0,
                        'total_pages': 0,
                        'has_next': False,
                        'has_previous': False,
                        'session_token': ''
                    },
                    'metadata': {
                        'companies_matched': companies_count,
                        'companies_used': 0,
                        'company_filter_applied': 0,
                        'profiles_matched': 0,
                        'query_time_ms': int((time.time() - start_time) * 1000),
                        'search_mode': search_mode,
                        'suggestion': 'No companies matched your criteria. Try broadening company filters.'
                    }
                }

    # STEP 2: Query people (optimized: field filtering, cursor support)
    people_results = await loop.run_in_executor(
        None,
        people_service.search_people_at_companies,
        people_criteria,
        company_names,
        page,
        page_size,
        cursor
    )

    # Extract results
    profiles = [hit['_source'] for hit in people_results['hits']['hits']]
    total_profiles = people_results['hits']['total']['value']
    total_pages = (total_profiles + page_size - 1) // page_size

    # Generate or reuse session token
    if not session_token and company_names:
        new_session_token = generate_session_token(
            company_names,
            company_criteria,
            people_criteria
        )
    else:
        new_session_token = session_token or ''

    # Generate cursor for next page if needed
    next_cursor = None
    if people_results['hits']['hits'] and page >= 20 and (page * page_size) < total_profiles:
        # Get sort values from last hit for search_after
        last_hit = people_results['hits']['hits'][-1]
        sort_values = last_hit.get('sort', [])
        if sort_values:
            next_cursor = base64.urlsafe_b64encode(json.dumps(sort_values).encode()).decode()

    query_time_ms = int((time.time() - start_time) * 1000)

    # Generate refinement suggestion if too many companies
    suggestion = None
    if companies_count > 1000:
        suggestion = f"{companies_count:,} companies matched. Consider adding location, size, or founded_after filters to refine results."

    return {
        'status': 'success',
        'results': profiles,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_results': total_profiles,
            'total_pages': total_pages,
            'has_next': (page * page_size) < total_profiles,
            'has_previous': page > 1,
            'session_token': new_session_token,
            'next_cursor': next_cursor
        },
        'metadata': {
            'companies_matched': companies_count,
            'companies_used': len(company_names),
            'company_filter_applied': len(company_names),
            'profiles_matched': total_profiles,
            'query_time_ms': query_time_ms,
            'search_mode': search_mode,
            'suggestion': suggestion
        }
    }
