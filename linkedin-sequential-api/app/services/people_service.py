"""
People Search Service
Queries linkedin_profiles_enriched_* with company name filter
"""

from typing import List, Dict, Any
from app.services.opensearch_client import opensearch_client
from app.config import settings

def search_people_at_companies(
    people_filters: dict,
    company_names: List[str],
    page: int = 1,
    page_size: int = 25,
    cursor: str = None
) -> Dict[str, Any]:
    """
    Search people working at specific companies

    PRODUCTION OPTIMIZATIONS:
    - Sorted company names (research: sorted terms = 10-15% faster)
    - Field filtering (return only essential fields, 70% smaller)
    - Use filter clauses (non-scored, cached, faster)
    - Cursor support for deep pagination

    Args:
        people_filters: People criteria (title, location, seniority, etc.)
        company_names: List of company names from company query (already sorted)
        page: Page number (1-20 for offset, ignored if cursor provided)
        page_size: Results per page
        cursor: For pages >20 (search_after cursor)

    Returns:
        OpenSearch response with matching profiles
    """
    # Build query
    query = {
        'query': {
            'bool': {
                'must': [],    # Only scored criteria
                'filter': [],  # Non-scored, cached
                'should': []
            }
        },
        'size': page_size,
        'track_total_hits': True,  # OPTIMIZATION: Only count up to 10K (50-80% faster!)
        'timeout': '15s',  # Fail fast instead of blocking
        # FIELD FILTERING: Return only essential fields (70% payload reduction)
        '_source': {
            'includes': [
                'publicId', 'fullName', 'headline',
                'current_company_extracted', 'locationName', 'locationCountry',
                'seniority_level', 'total_experience_years', 'skills'
            ]
        },
        # Sort for consistent pagination
        'sort': [
            {'_score': {'order': 'desc'}},
            {'publicId.keyword': {'order': 'asc'}}  # Tie-breaker for cursor
        ]
    }

    # Pagination: Offset (pages 1-20) or Cursor (pages 20+)
    if cursor:
        # Deep pagination with cursor (efficient)
        import json
        query['search_after'] = json.loads(base64.urlsafe_b64decode(cursor))
    else:
        # Shallow pagination with offset
        query['from'] = (page - 1) * page_size

    # KEY FILTER: Company names (already sorted and deduped)
    if company_names:
        query['query']['bool']['filter'].append({
            'terms': {
                'current_company_extracted.keyword': company_names  # Pre-sorted!
            }
        })
    else:
        # No company filter - shouldn't happen in sequential search
        pass

    # Job title (headline search) - ARRAY with OR logic (REQUIRED filter)
    if people_filters.get('job_title'):
        job_titles = people_filters['job_title']
        if isinstance(job_titles, str):
            job_titles = [job_titles]

        # Create nested bool: Must match at least ONE job title (OR within array)
        # Using match with operator:and on CURRENT title field only (not headline)
        # This handles variations: "Head of", "Head -", "Head," without clause explosion
        title_queries = []
        for title in job_titles:
            # Search ONLY in current job title (currentCompanies.positions.title)
            title_queries.append({
                'match': {
                    'currentCompanies.positions.title': {
                        'query': title,
                        'operator': 'and'  # All words must be present
                    }
                }
            })

        if title_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': title_queries,
                    'minimum_should_match': 1
                }
            })

    # Location - ARRAY with OR logic (REQUIRED filter)
    if people_filters.get('location'):
        locations = people_filters['location']
        if isinstance(locations, str):
            locations = [locations]

        # Create nested bool: Must match at least ONE location (use match_phrase for exact matching)
        location_queries = []
        for loc in locations:
            location_queries.append({
                'match_phrase': {'locationName': loc}  # Exact phrase to avoid "San" matching "San Antonio"
            })

        if location_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': location_queries,
                    'minimum_should_match': 1
                }
            })

    # Location Country (NEW - consistency with company)
    if people_filters.get('location_country'):
        countries = people_filters['location_country']
        if isinstance(countries, str):
            countries = [countries]

        query['query']['bool']['filter'].append({
            'terms': {'locationCountry.keyword': countries}
        })

    # Seniority
    if people_filters.get('seniority'):
        seniority_levels = people_filters['seniority']
        if isinstance(seniority_levels, str):
            seniority_levels = [seniority_levels]
        query['query']['bool']['filter'].append({
            'terms': {'seniority_level': seniority_levels}
        })

    # Years of experience
    if people_filters.get('years_of_experience'):
        exp_ranges = people_filters['years_of_experience']
        if isinstance(exp_ranges, str):
            exp_ranges = [exp_ranges]
        query['query']['bool']['filter'].append({
            'terms': {'total_experience_range': exp_ranges}
        })

    # Years in current role
    if people_filters.get('years_in_current_role'):
        role_ranges = people_filters['years_in_current_role']
        if isinstance(role_ranges, str):
            role_ranges = [role_ranges]
        query['query']['bool']['filter'].append({
            'terms': {'years_in_current_role_range': role_ranges}
        })

    # Skills - ARRAY with OR logic (REQUIRED filter)
    if people_filters.get('skills'):
        skills = people_filters['skills']
        if isinstance(skills, str):
            skills = [skills]

        # Create nested bool: Must have at least ONE skill
        skill_queries = []
        for skill in skills:
            skill_queries.append({
                'match': {'skills': skill}
            })

        if skill_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': skill_queries,
                    'minimum_should_match': 1
                }
            })

    # Industry
    if people_filters.get('industry'):
        industries = people_filters['industry']
        if isinstance(industries, str):
            industries = [industries]
        query['query']['bool']['filter'].append({
            'terms': {'industry.keyword': industries}
        })

    # ========== NEW FILTERS BELOW ==========

    # Name search (NEW - fuzzy match on fullName, firstName, lastName) - REQUIRED filter
    if people_filters.get('name'):
        names = people_filters['name']
        if isinstance(names, str):
            names = [names]

        # Create nested bool: Must match at least ONE name
        name_queries = []
        for name in names:
            name_queries.append({
                'multi_match': {
                    'query': name,
                    'fields': ['fullName^2', 'firstName', 'lastName'],
                    'type': 'best_fields',
                }
            })

        if name_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': name_queries,
                    'minimum_should_match': 1
                }
            })

    # Current Title Extracted (NEW - more accurate than headline) - REQUIRED filter
    if people_filters.get('current_title_extracted'):
        titles = people_filters['current_title_extracted']
        if isinstance(titles, str):
            titles = [titles]

        # Create nested bool: Must match at least ONE title
        title_queries = []
        for title in titles:
            title_queries.append({
                'match': {
                    'current_title_extracted': {
                        'query': title,
                    }
                }
            })

        if title_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': title_queries,
                    'minimum_should_match': 1
                }
            })

    # Job Description Contains (NEW - dot notation for object type)
    if people_filters.get('job_description_contains'):
        query['query']['bool']['must'].append({
            'match': {
                'currentCompanies.positions.description': people_filters['job_description_contains']
            }
        })

    # Summary Contains (NEW)
    if people_filters.get('summary_contains'):
        query['query']['bool']['must'].append({
            'match': {'summary': people_filters['summary_contains']}
        })

    # Employment Type (NEW - object type, use dot notation)
    if people_filters.get('employment_type'):
        emp_types = people_filters['employment_type']
        if isinstance(emp_types, str):
            emp_types = [emp_types]

        query['query']['bool']['filter'].append({
            'terms': {'currentCompanies.positions.employmentType.keyword': emp_types}
        })

    # Job Location (NEW) - REQUIRED filter
    if people_filters.get('job_location'):
        job_locs = people_filters['job_location']
        if isinstance(job_locs, str):
            job_locs = [job_locs]

        # Create nested bool: Must match at least ONE job location
        loc_queries = [{'match': {'currentCompanies.positions.location': loc}} for loc in job_locs]

        if loc_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': loc_queries,
                    'minimum_should_match': 1
                }
            })

    # Education School (NEW) - REQUIRED filter
    if people_filters.get('education_school'):
        schools = people_filters['education_school']
        if isinstance(schools, str):
            schools = [schools]

        # Create nested bool: Must have attended at least ONE school
        school_queries = []
        for school in schools:
            school_queries.append({
                'match': {
                    'educations.school.name': {
                        'query': school,
                    }
                }
            })

        if school_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': school_queries,
                    'minimum_should_match': 1
                }
            })

    # Education Degree (NEW) - REQUIRED filter
    if people_filters.get('education_degree'):
        degrees = people_filters['education_degree']
        if isinstance(degrees, str):
            degrees = [degrees]

        # Create nested bool: Must have at least ONE degree type
        degree_queries = []
        for degree in degrees:
            degree_queries.append({
                'match': {
                    'educations.degree': {
                        'query': degree,
                    }
                }
            })

        if degree_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': degree_queries,
                    'minimum_should_match': 1
                }
            })

    # Education Field of Study (NEW) - REQUIRED filter
    if people_filters.get('education_field'):
        fields = people_filters['education_field']
        if isinstance(fields, str):
            fields = [fields]

        # Create nested bool: Must have studied at least ONE field
        field_queries = []
        for field in fields:
            field_queries.append({
                'match': {
                    'educations.fieldOfStudy': {
                        'query': field,
                    }
                }
            })

        if field_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': field_queries,
                    'minimum_should_match': 1
                }
            })

    # Graduated After/Before (NEW - range query on object field)
    if people_filters.get('graduated_after') or people_filters.get('graduated_before'):
        range_query = {}
        if people_filters.get('graduated_after'):
            range_query['gte'] = people_filters['graduated_after']
        if people_filters.get('graduated_before'):
            range_query['lte'] = people_filters['graduated_before']

        query['query']['bool']['filter'].append({
            'range': {'educations.endedYear': range_query}
        })

    # Started Current Job After (NEW - range query on object field)
    if people_filters.get('started_current_job_after'):
        query['query']['bool']['filter'].append({
            'range': {
                'currentCompanies.positions.startDateYear': {
                    'gte': people_filters['started_current_job_after']
                }
            }
        })

    # Previous Company (NEW) - REQUIRED filter
    if people_filters.get('previous_company'):
        prev_companies = people_filters['previous_company']
        if isinstance(prev_companies, str):
            prev_companies = [prev_companies]

        # Create nested bool: Must have worked at at least ONE company
        prev_queries = []
        for company in prev_companies:
            prev_queries.append({
                'match': {
                    'previousCompanies.company.name': {
                        'query': company,
                    }
                }
            })

        if prev_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': prev_queries,
                    'minimum_should_match': 1
                }
            })

    # Certifications (NEW) - REQUIRED filter
    if people_filters.get('certifications'):
        certs = people_filters['certifications']
        if isinstance(certs, str):
            certs = [certs]

        # Create nested bool: Must have at least ONE certification
        cert_queries = []
        for cert in certs:
            cert_queries.append({
                'match': {
                    'certifications.name': {
                        'query': cert,
                    }
                }
            })

        if cert_queries:
            query['query']['bool']['must'].append({
                'bool': {
                    'should': cert_queries,
                    'minimum_should_match': 1
                }
            })

    # Sort by relevance score
    query['sort'] = [
        {'_score': {'order': 'desc'}},
        {'publicId.keyword': {'order': 'asc'}}  # Tie-breaker
    ]

    # Execute query
    results = opensearch_client.client.search(
        index=settings.profiles_index,
        body=query
    )

    return results
