"""
Company Search Service
Queries linkedin-prod-companies index and returns company names
"""

from typing import List, Tuple
from app.services.opensearch_client import opensearch_client
from app.config import settings

def search_companies(company_filters: dict, limit: int = 200) -> Tuple[List[str], int]:
    """
    Search companies and return their names for people query

    PRODUCTION OPTIMIZATIONS:
    - Limit to 200 (from 1000) for better people query performance
    - Score by size, followers, employeesOnLi (get BEST companies)
    - Only fetch 'name' field (reduce payload)
    - Use filter clauses (enable caching)

    Args:
        company_filters: Dictionary of company criteria
        limit: Max companies to return (default 200, max 500)

    Returns:
        Tuple of (company_names, total_matched)
    """
    limit = min(limit, 500)  # Hard cap at 500

    # Build OpenSearch query
    query = {
        'query': {
            'bool': {
                'must': [],  # Only for scored queries
                'filter': [],  # Non-scored, faster, cached
                'should': []  # OR logic queries (initialize to avoid KeyError)
            }
        },
        'size': limit,
        '_source': ['name'],  # ONLY name needed (optimization)
        'track_total_hits': 1000,  # OPTIMIZATION: Limit total count (faster!)
        'timeout': '10s',  # Fail fast if query too slow
        # SCORING: Get BEST companies first
        'sort': [
            {'size': {'order': 'desc', 'missing': '_last'}},
            {'employeesOnLi': {'order': 'desc', 'missing': '_last'}},
            {'followers': {'order': 'desc', 'missing': '_last'}}
        ]
    }

    # Industry filter
    if company_filters.get('industry'):
        industries = company_filters['industry']
        if isinstance(industries, str):
            industries = [industries]
        query['query']['bool']['must'].append({
            'terms': {'industry.keyword': industries}
        })

    # Size filter (numeric range: 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+)
    if company_filters.get('size'):
        sizes = company_filters['size']
        if isinstance(sizes, str):
            sizes = [sizes]

        # Convert size ranges to numeric queries
        size_queries = []
        for size_range in sizes:
            if size_range == '1_10':
                size_queries.append({'range': {'size': {'gte': 1, 'lte': 10}}})
            elif size_range == '11_50':
                size_queries.append({'range': {'size': {'gte': 11, 'lte': 50}}})
            elif size_range == '51_200':
                size_queries.append({'range': {'size': {'gte': 51, 'lte': 200}}})
            elif size_range == '201_500':
                size_queries.append({'range': {'size': {'gte': 201, 'lte': 500}}})
            elif size_range == '501_1000':
                size_queries.append({'range': {'size': {'gte': 501, 'lte': 1000}}})
            elif size_range == '1000+':
                size_queries.append({'range': {'size': {'gte': 1000}}})

        if size_queries:
            query['query']['bool']['should'].extend(size_queries)
            query['query']['bool']['minimum_should_match'] = 1

    # Founded year filters
    if company_filters.get('founded_after') or company_filters.get('founded_before'):
        range_query = {}
        if company_filters.get('founded_after'):
            range_query['gte'] = company_filters['founded_after']
        if company_filters.get('founded_before'):
            range_query['lte'] = company_filters['founded_before']

        query['query']['bool']['filter'].append({
            'range': {'founded': range_query}
        })

    # Location country
    if company_filters.get('location_country'):
        query['query']['bool']['filter'].append({
            'term': {'locationCountry.keyword': company_filters['location_country']}
        })

    # Location contains (fuzzy match in overview/name)
    if company_filters.get('location_contains'):
        query['query']['bool']['must'].append({
            'multi_match': {
                'query': company_filters['location_contains'],
                'fields': ['overview', 'name', 'tagline'],
                'type': 'best_fields'
            }
        })

    # Revenue filter
    if company_filters.get('revenue_min'):
        query['query']['bool']['filter'].append({
            'range': {'revenue': {'gte': company_filters['revenue_min']}}
        })

    # Company name search (NEW - fuzzy match)
    if company_filters.get('company_name'):
        company_names = company_filters['company_name']
        if isinstance(company_names, str):
            company_names = [company_names]

        # OR logic across multiple company names
        company_name_queries = []
        for name in company_names:
            company_name_queries.append({
                'match': {
                    'name': {
                        'query': name,
                        'fuzziness': 'AUTO'
                    }
                }
            })

        if company_name_queries:
            query['query']['bool']['should'].extend(company_name_queries)
            query['query']['bool']['minimum_should_match'] = 1

    # Specialties search (NEW - OR logic)
    if company_filters.get('specialties'):
        specs = company_filters['specialties']
        if isinstance(specs, str):
            specs = [specs]

        # OR logic: match any specialty
        for spec in specs:
            query['query']['bool']['should'].append({
                'match': {
                    'specialties': {
                        'query': spec,
                        'fuzziness': 'AUTO'
                    }
                }
            })

        if specs:
            query['query']['bool']['minimum_should_match'] = 1

    # HQ City filter (NEW)
    if company_filters.get('hq_city'):
        cities = company_filters['hq_city']
        if isinstance(cities, str):
            cities = [cities]

        # OR logic: match any city
        query['query']['bool']['filter'].append({
            'terms': {'headquarter.address.city.keyword': cities}
        })

    # Execute query
    results = opensearch_client.client.search(
        index=settings.companies_index,
        body=query
    )

    # Extract and clean company names
    company_names = [
        hit['_source']['name']
        for hit in results['hits']['hits']
        if hit['_source'].get('name') and hit['_source']['name'].strip()
    ]

    # Remove duplicates and sort for performance (research: sorted terms = faster)
    company_names_unique = sorted(list(set(company_names)))

    total_matched = results['hits']['total']['value']

    return company_names_unique, total_matched
