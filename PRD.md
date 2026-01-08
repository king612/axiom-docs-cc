# Product Requirements Document (PRD)

## Axiom Intelligent Proposal Assistant

### Executive Summary

A web-based tool that helps proposal builders at a project-based construction company find similar historical bid proposals when creating new bids. The system analyzes ~5000 historical Excel bid spreadsheets (2016-2025) and uses ML/AI to recommend 3-10 similar past projects based on input parameters.

---

## Problem Statement

Proposal builders currently manually search through years of historical bid spreadsheets to find comparable past projects. This process is time-consuming and relies heavily on institutional knowledge. A systematic approach using AI/ML can improve consistency and efficiency.

---

## User Persona

**Primary User**: Proposal Builder
- Experienced in construction estimating
- Has access to historical bid library
- Needs to quickly identify relevant past projects for reference
- Values accuracy over speed

---

## MVP Features

### 1. Search Interface

**Page Title**: "Axiom Intelligent Proposal Assistant" (large, bold, centered)

**Company Logo**: Display logo from https://axiompllc.com

**Form Label**: "Search for recent proposals of similar size and scope"

**Input Fields** (all optional - partial searches supported):

| Field | Type | Format | Required |
|-------|------|--------|----------|
| Total sheets | Integer | Numeric input | No |
| Total Engineering Hrs. | Float | Decimal input | No |
| Total Drafting Hrs. | Float | Decimal input | No |
| Total Manager/Reviewer Hrs. | Float | Decimal input | No |
| CD Fee | Currency | Dollar format | No |
| CA Fee | Currency | Dollar format | No |
| SQ FT | Integer | Numeric input | No |
| Total $ spent CD | Currency | Dollar format | No |
| Total $ spent CA | Currency | Dollar format | No |

Users may leave fields blank; the system will match based on provided fields only.

**Result Limit Control**:
- Dropdown: "Maximum historical bids"
- Values: 1-10
- Default: 5

**Action**: "Search" button at bottom

### 2. Search Results

**Output**: Ranked list of similar past project Excel filenames
- Results ordered by similarity score (best matches first)
- Display similarity score alongside each filename
- Maximum: 10 results (user-configurable via dropdown)
- May return fewer results if limited similar projects exist

---

## UI Constraints

- **Framework**: React (not React Native)
- **Language**: JavaScript only (no TypeScript)
- **Styling**: Bootstrap only (no Tailwind, no Material UI)

---

## Data Requirements

### Source Data Location
```
data/estimates/<year>/
├── Proposals New/
├── Proposals Approved/
└── [other folders - ignore]
```

### File Versioning Rules

Only process the latest version of each spreadsheet:

1. **Major version**: Alphabetical suffix in project ID
   - `P22-003B` supersedes `P22-003A`

2. **Minor version**: Numeric suffix before extension
   - `filename.3.xlsx` supersedes `filename.2.xlsx`

3. **Exclude**: All files in `.versions/` subfolders

### Training Data

Located within spreadsheets on first tab:
- Section: "past projects to compare"
- Section: "Recent Proposals That are similar size and scope"

Project IDs listed reference historical bids selected by domain experts as good comparisons. Spreadsheets with blank comparison sections are excluded from training.

**Training Algorithm Requirements:**
- Detect patterns from expert-labeled training data
- Apply recency bias: favor more recent bids in similarity rankings
- Use all available training examples (no minimum threshold)

---

## Non-Functional Requirements

### MVP Scope
- Single-user (no authentication)
- Local deployment for development/testing
- Internet access available for API calls

### Quality vs Performance
- Prioritize match quality over response time
- No hard latency requirements

### Deferred Features
- Multi-user authentication
- Server deployment
- Egnyte integration
- Project management data integration

---

## Success Metrics

1. System returns relevant similar projects (validated by domain expert review)
2. Results include projects that domain experts would have manually selected
3. Reduces time to identify comparable historical bids

---

## Technical Dependencies

- Python 3.12
- ChromaDB for vector storage
- Local embeddings (sentence-transformers)
- Anthropic Claude API
- LlamaIndex for document indexing

---

## Resolved Design Decisions

| Question | Decision |
|----------|----------|
| Partial field matches? | Yes - all input fields are optional; system matches on provided fields only |
| Result ranking? | Best matches first by similarity score; training algorithm detects patterns while favoring recency |
| Display similarity scores? | Yes - show score alongside each result filename |
| Fewer than 3 results available? | Acceptable - return whatever matches exist using available training data |
