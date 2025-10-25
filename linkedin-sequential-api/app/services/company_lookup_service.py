"""
Company Lookup Service
Batch fetch company details (domain, industry) using LinkedIn company IDs
"""

from typing import List, Dict, Any
from app.services.opensearch_client import opensearch_client


def get_companies_by_ids(company_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    Batch lookup company details by LinkedIn company IDs (memberIds)

    Args:
        company_ids: List of LinkedIn company IDs (from profile companyId field)

    Returns:
        Dict mapping company ID to company data:
        {
            88002910: {"domain": "creditcode.com", "industry": "Financial Services"},
            1441: {"domain": "google.com", "industry": "Internet"},
            ...
        }
    """

    if not company_ids:
        return {}

    # Remove duplicates and None values
    unique_ids = list(set([cid for cid in company_ids if cid]))

    if not unique_ids:
        return {}

    # Limit to reasonable batch size
    unique_ids = unique_ids[:500]  # Max 500 companies per batch

    try:
        # Build OpenSearch query - lookup by memberId
        query = {
            "query": {
                "terms": {
                    "memberId": unique_ids
                }
            },
            "size": len(unique_ids),
            "_source": ["memberId", "domain", "industry"]  # ONLY what's needed
        }

        # Execute query
        results = opensearch_client.client.search(
            index="linkedin-prod-companies",
            body=query
        )

        # Build mapping: company ID → company data
        company_map = {}

        for hit in results['hits']['hits']:
            company = hit['_source']
            member_id = company.get('memberId')

            if member_id:
                company_map[member_id] = {
                    'domain': company.get('domain') if company.get('domain') else None,
                    'industry': company.get('industry') if company.get('industry') else None
                }

        return company_map

    except Exception as e:
        print(f"Error fetching companies by IDs: {e}")
        return {}


def extract_company_id(company_obj: Dict) -> int:
    """
    Extract LinkedIn company ID from company object
    Tries companyId first, then extracts from URL if available
    """
    # Try companyId first
    if company_obj.get('companyId'):
        return company_obj['companyId']

    # Extract from URL
    url = company_obj.get('url', '')
    if url and '/company/' in url:
        try:
            # URL format: https://www.linkedin.com/company/12345/
            parts = url.split('/company/')
            if len(parts) > 1:
                id_str = parts[1].strip('/')
                return int(id_str)
        except:
            pass

    return None


def enrich_profile_companies(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich company objects in profiles with domain and industry
    Uses LinkedIn company IDs (from companyId or URL) for accurate matching

    Args:
        profiles: List of profile dicts

    Returns:
        Profiles with enriched company objects (domain + industry added)
    """

    if not profiles:
        return profiles

    # Step 1: Extract ALL unique company IDs from all profiles
    company_ids = set()

    for profile in profiles:
        # From current companies
        for company in profile.get('currentCompanies', []):
            comp_id = extract_company_id(company.get('company', {}))
            if comp_id:
                company_ids.add(comp_id)

        # From previous companies
        for company in profile.get('previousCompanies', []):
            comp_id = extract_company_id(company.get('company', {}))
            if comp_id:
                company_ids.add(comp_id)

    # Step 2: Batch fetch company data using IDs
    company_data_map = get_companies_by_ids(list(company_ids))

    # Step 3: Merge company data into profiles
    for profile in profiles:
        # Enrich current companies
        for company in profile.get('currentCompanies', []):
            comp_id = extract_company_id(company.get('company', {}))  # Use extract function (handles URL)
            if comp_id and comp_id in company_data_map:
                company['company']['domain'] = company_data_map[comp_id].get('domain')
                company['company']['industry'] = company_data_map[comp_id].get('industry')

        # Enrich previous companies
        for company in profile.get('previousCompanies', []):
            comp_id = extract_company_id(company.get('company', {}))  # Use extract function (handles URL)
            if comp_id and comp_id in company_data_map:
                company['company']['domain'] = company_data_map[comp_id].get('domain')
                company['company']['industry'] = company_data_map[comp_id].get('industry')

    return profiles
