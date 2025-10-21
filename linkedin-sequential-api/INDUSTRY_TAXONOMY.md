# Company Industry Taxonomy - Complete Reference

**Total Industries:** 148 unique values
**Total Companies:** 54,404,808
**Date Generated:** October 19, 2025

---

## Complete Industry List

### Top 50 Industries (by company count)

| # | Industry Name | Companies |
|---|---------------|-----------|
| 1 | *(empty/null)* | 10,868,136 |
| 2 | Real Estate | 2,578,041 |
| 3 | Medical Practice | 2,238,734 |
| 4 | Construction | 2,221,703 |
| 5 | Retail | 1,870,171 |
| 6 | **Information Technology & Services** | **1,668,978** |
| 7 | **Computer Software** | **1,527,551** |
| 8 | Management Consulting | 1,474,961 |
| 9 | Marketing & Advertising | 1,292,113 |
| 10 | Individual & Family Services | 1,222,575 |
| 11 | Restaurants | 1,169,841 |
| 12 | Hospital & Health Care | 954,263 |
| 13 | **Financial Services** | **795,324** |
| 14 | Health, Wellness & Fitness | 751,219 |
| 15 | Civic & Social Organization | 730,519 |
| 16 | Hospitality | 631,940 |
| 17 | Non-profit Organization Management | 592,553 |
| 18 | Transportation/Trucking/Railroad | 501,027 |
| 19 | Food & Beverages | 493,999 |
| 20 | Consumer Goods | 489,361 |
| 21 | Consumer Services | 486,702 |
| 22 | Electrical & Electronic Manufacturing | 482,616 |
| 23 | **Internet** | **478,731** |
| 24 | Facilities Services | 474,685 |
| 25 | Automotive | 469,582 |
| 26 | Sports | 455,551 |
| 27 | Higher Education | 446,465 |
| 28 | Accounting | 415,423 |
| 29 | Education Management | 411,164 |
| 30 | Design | 407,444 |
| 31 | Architecture & Planning | 406,022 |
| 32 | Wholesale | 395,093 |
| 33 | Professional Training & Coaching | 385,816 |
| 34 | Farming | 373,551 |
| 35 | Machinery | 371,415 |
| 36 | Apparel & Fashion | 368,921 |
| 37 | Mechanical Or Industrial Engineering | 363,014 |
| 38 | Food Production | 362,489 |
| 39 | Insurance | 354,834 |
| 40 | Law Practice | 317,223 |
| 41 | Leisure, Travel & Tourism | 311,899 |
| 42 | Entertainment | 309,619 |
| 43 | Mining & Metals | 300,188 |
| 44 | Legal Services | 296,071 |
| 45 | Performing Arts | 283,357 |
| 46 | Business Supplies & Equipment | 283,108 |
| 47 | Media Production | 277,064 |
| 48 | Events Services | 275,491 |
| 49 | E-learning | 263,146 |
| 50 | Government Administration | 260,985 |

*[See complete list in /tmp/ALL_INDUSTRIES.txt for all 148 industries]*

---

## Industry Categories

### Technology (11 industries, 4.7M companies)

**Most Common:**
- Information Technology & Services: 1,668,978
- Computer Software: 1,527,551
- Internet: 478,731
- Information Services: 120,893
- Computer Games: 69,584
- Computer & Network Security: 64,768
- Computer Hardware: 41,112
- Computer Networking: 26,671

**Use for tech companies:**
```json
"industry": [
  "Information Technology & Services",
  "Computer Software",
  "Internet"
]
```

---

### Financial Services (6 industries, 1.6M companies)

**All Financial:**
- Financial Services: 795,324
- Insurance: 354,834
- Investment Management: 201,052
- Banking: 122,531
- Investment Banking: 76,113
- Venture Capital & Private Equity: 70,569

**Use for financial companies:**
```json
"industry": [
  "Financial Services",
  "Banking",
  "Investment Banking"
]
```

---

### Healthcare (7 industries, 5.0M companies)

**All Healthcare:**
- Medical Practice: 2,238,734
- Hospital & Health Care: 954,263
- Health, Wellness & Fitness: 751,219
- Medical Device: 175,771
- Mental Health Care: 126,649
- Pharmaceuticals: 110,369
- Biotechnology: 90,916

**Use for healthcare:**
```json
"industry": [
  "Hospital & Health Care",
  "Medical Practice"
]
```

---

### Professional Services (5 industries, 2.7M companies)

- Management Consulting: 1,474,961
- Accounting: 415,423
- Legal Services: 296,071
- Human Resources: 254,115
- Staffing & Recruiting: 254,029

---

### Manufacturing (Multiple industries, ~2M companies)

- Electrical & Electronic Manufacturing: 482,616
- Automotive: 469,582
- Machinery: 371,415
- Mechanical Or Industrial Engineering: 363,014
- Chemicals: 142,396

---

### Retail & Consumer (9 industries, 5.7M companies)

- Retail: 1,870,171
- Restaurants: 1,169,841
- Food & Beverages: 493,999
- Consumer Goods: 489,361
- Consumer Services: 486,702
- Wholesale: 395,093
- Apparel & Fashion: 368,921
- Food Production: 362,489

---

### Real Estate & Construction (5 industries, 5.4M companies)

- Real Estate: 2,578,041
- Construction: 2,221,703
- Architecture & Planning: 406,022
- Civil Engineering: 168,283
- Commercial Real Estate: 55,640

---

## API Usage Examples

### Find Software Engineers
```json
{
  "company_criteria": {
    "industry": [
      "Information Technology & Services",
      "Computer Software",
      "Internet"
    ]
  },
  "people_criteria": {
    "job_title": "Software Engineer"
  }
}
```

### Find Financial Analysts
```json
{
  "company_criteria": {
    "industry": [
      "Financial Services",
      "Investment Banking",
      "Banking"
    ]
  },
  "people_criteria": {
    "job_title": "Analyst",
    "seniority": ["senior"]
  }
}
```

### Find Healthcare Professionals
```json
{
  "company_criteria": {
    "industry": [
      "Hospital & Health Care",
      "Medical Practice",
      "Pharmaceuticals"
    ]
  },
  "people_criteria": {
    "location": "United States"
  }
}
```

---

## Important Notes

### ⚠️ Industry Names Must Be EXACT

**Wrong:**
- "Technology" ❌ (returns 0)
- "Tech" ❌ (returns 0)
- "IT" ❌ (returns 0)

**Correct:**
- "Information Technology & Services" ✅
- "Computer Software" ✅
- "Internet" ✅

### ⚠️ Case-Sensitive

All industry names are case-sensitive. Use exact capitalization.

### ⚠️ Special Characters

Some industries have special characters:
- "Venture Capital & Private Equity" (ampersand)
- "E-learning" (hyphen)
- "Marketing & Advertising" (ampersand)

Use exact strings from this document.

---

## Empty Industry Values

**10,868,136 companies (20%)** have empty/null industry values.

To exclude them:
```json
{
  "company_criteria": {
    "industry": ["Information Technology & Services"]
    // This automatically excludes empty industries
  }
}
```

To search ONLY empty industries:
- Not directly supported
- Workaround: Use very broad filters and manually filter results

---

## Complete List of All 148 Industries

*Available in: /tmp/ALL_INDUSTRIES.txt*

**Quick Reference - Top Industries by Category:**

**Technology:**
Information Technology & Services, Computer Software, Internet, Computer Hardware, Computer Networking, Computer Games, Computer & Network Security

**Finance:**
Financial Services, Banking, Investment Banking, Insurance, Investment Management, Venture Capital & Private Equity, Capital Markets

**Healthcare:**
Medical Practice, Hospital & Health Care, Health Wellness & Fitness, Pharmaceuticals, Medical Device, Biotechnology, Mental Health Care

**Professional Services:**
Management Consulting, Accounting, Legal Services, Law Practice, Human Resources, Staffing & Recruiting

**Manufacturing:**
Electrical & Electronic Manufacturing, Automotive, Machinery, Mechanical Or Industrial Engineering, Chemicals, Industrial Automation

**Retail:**
Retail, Restaurants, Food & Beverages, Consumer Goods, Apparel & Fashion, Wholesale, Supermarkets

**Real Estate:**
Real Estate, Construction, Architecture & Planning, Civil Engineering, Commercial Real Estate

**Media:**
Marketing & Advertising, Media Production, Publishing, Broadcast Media, Online Media, Entertainment, Performing Arts

**Education:**
Higher Education, Education Management, E-learning, Primary/Secondary Education, Research

**Other Major:**
Transportation/Trucking/Railroad, Oil & Energy, Utilities, Telecommunications, Government Administration

---

## Usage in API

**Single Industry:**
```json
"industry": ["Financial Services"]
```

**Multiple Industries:**
```json
"industry": [
  "Information Technology & Services",
  "Computer Software",
  "Internet"
]
```

**All Tech Companies:**
```json
"industry": [
  "Information Technology & Services",
  "Computer Software",
  "Internet",
  "Computer Hardware",
  "Computer & Network Security",
  "Telecommunications"
]
```

---

**For complete taxonomy including all fields, see API_DOCUMENTATION.md**

**Generated from:** 54,404,808 companies in linkedin-prod-companies index
**Last Updated:** October 19, 2025
