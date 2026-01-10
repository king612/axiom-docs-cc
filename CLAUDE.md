# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Axiom Intelligent Proposal Assistant** - A file system-based agent that analyzes historical Excel bid spreadsheets from a construction company to find similar past proposals for new bids. The system uses ML/AI to match new project parameters against ~5000 historical bid documents spanning 2016-2025.

## Technology Stack

- **Python**: 3.12
- **Backend**: Flask or FastAPI (simple, minimal dependencies)
- **Frontend**: React (JavaScript, not TypeScript), Bootstrap styling only
- **Vector Database**: ChromaDB
- **Embeddings**: Local (sentence-transformers)
- **LLM API**: Anthropic Claude (API key available)
- **Document Indexing**: LlamaIndex

## Data Structure

Historical bid spreadsheets are located in: `data/estimates/<year>/`

Each year folder contains:
- `Proposals New` (or variations like `proposals new`, `Proposal New`)
- `Proposals Approved`

### File Versioning Convention

Only use the **latest version** of each spreadsheet:

1. **Major version** (alphabetical): Last letter in project ID
   - `P22-003B` is newer than `P22-003A`

2. **Minor version** (numerical): Number at end of filename
   - `P22-003B ABS Tracy.3.xlsx` is newer than `P22-003B ABS Tracy.2.xlsx`

3. **Version folders**: Files in `.versions/` subfolders are older versions - ignore them

### Training Data Location

Training labels exist within the spreadsheets themselves on the first tab in tables labeled:
- "past projects to compare"
- "Recent Proposals That are similar size and scope"

Project IDs in these tables correspond to historical bids chosen by domain experts. Spreadsheets with blank comparison tables cannot be used for training.

## Key Fields for Similarity Matching

Extract from first tab of spreadsheets:
- `total # of shts.` (Total sheets - integer)
- `Total Engineering Hrs.` (float)
- `Total Drafting Hrs.` (float)
- `Total Manager/Reviewer Hrs.` (float)
- `CD Fee` (currency)
- `CA Fee` (currency)
- `SQ FT` (integer)
- `Total $ spent CD` (currency)
- `Total $ spent CA` (currency)

Fields may be missing in some spreadsheets. Favor more recent bids during training.

## MVP Requirements

1. Web UI to input project parameters and search for 3-10 similar historical bids
2. Output: List of similar past project Excel filenames for human review
3. Single-user initially (multi-user auth deferred)
4. Prioritize match quality over speed

## Future Considerations

- Egnyte integration for remote file access
- Project management data integration (contracts awarded, schedule milestones, cost overruns, profitability, change orders)
- RAG for additional document types (*.doc, *.pdf)
- Server deployment (currently local development)

## Commands

### Backend Setup
```bash
# Setup Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY

# Ingest data into vector store (run once, or after data changes)
python scripts/ingest_data.py --clear

# Run backend development server (port 5001, changed from 5000 to avoid macOS AirPlay conflict)
python -m backend.app
```

### Frontend Setup
```bash
cd frontend
npm install

# Run frontend development server (port 3000)
npm start
```

### API Endpoints (http://localhost:5001)
- `GET  /api/health` - Health check
- `GET  /api/stats` - Vector store statistics
- `POST /api/search` - Search for similar projects
- `POST /api/ingest` - Trigger re-ingestion
- `GET  /api/project/<id>` - Get project details

## Project Structure

```
backend/
├── app.py              # Flask application entry point
├── config.py           # Configuration and environment variables
├── api/
│   └── routes.py       # REST API endpoints
├── db/
│   └── vector_store.py # ChromaDB interface
├── models/
│   └── project.py      # Data models (Project, ProjectFeatures, SearchResult)
└── services/
    ├── excel_parser.py    # Excel spreadsheet parsing
    ├── version_resolver.py # File version resolution
    ├── ingestion.py       # Data ingestion pipeline
    └── similarity.py      # Similarity search engine

frontend/
├── package.json
├── public/
│   └── index.html
└── src/
    ├── index.js         # React entry point
    ├── index.css        # Global styles
    ├── App.js           # Main application component
    ├── components/
    │   ├── Header.js        # Logo and title
    │   ├── SearchForm.js    # Search input form
    │   ├── ResultsList.js   # Search results display
    │   └── LoadingSpinner.js
    └── services/
        └── api.js       # Backend API client
```
