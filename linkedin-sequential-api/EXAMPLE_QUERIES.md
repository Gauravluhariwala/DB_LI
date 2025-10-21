# Sequential Search API - Example Queries

**Production Endpoint:** https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential

---

## Basic Examples

### 1. Find Senior Professionals at Financial Services Companies

```bash
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
    "page_size": 15
  }' | python3 -m json.tool
```

**Expected:**
- Companies: ~795K matched
- Profiles: ~385K senior professionals
- Time: 500-1000ms

---

### 2. Find Engineers at Tech Companies in US

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Information Technology & Services", "Computer Software"],
      "location_country": "US"
    },
    "people_criteria": {
      "job_title": "Software Engineer",
      "seniority": ["senior", "mid_level"]
    },
    "page": 1,
    "page_size": 25
  }' | python3 -m json.tool
```

**Expected:**
- Companies: ~600K US tech companies
- Uses top 200
- Profiles: ~50K engineers
- Time: 600-900ms

---

### 3. Find Managers at Mid-Sized Companies

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "size": ["51_200", "201_500"],
      "industry": ["Marketing & Advertising"]
    },
    "people_criteria": {
      "job_title": "Manager",
      "seniority": ["manager", "senior"]
    },
    "page": 1,
    "page_size": 20
  }' | python3 -m json.tool
```

---

### 4. Find Healthcare Workers in India

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Hospital & Health Care", "Medical Practice"],
      "location_country": "IN"
    },
    "people_criteria": {
      "location": "India"
    },
    "page": 1,
    "page_size": 15
  }' | python3 -m json.tool
```

---

### 5. Direct Search (No Company Filter)

Find all Software Engineers in San Francisco, regardless of company:

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {},
    "people_criteria": {
      "job_title": "Software Engineer",
      "location": "San Francisco"
    },
    "page": 1,
    "page_size": 25
  }' | python3 -m json.tool
```

**Expected:**
- Search mode: "direct" (no company filtering)
- Time: 300-800ms (faster, single query)

---

## Advanced Examples

### 6. Startups Founded After 2015 with Experienced Engineers

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Computer Software", "Internet"],
      "founded_after": 2015,
      "size": ["11_50", "51_200"]
    },
    "people_criteria": {
      "job_title": "Engineer",
      "years_of_experience": ["10_15", "15"],
      "seniority": ["senior"]
    },
    "page": 1,
    "page_size": 20
  }' | python3 -m json.tool
```

---

### 7. Developers with Specific Skills at Small Companies

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Marketing & Advertising"],
      "size": ["1_10", "11_50"]
    },
    "people_criteria": {
      "job_title": "Developer",
      "skills": ["Python", "React"]
    },
    "page": 1,
    "page_size": 15
  }' | python3 -m json.tool
```

---

### 8. C-Level at Large Financial Institutions

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Financial Services", "Investment Banking"],
      "size": ["1000+"]
    },
    "people_criteria": {
      "seniority": ["c_level"],
      "years_of_experience": ["15"]
    },
    "page": 1,
    "page_size": 10
  }' | python3 -m json.tool
```

---

## Pagination Examples

### 9. Get Page 1 and Extract Session Token

```bash
# Get page 1
RESPONSE=$(curl -s -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {"industry": ["Financial Services"]},
    "people_criteria": {"seniority": ["senior"]},
    "page": 1,
    "page_size": 25
  }')

# Display results
echo "$RESPONSE" | python3 -m json.tool | head -50

# Extract session token for page 2
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['pagination']['session_token'])")
echo ""
echo "Session token: $TOKEN"
```

---

### 10. Get Page 2 with Session Token (6x Faster!)

```bash
# Use the token from page 1
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d "{
    \"company_criteria\": {\"industry\": [\"Financial Services\"]},
    \"people_criteria\": {\"seniority\": [\"senior\"]},
    \"page\": 2,
    \"page_size\": 25,
    \"session_token\": \"$TOKEN\"
  }" | python3 -m json.tool
```

**Expected:**
- Page 1 time: 500-1000ms
- Page 2 time: 200-400ms (6x faster!)
- Same company filter used

---

## Testing Different Industries

### 11. Real Estate Companies

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Real Estate"],
      "location_country": "US"
    },
    "people_criteria": {
      "job_title": "Agent"
    },
    "page": 1,
    "page_size": 15
  }'
```

---

### 12. Healthcare in Specific Location

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Hospital & Health Care"],
      "location_country": "IN"
    },
    "people_criteria": {
      "location": "Mumbai"
    },
    "page": 1,
    "page_size": 20
  }'
```

---

### 13. Retail Companies

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Retail"],
      "size": ["201_500", "501_1000"]
    },
    "people_criteria": {
      "job_title": "Manager",
      "seniority": ["manager"]
    },
    "page": 1,
    "page_size": 15
  }'
```

---

## Edge Case Testing

### 14. No Results (Invalid Industry)

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Unicorn Farming"]
    },
    "people_criteria": {
      "job_title": "Engineer"
    },
    "page": 1,
    "page_size": 10
  }'
```

**Expected:**
```json
{
  "status": "success",
  "results": [],
  "metadata": {
    "companies_matched": 0,
    "suggestion": "No companies matched your criteria..."
  }
}
```

---

### 15. Very Large Result Set

```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Real Estate"]
    },
    "people_criteria": {},
    "page": 1,
    "page_size": 50
  }'
```

**Expected:**
- 2.5M+ companies
- 500K+ profiles
- Suggestion to refine filters

---

## Response Parsing Examples

### 16. Extract Just Profile Names

```bash
curl -s -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {"industry": ["Financial Services"]},
    "people_criteria": {"seniority": ["c_level"]},
    "page": 1,
    "page_size": 10
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"{r['fullName']} - {r['headline']}\") for r in data['results']]"
```

---

### 17. Extract Metadata Only

```bash
curl -s -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {"industry": ["Computer Software"]},
    "people_criteria": {"job_title": "Engineer"},
    "page": 1,
    "page_size": 10
  }' | python3 -c "import sys, json; m=json.load(sys.stdin)['metadata']; print(f\"Companies: {m['companies_matched']:,}\\nProfiles: {m['profiles_matched']:,}\\nQuery time: {m['query_time_ms']}ms\\nMode: {m['search_mode']}\")"
```

---

### 18. Count Results Without Fetching All Data

```bash
curl -s -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {"industry": ["Banking"]},
    "people_criteria": {"seniority": ["senior"]},
    "page": 1,
    "page_size": 10
  }' | python3 -c "import sys, json; m=json.load(sys.stdin)['metadata']; print(f\"Total matches: {m['profiles_matched']:,} profiles at {m['companies_used']} companies\")"
```

---

## Quick Copy-Paste Tests

### Test 1: Quick Success Test
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' -H 'Content-Type: application/json' -d '{"company_criteria":{"industry":["Financial Services"]},"people_criteria":{"seniority":["senior"]},"page":1,"page_size":10}'
```

### Test 2: Tech Engineers
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' -H 'Content-Type: application/json' -d '{"company_criteria":{"industry":["Information Technology & Services"]},"people_criteria":{"job_title":"Engineer"},"page":1,"page_size":15}'
```

### Test 3: Healthcare India
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' -H 'Content-Type: application/json' -d '{"company_criteria":{"industry":["Hospital & Health Care"],"location_country":"IN"},"people_criteria":{"location":"India"},"page":1,"page_size":10}'
```

### Test 4: Direct Search
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' -H 'Content-Type: application/json' -d '{"company_criteria":{},"people_criteria":{"job_title":"Data Scientist","location":"United States"},"page":1,"page_size":10}'
```

---

## Health Check

```bash
curl -X GET 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/health'
```

**Expected:**
```json
{
  "status": "healthy",
  "opensearch": "connected",
  "timestamp": 1729534567.123
}
```

---

## Common Industry Values

Use these exact values (case-sensitive):

**Technology:**
- "Information Technology & Services"
- "Computer Software"
- "Internet"

**Finance:**
- "Financial Services"
- "Banking"
- "Investment Banking"

**Healthcare:**
- "Hospital & Health Care"
- "Medical Practice"
- "Pharmaceuticals"

**Business Services:**
- "Management Consulting"
- "Marketing & Advertising"
- "Accounting"

**Others:**
- "Real Estate"
- "Construction"
- "Retail"
- "Higher Education"

*Full list in INDUSTRY_TAXONOMY.md*

---

## Tips

1. **Always use exact industry names** (see INDUSTRY_TAXONOMY.md)
2. **Use session tokens** for pagination (6x faster)
3. **Start with specific filters** to reduce company count
4. **Check metadata.suggestion** for refinement ideas
5. **Direct search** (empty company_criteria) when you don't need company filtering

---

**For complete API reference, see API_DOCUMENTATION.md**
