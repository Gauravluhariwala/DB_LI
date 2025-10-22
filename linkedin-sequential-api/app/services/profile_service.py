"""
Profile Service - Individual Profile Lookup
Fetch individual LinkedIn profiles by publicId or URN
"""

from typing import Optional, List, Dict, Any
from app.services.opensearch_client import opensearch_client
from app.config import settings


def get_profile_by_id(public_id: str, include_fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch a single LinkedIn profile by publicId

    Args:
        public_id: LinkedIn public ID (e.g., "john-smith-12345")
        include_fields: Optional list of fields to return (None = all fields)

    Returns:
        Profile dict or None if not found

    Example:
        profile = get_profile_by_id("john-smith-12345")
    """
    # Search across all 8 profile indices
    indices = [
        "linkedin_profiles_enriched_0",
        "linkedin_profiles_enriched_1",
        "linkedin_profiles_enriched_2",
        "linkedin_profiles_enriched_3",
        "linkedin_profiles_enriched_4",
        "linkedin_profiles_enriched_5",
        "linkedin_profiles_enriched_6",
        "linkedin_profiles_enriched_7"
    ]

    query = {
        "query": {
            "term": {
                "publicId.keyword": public_id
            }
        },
        "size": 1
    }

    # Field filtering if requested
    if include_fields:
        query["_source"] = {"includes": include_fields}

    try:
        # Search all indices
        for index in indices:
            result = opensearch_client.client.search(
                index=index,
                body=query
            )

            if result['hits']['hits']:
                # Found it!
                profile = result['hits']['hits'][0]['_source']
                profile['_index'] = index  # Add which index it came from
                return profile

        # Not found in any index
        return None

    except Exception as e:
        print(f"Error fetching profile {public_id}: {e}")
        return None


def get_profiles_batch(public_ids: List[str], include_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Fetch multiple LinkedIn profiles by publicIds (batch lookup)

    Args:
        public_ids: List of LinkedIn public IDs
        include_fields: Optional list of fields to return

    Returns:
        List of profile dicts (profiles not found are omitted)

    Example:
        profiles = get_profiles_batch(["john-smith-12345", "jane-doe-67890"])
    """
    if not public_ids:
        return []

    # Limit batch size
    public_ids = public_ids[:100]  # Max 100 at a time

    # Search all 8 indices
    indices = [
        "linkedin_profiles_enriched_0",
        "linkedin_profiles_enriched_1",
        "linkedin_profiles_enriched_2",
        "linkedin_profiles_enriched_3",
        "linkedin_profiles_enriched_4",
        "linkedin_profiles_enriched_5",
        "linkedin_profiles_enriched_6",
        "linkedin_profiles_enriched_7"
    ]

    query = {
        "query": {
            "terms": {
                "publicId.keyword": public_ids
            }
        },
        "size": len(public_ids)
    }

    # Field filtering if requested
    if include_fields:
        query["_source"] = {"includes": include_fields}

    profiles = []

    try:
        # Search all indices
        for index in indices:
            result = opensearch_client.client.search(
                index=index,
                body=query
            )

            for hit in result['hits']['hits']:
                profile = hit['_source']
                profile['_index'] = index
                profiles.append(profile)

        return profiles

    except Exception as e:
        print(f"Error batch fetching profiles: {e}")
        return []


def search_profiles_by_name_exact(full_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search profiles by exact full name match (for name disambiguation)

    Args:
        full_name: Full name to search (e.g., "John Smith")
        limit: Max results to return

    Returns:
        List of matching profiles

    Use case: When multiple people have same name, return all matches
    """
    indices = [
        "linkedin_profiles_enriched_0",
        "linkedin_profiles_enriched_1",
        "linkedin_profiles_enriched_2",
        "linkedin_profiles_enriched_3",
        "linkedin_profiles_enriched_4",
        "linkedin_profiles_enriched_5",
        "linkedin_profiles_enriched_6",
        "linkedin_profiles_enriched_7"
    ]

    query = {
        "query": {
            "match": {
                "fullName": {
                    "query": full_name,
                    "operator": "and"
                }
            }
        },
        "size": limit,
        "_source": {
            "includes": [
                "publicId", "fullName", "headline", "locationName",
                "current_company_extracted", "logoUrl"
            ]
        }
    }

    profiles = []

    try:
        for index in indices:
            result = opensearch_client.client.search(
                index=index,
                body=query
            )

            for hit in result['hits']['hits']:
                profile = hit['_source']
                profile['_index'] = index
                profiles.append(profile)

            # Stop if we have enough
            if len(profiles) >= limit:
                break

        return profiles[:limit]

    except Exception as e:
        print(f"Error searching by name: {e}")
        return []
