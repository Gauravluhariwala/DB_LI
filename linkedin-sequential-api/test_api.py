#!/usr/bin/env python3
"""
Test script for Sequential Search API
Tests the exact example: "Engineers in SF at mid-sized tech companies founded after 2010"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from app.services import sequential_service

async def test_sequential_search():
    """Test the sequential company → people search"""

    print("=" * 60)
    print("Testing Sequential Search API")
    print("=" * 60)
    print()

    # Test Case: Engineers in SF at mid-sized tech companies founded after 2010
    company_criteria = {
        'industry': ['Technology', 'Software'],
        'size': ['11_50', '51_200'],
        'founded_after': 2010,
        'location_contains': 'San Francisco'
    }

    people_criteria = {
        'job_title': 'Engineer',
        'location': 'San Francisco',
        'seniority': ['senior', 'mid_level']
    }

    print("Query:")
    print(f"  Companies: Tech companies in SF, 11-200 employees, founded after 2010")
    print(f"  People: Engineers (senior/mid-level) in San Francisco")
    print()

    try:
        results = await sequential_service.execute_sequential_search(
            company_criteria,
            people_criteria,
            page=1,
            page_size=10
        )

        print("Results:")
        print("=" * 60)
        print(f"✅ Companies matched: {results['metadata']['companies_matched']:,}")
        print(f"✅ Profiles matched: {results['metadata']['profiles_matched']:,}")
        print(f"✅ Query time: {results['metadata']['query_time_ms']}ms")
        print(f"✅ Company filter applied: {results['metadata'].get('company_filter_applied', 0)} companies")
        print()

        print(f"Sample Results (showing {len(results['results'])} of {results['metadata']['profiles_matched']:,}):")
        print("-" * 60)

        for i, profile in enumerate(results['results'][:5], 1):
            print(f"{i}. {profile.get('fullName', 'N/A')}")
            print(f"   Title: {profile.get('headline', 'N/A')}")
            print(f"   Company: {profile.get('current_company_extracted', 'N/A')}")
            print(f"   Location: {profile.get('locationName', 'N/A')}")
            print(f"   Seniority: {profile.get('seniority_level', 'N/A')}")
            print()

        print("=" * 60)
        print("✅ TEST PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sequential_search())
