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
        limit: Max companies to return (default 200, testing with higher limits)

    Returns:
        Tuple of (company_names, total_matched)
    """
    limit = min(limit, 10000)  # TESTING: Increased cap from 500 to 2000

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
        'track_total_hits': True,  # OPTIMIZATION: Limit total count (faster!)
        'timeout': '10s'  # Fail fast if query too slow
        # NOTE: Sort will be set conditionally below based on filters
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

    # Company name search (FIXED) - Tiered matching: exact > phrase > fuzzy
    if company_filters.get('company_name'):
        company_names = company_filters['company_name']
        if isinstance(company_names, str):
            company_names = [company_names]

        # Create tiered bool query for each company name
        name_queries = []
        for name in company_names:
            # Multi-tier matching with STRONG boosting
            name_queries.append({
                'bool': {
                    'should': [
                        # Tier 1: Exact match (MASSIVE boost for exact company name)
                        {'term': {'name.keyword': {'value': name, 'boost': 1000}}},
                        # Tier 2: Phrase match (medium priority)
                        {'match_phrase': {'name': {'query': name, 'boost': 100}}},
                        # Tier 3: Fuzzy match (lowest priority, for typos)
                    ],
                    'minimum_should_match': 1
                }
            })

        if name_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': name_queries,
                    'minimum_should_match': 1
                }
            })

    # Specialties search (FIXED) - Tiered matching: exact > phrase > fuzzy
    if company_filters.get('specialties'):
        specs = company_filters['specialties']
        if isinstance(specs, str):
            specs = [specs]

        # Create tiered bool query for each specialty
        spec_queries = []
        for spec in specs:
            # Multi-tier matching with boosting
            spec_queries.append({
                'bool': {
                    'should': [
                        # Tier 1: Exact match (highest priority)
                        {'term': {'specialties.keyword': {'value': spec, 'boost': 10}}},
                        # Tier 2: Phrase match (medium priority)
                        {'match_phrase': {'specialties': {'query': spec, 'boost': 5}}},
                        # Tier 3: Fuzzy match (lowest priority, for variations)
                    ],
                    'minimum_should_match': 1
                }
            })

        if spec_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': spec_queries,
                    'minimum_should_match': 1
                }
            })

    # HQ City filter (NEW)
    if company_filters.get('hq_city'):
        cities = company_filters['hq_city']
        if isinstance(cities, str):
            cities = [cities]

        # OR logic: match any city
        query['query']['bool']['filter'].append({
            'terms': {'headquarter.address.city.keyword': cities}
        })

    # Domain filter (NEW) - Exact match on website domain
    if company_filters.get('domain'):
        domains = company_filters['domain']
        if isinstance(domains, str):
            domains = [domains]

        query['query']['bool']['filter'].append({
            'terms': {'domain.keyword': domains}
        })

    # Funding Round filter (NEW) - Filter by funding stage
    if company_filters.get('funding_round'):
        funding_rounds = company_filters['funding_round']
        if isinstance(funding_rounds, str):
            funding_rounds = [funding_rounds]

        query['query']['bool']['filter'].append({
            'terms': {'funding.lastRound.type.keyword': funding_rounds}
        })

    # Lead Investor filter (NEW) - Filter by VC/investor (fuzzy)
    if company_filters.get('lead_investor'):
        investors = company_filters['lead_investor']
        if isinstance(investors, str):
            investors = [investors]

        # Create nested bool for investor OR logic (fuzzy match for variations)
        investor_queries = []
        for investor in investors:
            investor_queries.append({
                'match': {
                    'funding.lastRound.leadInvestors.name': {
                        'query': investor,
                    }
                }
            })

        if investor_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': investor_queries,
                    'minimum_should_match': 1
                }
            })

    # Minimum Funding Rounds filter (NEW)
    if company_filters.get('min_funding_rounds'):
        query['query']['bool']['filter'].append({
            'range': {'funding.roundsCount': {'gte': company_filters['min_funding_rounds']}}
        })

    # Set sort order based on filters
    # If company_name or specialties specified, sort by relevance score (for exact match prioritization)
    # Otherwise, sort by company size/metrics (for quality)
    if company_filters.get('company_name') or company_filters.get('specialties'):
        query['sort'] = [
            {'_score': {'order': 'desc'}},  # Sort by relevance (exact matches first)
            {'size': {'order': 'desc', 'missing': '_last'}}  # Tie-breaker: larger companies
        ]
    else:
        query['sort'] = [
            {'size': {'order': 'desc', 'missing': '_last'}},
            {'employeesOnLi': {'order': 'desc', 'missing': '_last'}},
            {'followers': {'order': 'desc', 'missing': '_last'}}
        ]

    # Execute query
    results = opensearch_client.client.search(
        index=settings.companies_index,
        body=query
    )

    # Extract and clean company names (PRESERVE RELEVANCE ORDER!)
    company_names = []
    seen = set()

    for hit in results['hits']['hits']:
        name = hit['_source'].get('name', '').strip()
        if name and name not in seen:
            company_names.append(name)
            seen.add(name)

    # DO NOT alphabetically sort - preserve relevance order from OpenSearch!
    # (When company_name/specialties specified, results are sorted by _score for exact matches first)
    company_names_unique = company_names

    total_matched = results['hits']['total']['value']

    return company_names_unique, total_matched
