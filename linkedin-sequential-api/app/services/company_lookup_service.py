"""
Company Lookup Service - Hybrid ID + Name Matching
Enriches companies and education with domain + industry
Uses both memberId and name matching for maximum coverage
"""

from typing import List, Dict, Any, Tuple
from app.services.opensearch_client import opensearch_client


def get_companies_hybrid(
    company_ids_to_names: Dict[int, str]
) -> Dict[int, Dict[str, Any]]:
    """
    Hybrid lookup: Try ID first, fallback to name matching

    Args:
        company_ids_to_names: Map of {companyId: companyName}

    Returns:
        Map of {companyId: {"domain": "...", "industry": "..."}}
    """

    if not company_ids_to_names:
        return {}

    result_map = {}

    # STEP 1: Try matching by memberId (fast, accurate when it works)
    company_ids = list(company_ids_to_names.keys())

    try:
        query_by_id = {
            "query": {"terms": {"memberId": company_ids}},
            "size": len(company_ids),
            "_source": ["memberId", "domain", "industry"]
        }

        id_results = opensearch_client.client.search(
            index="linkedin-prod-companies",
            body=query_by_id
        )

        # Store ID matches
        matched_ids = set()

        for hit in id_results['hits']['hits']:
            company = hit['_source']
            member_id = company.get('memberId')

            if member_id and member_id in company_ids_to_names:
                result_map[member_id] = {
                    'domain': company.get('domain') if company.get('domain') else None,
                    'industry': company.get('industry') if company.get('industry') else None
                }
                matched_ids.add(member_id)

    except Exception as e:
        print(f"Error in ID matching: {e}")
        matched_ids = set()

    # STEP 2: For unmatched IDs, try name matching (fallback)
    unmatched_ids = set(company_ids) - matched_ids

    if unmatched_ids:
        unmatched_names = [company_ids_to_names[cid] for cid in unmatched_ids if cid in company_ids_to_names]

        try:
            # Simple name matching - use terms query to avoid clause explosion
            query_by_name = {
                "query": {
                    "terms": {
                        "name.keyword": unmatched_names[:100]  # Exact match only, simple
                    }
                },
                "size": len(unmatched_names),
                "_source": ["name", "memberId", "domain", "industry"]
            }

            name_results = opensearch_client.client.search(
                index="linkedin-prod-companies",
                body=query_by_name
            )

            # Map results back to original IDs by name
            name_to_data = {}
            for hit in name_results['hits']['hits']:
                company = hit['_source']
                name = company.get('name', '').strip()

                if name and name not in name_to_data:  # Take first (best) match
                    name_to_data[name] = {
                        'domain': company.get('domain') if company.get('domain') else None,
                        'industry': company.get('industry') if company.get('industry') else None
                    }

            # Map back to IDs
            for cid in unmatched_ids:
                if cid in company_ids_to_names:
                    name = company_ids_to_names[cid]
                    if name in name_to_data:
                        result_map[cid] = name_to_data[name]

        except Exception as e:
            print(f"Error in name matching: {e}")

    return result_map


def extract_company_id(company_obj: Dict) -> Tuple[int, str]:
    """
    Extract both ID and name from company object

    Returns:
        (company_id, company_name)
    """
    comp_id = None
    comp_name = company_obj.get('name', '').strip()

    # Try companyId first
    if company_obj.get('companyId'):
        comp_id = company_obj['companyId']
    # Extract from URL if no companyId
    elif company_obj.get('url') and '/company/' in company_obj['url']:
        try:
            parts = company_obj['url'].split('/company/')
            if len(parts) > 1:
                id_str = parts[1].strip('/')
                comp_id = int(id_str)
        except:
            pass

    return (comp_id, comp_name)


def enrich_profile_companies(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich companies AND education with domain + industry
    Uses hybrid ID + name matching for maximum coverage
    """

    if not profiles:
        return profiles

    # Collect ALL IDs and names (companies + schools)
    id_to_name_map = {}

    for profile in profiles:
        # From current companies
        for company in profile.get('currentCompanies', []):
            comp_id, comp_name = extract_company_id(company.get('company', {}))
            if comp_id and comp_name:
                id_to_name_map[comp_id] = comp_name

        # From previous companies
        for company in profile.get('previousCompanies', []):
            comp_id, comp_name = extract_company_id(company.get('company', {}))
            if comp_id and comp_name:
                id_to_name_map[comp_id] = comp_name

        # From education schools
        for education in profile.get('educations', []):
            school = education.get('school', {})
            school_name = school.get('name', '').strip()

            # Try schoolId first
            school_id = school.get('schoolId')

            # If no schoolId, extract from URL (same as companies)
            if not school_id and school.get('url') and '/company/' in school['url']:
                try:
                    parts = school['url'].split('/company/')
                    if len(parts) > 1:
                        school_id = int(parts[1].strip('/'))
                except:
                    pass

            if school_id and school_name:
                try:
                    id_to_name_map[int(school_id)] = school_name
                except:
                    pass

    # Batch lookup with hybrid matching
    enrichment_data = get_companies_hybrid(id_to_name_map)

    # Merge into profiles
    for profile in profiles:
        # Enrich current companies
        for company in profile.get('currentCompanies', []):
            comp_id, _ = extract_company_id(company.get('company', {}))
            if comp_id and comp_id in enrichment_data:
                company['company']['domain'] = enrichment_data[comp_id].get('domain')
                company['company']['industry'] = enrichment_data[comp_id].get('industry')

        # Enrich previous companies
        for company in profile.get('previousCompanies', []):
            comp_id, _ = extract_company_id(company.get('company', {}))
            if comp_id and comp_id in enrichment_data:
                company['company']['domain'] = enrichment_data[comp_id].get('domain')
                company['company']['industry'] = enrichment_data[comp_id].get('industry')

        # Enrich education schools
        for education in profile.get('educations', []):
            school = education.get('school', {})
            school_id = school.get('schoolId')

            if school_id:
                try:
                    school_id_int = int(school_id)
                    if school_id_int in enrichment_data:
                        education['school']['domain'] = enrichment_data[school_id_int].get('domain')
                        education['school']['industry'] = enrichment_data[school_id_int].get('industry')
                except:
                    pass

    return profiles
