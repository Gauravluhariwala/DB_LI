# LinkedIn Sequential Search API - Complete Documentation

**Production Endpoint:** https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/

**Version:** 1.0.0
**Status:** 🟢 LIVE IN PRODUCTION
**Last Updated:** October 19, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Request Format](#request-format)
5. [Response Format](#response-format)
6. [Filter Reference](#filter-reference)
7. [Pagination](#pagination)
8. [Examples](#examples)
9. [Error Handling](#error-handling)
10. [Performance](#performance)
11. [Rate Limits](#rate-limits)
12. [Best Practices](#best-practices)

---

## Overview

The Sequential Search API performs a two-stage search:

1. **Stage 1:** Query companies with your criteria (industry, size, location, etc.)
2. **Stage 2:** Find people working at those companies with your people criteria (title, seniority, skills, etc.)

**Data Available:**
- 54,404,808 LinkedIn companies
- 826,000,000+ LinkedIn profiles (enriched with experience data)

**Key Features:**
- ✅ Sequential filtering (companies → people)
- ✅ Smart fallback (direct people search when no company criteria)
- ✅ Session tokens (6x faster pagination)
- ✅ Field filtering (70% smaller payloads)
- ✅ Company scoring (get top companies by size/followers)
- ✅ Sub-1s query times (warm Lambda)

---

## Quick Start

### Basic Request

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Financial Services"]
    },
    "people_criteria": {
      "job_title": "Manager",
      "seniority": ["senior"]
    },
    "page": 1,
    "page_size": 25
  }'
```

### Response

```json
{
  "status": "success",
  "results": [
    {
      "publicId": "john-smith-123",
      "fullName": "John Smith",
      "headline": "Senior Manager at Goldman Sachs",
      "current_company_extracted": "Goldman Sachs",
      "locationName": "New York",
      "seniority_level": "senior",
      "total_experience_years": 15
    }
    // ... 24 more results
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 25,
    "total_results": 12453,
    "total_pages": 499,
    "has_next": true,
    "session_token": "eyJ..."
  },
  "metadata": {
    "companies_matched": 795324,
    "companies_used": 186,
    "profiles_matched": 12453,
    "query_time_ms": 645,
    "search_mode": "sequential"
  }
}
```

---

## API Endpoints

### POST /v1/search/sequential

Main search endpoint for sequential company → people queries.

**Authentication:** None (public endpoint)
**Rate Limit:** Unlimited (add API Gateway for rate limiting)
**Timeout:** 29 seconds max

---

## Request Format

### Schema

```typescript
{
  company_criteria: {
    industry?: string[],           // Industry names (exact match)
    size?: string[],               // Size ranges
    founded_after?: number,        // Year (>=)
    founded_before?: number,       // Year (<=)
    location_country?: string,     // Country code
    location_contains?: string,    // Location search
    revenue_min?: number          // Minimum revenue
  },
  people_criteria: {
    job_title?: string,           // Job title search
    location?: string,            // Location name
    seniority?: string[],         // Seniority levels
    years_of_experience?: string[], // Experience ranges
    years_in_current_role?: string[], // Current role duration
    skills?: string[],            // Skills
    industry?: string[]           // Industry
  },
  page: number,                   // Page number (1-20)
  page_size: number,              // Results per page (10-50)
  session_token?: string,         // For pages 2+ (from page 1 response)
  cursor?: string                 // For pages >20 (deep pagination)
}
```

### Field Details

**company_criteria (all optional):**
- `industry`: Array of exact industry names (see [Industry Values](#industry-values))
- `size`: Array of size ranges: `["1_10", "11_50", "51_200", "201_500", "501_1000", "1000+"]`
- `founded_after`: Year (e.g., 2010 means companies founded in 2010 or later)
- `founded_before`: Year (e.g., 2020 means companies founded in 2020 or earlier)
- `location_country`: Two-letter country code (e.g., "US", "GB", "IN")
- `location_contains`: Text search in location/overview (e.g., "San Francisco")
- `revenue_min`: Minimum revenue (numeric)

**people_criteria (all optional, but at least one recommended):**
- `job_title`: Text search in headline (e.g., "Engineer", "Manager")
- `location`: Location name (e.g., "San Francisco", "India")
- `seniority`: Array of levels: `["junior", "mid_level", "manager", "senior", "c_level"]`
- `years_of_experience`: Array of ranges: `["0_2", "2_6", "6_10", "10_15", "15"]`
- `years_in_current_role`: Array of ranges: `["0_2", "2_6", "6_10", "10"]`
- `skills`: Array of skill names (e.g., `["Python", "React"]`)
- `industry`: Array of industry names

**Pagination:**
- `page`: Page number (1-20 for offset-based, requires cursor for >20)
- `page_size`: Results per page (min: 10, max: 50, default: 25)
- `session_token`: Use token from page 1 for faster subsequent pages
- `cursor`: Use for pages >20 (deep pagination)

---

## Response Format

```json
{
  "status": "success",
  "results": [
    {
      "publicId": "string",
      "fullName": "string",
      "headline": "string",
      "current_company_extracted": "string",
      "locationName": "string",
      "locationCountry": "string",
      "seniority_level": "string",
      "total_experience_years": number,
      "skills": ["string"]
    }
  ],
  "pagination": {
    "current_page": number,
    "page_size": number,
    "total_results": number,
    "total_pages": number,
    "has_next": boolean,
    "has_previous": boolean,
    "session_token": "string",
    "next_cursor": "string|null"
  },
  "metadata": {
    "companies_matched": number,
    "companies_used": number,
    "company_filter_applied": number,
    "profiles_matched": number,
    "query_time_ms": number,
    "search_mode": "sequential"|"direct",
    "suggestion": "string|null"
  }
}
```

---

## Filter Reference

### Industry Values

**Use exact values from this list** (case-sensitive):

**Technology:**
- `"Information Technology & Services"` (1.67M companies)
- `"Computer Software"` (1.53M companies)
- `"Internet"` (500K+ companies)
- `"Computer Hardware"` (200K+ companies)

**Financial Services:**
- `"Financial Services"` (795K companies)
- `"Banking"` (300K+ companies)
- `"Investment Banking"` (100K+ companies)

**Healthcare:**
- `"Hospital & Health Care"` (954K companies)
- `"Medical Practice"` (2.24M companies)
- `"Health, Wellness & Fitness"` (751K companies)

**Business Services:**
- `"Management Consulting"` (1.47M companies)
- `"Marketing & Advertising"` (1.29M companies)
- `"Accounting"` (500K+ companies)

**Real Estate & Construction:**
- `"Real Estate"` (2.58M companies)
- `"Construction"` (2.22M companies)

**Retail:**
- `"Retail"` (1.87M companies)
- `"Restaurants"` (1.17M companies)

*To get complete list, use aggregation query on index.*

### Size Ranges

Map to employee counts:
- `"1_10"`: 1-10 employees
- `"11_50"`: 11-50 employees
- `"51_200"`: 51-200 employees
- `"201_500"`: 201-500 employees
- `"501_1000"`: 501-1,000 employees
- `"1000+"`: 1,000+ employees

### Experience Ranges

- `"0_2"`: 0-2 years
- `"2_6"`: 2-6 years
- `"6_10"`: 6-10 years
- `"10_15"`: 10-15 years
- `"15"`: 15+ years

### Seniority Levels

- `"junior"`: Junior level
- `"mid_level"`: Mid-level
- `"manager"`: Manager
- `"senior"`: Senior level
- `"c_level"`: C-level (CEO, CTO, etc.)

---

## Pagination

### Standard Pagination (Pages 1-20)

**Page 1:**
```json
{
  "company_criteria": {...},
  "people_criteria": {...},
  "page": 1,
  "page_size": 25
}
```

**Response includes `session_token`** - save this!

**Page 2:**
```json
{
  "company_criteria": {...},  // Same as page 1
  "people_criteria": {...},   // Same as page 1
  "page": 2,
  "page_size": 25,
  "session_token": "eyJ..."   // From page 1 response
}
```

**Benefits of Session Token:**
- 6x faster (skips company query)
- Consistent results (same companies across all pages)
- Recommended for all pagination

### Deep Pagination (Pages 20+)

For pages beyond 20, use cursor-based pagination:

**Page 21:**
```json
{
  "cursor": "eyJ...",  // From page 20 response (next_cursor)
  "page_size": 25,
  "session_token": "eyJ..."
}
```

**Note:** Page number is ignored when cursor is provided.

---

## Examples

### Example 1: Find Senior Engineers at Tech Companies in SF

```json
{
  "company_criteria": {
    "industry": ["Information Technology & Services", "Computer Software"],
    "location_contains": "San Francisco"
  },
  "people_criteria": {
    "job_title": "Software Engineer",
    "location": "San Francisco",
    "seniority": ["senior"]
  },
  "page": 1,
  "page_size": 25
}
```

### Example 2: Find Managers at Mid-Sized Financial Services Companies

```json
{
  "company_criteria": {
    "industry": ["Financial Services"],
    "size": ["51_200", "201_500"],
    "location_country": "US"
  },
  "people_criteria": {
    "job_title": "Manager",
    "years_of_experience": ["10_15", "15"]
  },
  "page": 1,
  "page_size": 25
}
```

### Example 3: Find Healthcare Professionals in India

```json
{
  "company_criteria": {
    "industry": ["Hospital & Health Care"],
    "location_country": "IN"
  },
  "people_criteria": {
    "location": "India"
  },
  "page": 1,
  "page_size": 25
}
```

### Example 4: Direct Search (No Company Filter)

```json
{
  "company_criteria": {},  // Empty - triggers direct people search
  "people_criteria": {
    "job_title": "Data Scientist",
    "location": "United States",
    "skills": ["Python", "Machine Learning"]
  },
  "page": 1,
  "page_size": 25
}
```

**Response:** `search_mode: "direct"` (faster, no company filtering)

---

## Error Handling

### Validation Errors (HTTP 422)

```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "page_size"],
      "msg": "Input should be greater than or equal to 10",
      "input": 5
    }
  ]
}
```

**Common Validation Errors:**
- Page size < 10 or > 50
- Page number < 1 or > 20 (without cursor)
- Invalid field types

### Empty Results (HTTP 200)

```json
{
  "status": "success",
  "results": [],
  "metadata": {
    "companies_matched": 0,
    "profiles_matched": 0,
    "suggestion": "No companies matched your criteria. Try broadening company filters."
  }
}
```

**Causes:**
- No companies match company criteria
- Industry name doesn't exist in data
- Filters too restrictive

### Server Errors (HTTP 500)

```json
{
  "detail": "Search error: <error message>"
}
```

**Causes:**
- OpenSearch timeout
- OpenSearch connection error
- Internal service error

### Session Token Errors (HTTP 200)

```json
{
  "status": "error",
  "error": "invalid_token",
  "message": "Token expired. Tokens are valid for 60 minutes."
}
```

**Causes:**
- Token expired (>1 hour old)
- Token tampered with
- Token doesn't match current search criteria

---

## Performance

### Query Times

**Cold Start (First Request):**
- 2-4 seconds (Lambda initialization)

**Warm Requests:**
- Page 1 (with company query): 500-1,500ms
- Page 2+ (with session token): 200-500ms (6x faster!)
- Direct search (no companies): 300-800ms

**Factors Affecting Speed:**
- Number of companies matched
- Number of profiles matched
- Complexity of filters
- Lambda warm/cold state

### Optimization Tips

1. **Use specific company filters** to reduce company count
   - Add `location_country`
   - Add `size` ranges
   - Add `founded_after`

2. **Use session tokens** for pagination
   - Saves 500-1,000ms per request
   - Ensures consistent results

3. **Limit page size** for faster responses
   - 10-15: Fastest (<300ms)
   - 25: Balanced (<500ms)
   - 50: Slowest (<800ms)

---

## Rate Limits

**Current:** No rate limiting (Lambda Function URL)

**Recommended for Production:**
- Add API Gateway in front
- Set rate limit: 60 requests/minute per API key
- Burst: 1000 requests/second
- Throttle after limits exceeded

---

## Best Practices

### 1. Always Use Session Tokens

**Don't do this:**
```javascript
// BAD: Re-query companies for each page
for (let page = 1; page <= 10; page++) {
  const response = await fetch(url, {
    body: JSON.stringify({company_criteria: {...}, page})
  });
}
```

**Do this:**
```javascript
// GOOD: Use session token from page 1
const page1 = await fetch(url, {body: JSON.stringify({...})});
const token = page1.pagination.session_token;

for (let page = 2; page <= 10; page++) {
  const response = await fetch(url, {
    body: JSON.stringify({
      company_criteria: {...},
      page,
      session_token: token  // Reuse token
    })
  });
}
```

### 2. Start with Specific Filters

**Don't:**
```json
{
  "company_criteria": {"industry": ["Financial Services"]},
  // Result: 795,324 companies matched
}
```

**Do:**
```json
{
  "company_criteria": {
    "industry": ["Financial Services"],
    "location_country": "US",
    "size": ["51_200"]
  }
  // Result: ~50,000 companies (more manageable)
}
```

### 3. Handle Empty Results Gracefully

```javascript
if (response.metadata.companies_matched === 0) {
  // No companies matched
  // Show suggestion to user
  console.log(response.metadata.suggestion);
}
```

### 4. Use Appropriate Page Sizes

- **Mobile:** `page_size: 10-15` (fast loading)
- **Desktop:** `page_size: 25` (standard)
- **Data export:** `page_size: 50` (fewer requests)

---

## Code Examples

### Python

```python
import requests

api_url = "https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential"

# Search request
payload = {
    "company_criteria": {
        "industry": ["Information Technology & Services"],
        "size": ["51_200"],
        "location_country": "US"
    },
    "people_criteria": {
        "job_title": "Software Engineer",
        "seniority": ["senior"],
        "skills": ["Python"]
    },
    "page": 1,
    "page_size": 25
}

# Make request
response = requests.post(api_url, json=payload)
data = response.json()

# Process results
if data['status'] == 'success':
    print(f"Found {data['metadata']['profiles_matched']:,} profiles")
    print(f"Companies filtered: {data['metadata']['companies_used']}")

    for profile in data['results']:
        print(f"- {profile['fullName']}")
        print(f"  Title: {profile['headline']}")
        print(f"  Company: {profile['current_company_extracted']}")
        print()

    # For page 2, use session token
    session_token = data['pagination']['session_token']
else:
    print(f"Error: {data.get('message')}")
```

### JavaScript/Node.js

```javascript
const apiUrl = "https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential";

async function searchPeople() {
  const payload = {
    company_criteria: {
      industry: ["Financial Services"],
      location_country: "US"
    },
    people_criteria: {
      job_title: "Manager",
      seniority: ["senior"]
    },
    page: 1,
    page_size: 25
  };

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (data.status === 'success') {
    console.log(`Found ${data.metadata.profiles_matched} profiles`);

    data.results.forEach(profile => {
      console.log(`${profile.fullName} - ${profile.headline}`);
    });

    // Save session token for page 2
    return data.pagination.session_token;
  }
}

// Get page 2 with token
async function getPage2(sessionToken) {
  const payload = {
    company_criteria: {industry: ["Financial Services"]},
    people_criteria: {job_title: "Manager"},
    page: 2,
    page_size: 25,
    session_token: sessionToken  // Use token from page 1
  };

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });

  return response.json();
}
```

### cURL

```bash
# Page 1
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Financial Services"]
    },
    "people_criteria": {
      "seniority": ["senior"]
    },
    "page": 1,
    "page_size": 25
  }' > page1.json

# Extract session token
TOKEN=$(cat page1.json | jq -r '.pagination.session_token')

# Page 2 with token
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d "{
    \"company_criteria\": {\"industry\": [\"Financial Services\"]},
    \"people_criteria\": {\"seniority\": [\"senior\"]},
    \"page\": 2,
    \"page_size\": 25,
    \"session_token\": \"$TOKEN\"
  }"
```

---

## FAQ

### Q: Why did my query return 0 results?

**A:** Check these common issues:
1. **Wrong industry name:** Use exact values (e.g., "Information Technology & Services", not "Technology")
2. **Filters too restrictive:** Try removing some filters
3. **Check suggestion:** Response includes refinement suggestions

### Q: Can I get ALL companies, not just top 200?

**A:** No. The API limits to top 200 companies (scored by size/followers) for performance. This is intentional and best practice. If you need different companies, refine your filters.

### Q: Why is page 1 slower than page 2?

**A:** Page 1 queries both companies and people. Page 2+ with session token skips the company query (6x faster). This is expected and optimal behavior.

### Q: What happens if I don't provide company criteria?

**A:** The API automatically falls back to "direct" search mode - it queries people directly without company filtering. Faster but broader results.

### Q: Can I jump to page 50 directly?

**A:** No. Pages 1-20 support direct page numbers. For pages >20, you must use cursor-based pagination (get cursor from previous page).

### Q: How long are session tokens valid?

**A:** 1 hour. After that, you'll get a token expiration error and need to restart from page 1.

---

## Support

**Documentation:** `/Users/gauravluhariwala/linkedin-sequential-api/`
**Test Suite:** `/tmp/comprehensive_api_tests.py`
**Deployment:** `/tmp/PRODUCTION_API_DEPLOYED.md`

**Lambda Function:**
- Name: `linkedin-sequential-api`
- Region: `us-east-1`
- Logs: `/aws/lambda/linkedin-sequential-api`

---

## Changelog

### v1.0.0 (October 19, 2025)
- ✅ Initial production release
- ✅ Sequential company → people search
- ✅ Session tokens for pagination
- ✅ Field filtering (optimized payloads)
- ✅ Company scoring (top 200)
- ✅ Smart fallback to direct search
- ✅ Comprehensive error handling
- ✅ 19/20 tests passed

---

**API is live and ready for production use!** 🚀
