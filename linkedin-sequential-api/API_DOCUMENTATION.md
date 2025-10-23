# LinkedIn Sequential Search API - Complete Documentation

**Production Endpoint:** https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/

**Version:** 1.2.1
**Status:** 🟢 LIVE IN PRODUCTION
**Last Updated:** October 22, 2025 (Enhanced with 15 new fields + Individual Profile Lookup!)

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Sequential Search](#sequential-search)
5. [Semantic Specialty Search](#semantic-specialty-search) ⭐ NEW
6. [Request Format](#request-format)
7. [Response Format](#response-format)
8. [Filter Reference](#filter-reference)
9. [Pagination](#pagination)
10. [Examples](#examples)
11. [Error Handling](#error-handling)
12. [Performance](#performance)
13. [Rate Limits](#rate-limits)
14. [Best Practices](#best-practices)

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
- ✅ **15 new essential fields** (name, education, previous company, etc.) ⭐ v1.2.0
- ✅ **Query performance optimization** (50-80% faster with track_total_hits) ⭐ v1.2.0
- ✅ **Semantic specialty search** (AI-powered vector similarity)
- ✅ **Query expansion** (find related specialties)
- ✅ Smart fallback (direct people search when no company criteria)
- ✅ Session tokens (6x faster pagination)
- ✅ Field filtering (70% smaller payloads)
- ✅ Company scoring (get top companies by size/followers)
- ✅ Optimized query times (1-10s with track_total_hits)

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

### Search Endpoints

#### 1. POST /v1/search/sequential

Main search endpoint for sequential company → people queries.

**Authentication:** None (public endpoint)
**Rate Limit:** Unlimited (add API Gateway for rate limiting)
**Timeout:** 29 seconds max

---

### Individual Profile Endpoints ⭐ NEW v1.2.1

#### 2. GET /v1/profiles/{publicId}

Fetch a single LinkedIn profile by its publicId.

**Authentication:** None (public endpoint)
**Returns:** Complete profile with ALL 36 fields

**Example:**
```
GET /v1/profiles/john-smith-12345
GET /v1/profiles/siri-chauhan-1b35a4221
```

**Query Parameter:**
- `include_fields` - Comma-separated list of fields (optional)

**Example with filtering:**
```
GET /v1/profiles/john-smith-12345?include_fields=publicId,fullName,headline,skills
```

#### 3. POST /v1/profiles/batch

Fetch multiple profiles (up to 100) in a single request.

**Request:**
```json
{
  "public_ids": ["id1", "id2", "id3"],
  "include_fields": ["publicId", "fullName", "headline"]
}
```

**Returns:**
```json
{
  "profiles": [...],
  "total_found": 2,
  "total_requested": 3,
  "not_found": ["id3"]
}
```

#### 4. GET /v1/profiles/search/by-name/{fullName}

Search profiles by exact full name (for name disambiguation).

**Example:**
```
GET /v1/profiles/search/by-name/John%20Smith?limit=10
```

**Use Case:** When multiple people have the same name

---

### Semantic Search Endpoints

#### 5. POST /v1/specialties/search

Semantic vector search for company specialties (AI-powered similarity matching).

**Authentication:** None (public endpoint)
**Rate Limit:** Unlimited
**Database:** 44,899 unique specialties from 54M companies

#### 6. POST /v1/specialties/expand

Expand a search term to include semantically similar specialties.

**Authentication:** None (public endpoint)
**Use Case:** Query expansion for better search recall

#### 7. GET /v1/specialties/stats

Get statistics about the specialty vector database.

**Authentication:** None (public endpoint)
**Returns:** Total count, collection info, status

---

## Sequential Search

See sections below for complete sequential search documentation.

---

## Semantic Specialty Search

**NEW in v1.1.0** - AI-powered semantic search for company specialties using Chroma Cloud vector database.

### Overview

The Specialty Search API uses **semantic embeddings** to find company specialties that are similar in meaning to your search query. Unlike keyword matching, semantic search understands context and relationships between terms.

**Example:**
- Search: `"AI"`
- Returns: `"AI"`, `"Artificial Intelligence"`, `"Machine Learning"`, `"Deep Learning"`

**Database:**
- **44,899 unique specialties**
- Extracted from **54 million companies**
- Powered by **Chroma Cloud**
- Embedding model: **all-MiniLM-L6-v2**

### POST /v1/specialties/search

Find specialties semantically similar to your query.

**Request:**
```json
{
  "query": "artificial intelligence",
  "n_results": 3,
  "min_count": 10,
  "sort_by_count": true
}
```

**Parameters:**
- `query` (required): Search term (e.g., "AI", "blockchain", "web development")
- `n_results` (optional): Number of results (default: 3, max: 50)
- `min_count` (optional): Minimum company count filter (e.g., 10 = only specialties with 10+ companies)
- `sort_by_count` (optional): Sort by company count DESC, then similarity DESC (default: true)

**Response:**
```json
{
  "query": "artificial intelligence",
  "results": [
    {
      "specialty": "AI",
      "count": 79,
      "rank": 23,
      "similarity_score": 1.0
    },
    {
      "specialty": "Artificial Intelligence",
      "count": 57,
      "rank": 47,
      "similarity_score": 0.5825
    },
    {
      "specialty": "Machine Learning",
      "count": 56,
      "rank": 48,
      "similarity_score": 0.0927
    }
  ],
  "total_results": 3,
  "metadata": {
    "total_specialties_in_db": 44899,
    "search_method": "semantic_vector_similarity",
    "embedding_model": "all-MiniLM-L6-v2"
  }
}
```

**Field Descriptions:**
- `specialty`: The specialty name
- `count`: Number of companies with this specialty
- `rank`: Popularity rank (1 = most common)
- `similarity_score`: Semantic similarity (0-1, where 1.0 = exact match)

### POST /v1/specialties/expand

Expand a search term to include related specialties for better search results.

**Request:**
```json
{
  "query": "machine learning",
  "expansion_count": 5
}
```

**Parameters:**
- `query` (required): Term to expand
- `expansion_count` (optional): Number of related terms (default: 5, max: 20)

**Response:**
```json
{
  "original_query": "machine learning",
  "expanded_terms": [
    "Machine Learning",
    "Machine Learning Algorithms",
    "Machine Learning Solutions",
    "AI/Machine learning",
    "Machine Learning Technologies"
  ],
  "count": 5
}
```

**Use Case:**
```javascript
// User searches for "AI companies"
const expanded = await expandQuery("AI");
// expanded_terms: ["AI", "Artificial Intelligence", "Machine Learning", ...]

// Now search companies with ANY of these specialties
// Result: 3-5x more companies found!
```

### GET /v1/specialties/stats

Get statistics about the specialty vector database.

**Request:**
```bash
curl https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/specialties/stats
```

**Response:**
```json
{
  "total_specialties": 44899,
  "database": "Tags",
  "collection": "company_specialties",
  "status": "active"
}
```

### Examples

**Example 1: Find AI-related specialties (popular ones only)**
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/specialties/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "AI",
    "n_results": 5,
    "min_count": 10
  }'
```

**Result:** Only AI specialties with 10+ companies, sorted by popularity

**Example 2: Find blockchain specialties (all variants)**
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/specialties/search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "blockchain",
    "n_results": 10,
    "sort_by_count": false
  }'
```

**Result:** Top 10 blockchain-related terms sorted by similarity (includes rare variants)

**Example 3: Expand "web development" for search**
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/specialties/expand' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "web development",
    "expansion_count": 7
  }'
```

**Result:**
```
["Web Development", "Web-Development", "Web Developing", "Website Development", ...]
```

### Performance

**Query Times:**
- Search: ~100-300ms
- Expand: ~100-200ms
- Stats: ~20-50ms

**Cold Start:** ~10 seconds (first request only)

**Optimization:** Chroma Cloud handles embedding caching automatically

---

## Request Format

### Schema (v1.2.0 - Enhanced!)

```typescript
{
  company_criteria: {
    // === BASIC FILTERS ===
    industry?: string[],                    // Industry names (exact match)
    size?: string[],                        // Size ranges
    founded_after?: number,                 // Year (>=)
    founded_before?: number,                // Year (<=)
    location_country?: string,              // Country code
    location_contains?: string,             // Location search
    revenue_min?: number,                   // Minimum revenue

    // === NEW in v1.2.0 ===
    company_name?: string[],                // Company names (OR logic, fuzzy match) ⭐ NEW
    specialties?: string[],                 // Company specialties/tags (OR logic) ⭐ NEW
    hq_city?: string[]                      // Headquarter cities (OR logic) ⭐ NEW
  },

  people_criteria: {
    // === BASIC FILTERS (Enhanced to arrays) ===
    job_title?: string[],                   // Job titles (OR logic, fuzzy) - Changed to array!
    location?: string[],                    // Locations (OR logic) - Changed to array!
    seniority?: string[],                   // Seniority levels
    years_of_experience?: string[],         // Experience ranges
    years_in_current_role?: string[],       // Current role duration
    skills?: string[],                      // Skills (OR logic)
    industry?: string[],                    // Industry

    // === NEW in v1.2.0 - Identity & Location ===
    name?: string[],                        // Names (OR logic, fuzzy match) ⭐ NEW
    location_country?: string[],            // Country codes (OR logic) ⭐ NEW

    // === NEW in v1.2.0 - Job Details ===
    current_title_extracted?: string[],     // Extracted titles (OR, more accurate) ⭐ NEW
    job_description_contains?: string,      // Keyword in job description ⭐ NEW
    job_location?: string[],                // Job location (OR, may differ from person) ⭐ NEW
    employment_type?: string[],             // Full-time/Part-time/Contract (OR) ⭐ NEW
    started_current_job_after?: number,     // Started job after year ⭐ NEW

    // === NEW in v1.2.0 - Education ===
    education_school?: string[],            // Schools (OR logic, fuzzy) ⭐ NEW
    education_degree?: string[],            // Degrees (OR logic, fuzzy) ⭐ NEW
    education_field?: string[],             // Fields of study (OR logic, fuzzy) ⭐ NEW
    graduated_after?: number,               // Graduated after year ⭐ NEW
    graduated_before?: number,              // Graduated before year ⭐ NEW

    // === NEW in v1.2.0 - Work History ===
    previous_company?: string[],            // Past employers (OR logic, fuzzy) ⭐ NEW

    // === NEW in v1.2.0 - Profile Content ===
    summary_contains?: string,              // Keyword in bio/summary ⭐ NEW

    // === NEW in v1.2.0 - Credentials ===
    certifications?: string[]               // Certifications (OR logic, fuzzy) ⭐ NEW
  },

  page: number,                             // Page number (1-20)
  page_size: number,                        // Results per page (10-50)
  session_token?: string,                   // For pages 2+ (from page 1 response)
  cursor?: string                           // For pages >20 (deep pagination)
}
```

### OR Logic Explanation

**All array fields use OR logic** for wider search results:

```json
{
  "education_school": ["Stanford", "Harvard", "IIT Delhi"]
}
```
**Means:** Find people who went to Stanford **OR** Harvard **OR** IIT Delhi

**To combine with AND logic**, use multiple different fields:
```json
{
  "education_school": ["Stanford"],
  "education_field": ["Computer Science"],
  "location_country": ["US"]
}
```
**Means:** Stanford **AND** CS **AND** US (all conditions must match)

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

### v1.2.1 (October 22, 2025) ⭐ NEW
- ✅ **Individual Profile Lookup** - GET /v1/profiles/{publicId}
- ✅ **Batch Profile Fetch** - POST /v1/profiles/batch (up to 100 profiles)
- ✅ **Search by Name** - GET /v1/profiles/search/by-name/{fullName}
- ✅ **ALL 36 Fields Returned** - Including courses, honors, patents, publications, etc.
- ✅ **Field Filtering** - Optional include_fields parameter
- ✅ **Production Ready** - Tested and deployed

### v1.2.0 (October 22, 2025) ⭐ MAJOR UPDATE
- ✅ **15 New Essential Fields** - Comprehensive search capabilities
- ✅ **Name Search** - Find people by name (fuzzy matching)
- ✅ **Education Filtering** - School, degree, field of study
- ✅ **Previous Company Search** - Find ex-employees
- ✅ **Location Country** - Country-level filtering (consistency fix)
- ✅ **Job Content Search** - Keywords in job descriptions & bios
- ✅ **Employment Type** - Filter by Full-time/Part-time/Contract
- ✅ **Certifications** - Professional credential filtering
- ✅ **Company Specialties** - Search by company tags/specialties
- ✅ **Array Enhancement** - job_title, location now support OR logic
- ✅ **Query Performance** - 50-80% faster with track_total_hits optimization
- ✅ **Results capped at 10K** - Faster queries, better UX
- ✅ **20/20 tests passed** - Production ready

### v1.1.0 (October 22, 2025)
- ✅ **Semantic Specialty Search** - AI-powered vector search for company specialties
- ✅ **Chroma Cloud Integration** - 44,899 specialties, all-MiniLM-L6-v2 embeddings
- ✅ **Query Expansion API** - Expand search terms with related specialties
- ✅ **Smart Filtering** - Filter by minimum company count
- ✅ **Intelligent Sorting** - Sort by popularity + similarity
- ✅ **Real Similarity Scores** - Distance-based scores (0-1)

### v1.0.0 (October 19, 2025)
- ✅ Initial production release
- ✅ Sequential company → people search
- ✅ Session tokens for pagination
- ✅ Field filtering (optimized payloads)
- ✅ Company scoring (top 200)
- ✅ Smart fallback to direct search
- ✅ Comprehensive error handling

---

**API is live and ready for production use!** 🚀

**Latest (v1.2.1):**
- 29 searchable fields with OR logic arrays
- Individual profile lookup with ALL 36 fields
- Batch profile fetch (up to 100 profiles)
- Search by name for disambiguation

---

## Individual Profile Lookup - Curl Examples

### Get Single Profile (All Fields)

```bash
curl https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/profiles/siri-chauhan-1b35a4221
```

**Returns:** Complete profile with ALL 37 fields

### Get Profile with Field Filtering

```bash
curl 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/profiles/siri-chauhan-1b35a4221?include_fields=publicId,fullName,headline,skills,educations'
```

**Returns:** Only specified fields (faster, smaller payload)

### Batch Profile Fetch

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/profiles/batch' \
  -H 'Content-Type: application/json' \
  -d '{
    "public_ids": ["siri-chauhan-1b35a4221", "tariq4nwar", "sana-begum-869b47292"],
    "include_fields": ["publicId", "fullName", "headline", "skills", "current_company_extracted"]
  }'
```

**Response:**
```json
{
  "profiles": [
    {"publicId": "...", "fullName": "...", ...},
    {"publicId": "...", "fullName": "...", ...}
  ],
  "total_found": 3,
  "total_requested": 3,
  "not_found": []
}
```

### Search by Name

```bash
curl 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/profiles/search/by-name/Kumar?limit=10'
```

**Returns:** Up to 10 people named "Kumar"

### All 37 Fields Included

When fetching a profile without field filtering, you get:

- **Basic:** publicId, fullName, firstName, lastName, headline, summary, pronoun, urn, logoUrl
- **Location:** locationName, locationCountry
- **Experience:** seniority_level, total_experience_years, total_experience_range, years_in_current_role, years_in_current_role_range, current_company_extracted, current_title_extracted
- **Network:** connectionsCount, followersCount, industry
- **Skills:** skills array
- **Education:** educations (school, degree, fieldOfStudy, years)
- **Work History:** currentCompanies, previousCompanies (with positions, descriptions, dates)
- **Credentials:** certifications, courses
- **Activities:** languages, projects, publications, patents, honors, recommendations, organizations, volunteerExperiences
- **Meta:** lastUpdated, _index

**Total: 37 fields** (everything from LinkedIn!)

---

---

## Version 1.3.2 (October 24, 2025) ⭐ CRITICAL BUG FIXES + NEW FEATURES

### Critical Bug Fixes:
- ✅ **Fixed location filter bug** - Now correctly returns ONLY specified locations
- ✅ **Fixed company_name bug** - Exact matches now prioritized (tiered: exact > phrase > fuzzy)
- ✅ **Fixed specialties bug** - Same tiered matching approach
- ✅ **Fixed has_company_filters** - Now includes all company filter fields
- ✅ **Fixed backwards results** - Removing filters now correctly increases results
- ✅ **Removed company limits** - Now uses ALL matching companies (was capped at 200-1000)
- ✅ **Removed alphabetical sorting** - Preserves relevance order from OpenSearch

### Performance Improvements:
- ✅ Company query: Now returns 3,204 results (was 364) - 76% match to LinkedIn!
- ✅ Removed track_total_hits caps for accurate counts
- ✅ All array filters now work correctly with nested bool queries

### New Funding Filters:
- ✅ `funding_round` - Filter by funding stage (27 types: Pre-seed, Seed, Series A-J)
- ✅ `lead_investor` - Filter by VC/investor name (fuzzy matching)
- ✅ `min_funding_rounds` - Minimum number of funding rounds
- ✅ `domain` - Filter by website domain (exact match)

### All Filters Now Working:
**Company Criteria (13 fields):**
- industry, size, founded_after, founded_before
- location_country, location_contains, revenue_min
- company_name, specialties, hq_city
- **funding_round, lead_investor, min_funding_rounds, domain** ⭐ NEW

**People Criteria (23 fields):**
- All existing filters working correctly with proper AND/OR logic

### Test Results:
- ✅ Screenshot query: 3,204 results (76% of LinkedIn's 4.2K)
- ✅ Y Combinator: 70,226 people at YC companies
- ✅ Ex-Google: 360,149 former Google employees
- ✅ Microsoft: 118,950 Microsoft employees
- ✅ All location filters return correct locations only

**This is a MAJOR stability and accuracy release!**

