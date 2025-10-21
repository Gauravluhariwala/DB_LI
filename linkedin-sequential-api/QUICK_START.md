# Sequential Search API - Quick Start Guide

🚀 **API Endpoint:** https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential

---

## Common Use Cases

### 1. Find Senior Engineers at Tech Companies
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Information Technology & Services", "Computer Software"]
    },
    "people_criteria": {
      "job_title": "Engineer",
      "seniority": ["senior"]
    },
    "page": 1,
    "page_size": 25
  }'
```

### 2. Find Managers at Financial Services Companies in US
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Financial Services"],
      "location_country": "US"
    },
    "people_criteria": {
      "job_title": "Manager",
      "seniority": ["manager", "senior"]
    },
    "page": 1,
    "page_size": 25
  }'
```

### 3. Find Healthcare Professionals in India
```bash
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_criteria": {
      "industry": ["Hospital & Health Care"],
      "location_country": "IN"
    },
    "people_criteria": {
      "location": "India"
    },
    "page": 1,
    "page_size": 25
  }'
```

---

## Important Notes

### ✅ Industry Names Must Be EXACT

**Common Mistake:**
```json
"industry": ["Technology"]  // ❌ Returns 0 results
```

**Correct:**
```json
"industry": ["Information Technology & Services"]  // ✅ Returns 1.67M companies
```

**Get available industry values:**
See API_DOCUMENTATION.md for complete list of valid industry names.

### ✅ Always Use Session Tokens for Pagination

```javascript
// Get page 1
const page1 = await fetchPage1();
const token = page1.pagination.session_token;

// Get page 2 with token (6x faster!)
const page2 = await fetchPage2(token);
```

### ✅ Empty Company Criteria = Direct Search

```json
{
  "company_criteria": {},  // Empty = no company filter
  "people_criteria": {"job_title": "Engineer"}
}
// Searches ALL engineers, regardless of company
```

---

## Response Fields

**Essential fields returned** (optimized for performance):
- `publicId` - LinkedIn public ID
- `fullName` - Full name
- `headline` - Professional headline
- `current_company_extracted` - Current company name
- `locationName` - Location
- `locationCountry` - Country code
- `seniority_level` - Seniority (junior, mid_level, manager, senior, c_level)
- `total_experience_years` - Years of experience
- `skills` - Array of skills

**Fields NOT included** (excluded for performance):
- summary, recommendations, projects, certifications, previousCompanies

---

## Quick Reference

**Valid Industry Examples:**
- "Information Technology & Services"
- "Computer Software"
- "Financial Services"
- "Hospital & Health Care"
- "Real Estate"
- "Marketing & Advertising"

**Size Ranges:**
- "1_10", "11_50", "51_200", "201_500", "501_1000", "1000+"

**Seniority Levels:**
- "junior", "mid_level", "manager", "senior", "c_level"

**Page Size:**
- Min: 10
- Default: 25
- Max: 50

**Pagination:**
- Pages 1-20: Use page numbers
- Pages 20+: Use cursor from previous response

---

## Testing

**Test with:**
```bash
# Health check
curl https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/health

# Simple search
curl -X POST 'https://enxahgcmvx4yj7d645ygutnu6q0lfknk.lambda-url.us-east-1.on.aws/v1/search/sequential' \
  -H 'Content-Type: application/json' \
  -d '{"company_criteria":{"industry":["Financial Services"]},"people_criteria":{"seniority":["senior"]},"page":1,"page_size":10}'
```

---

**For complete documentation, see API_DOCUMENTATION.md**
