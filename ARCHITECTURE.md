# Architecture Document

## Axiom Intelligent Proposal Assistant

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              React Frontend                              │
│                    (Bootstrap, JavaScript, REST API)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Flask/FastAPI Backend                          │
│                                                                         │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  REST API   │  │ Similarity      │  │  Data Ingestion             │  │
│  │  Endpoints  │  │ Engine          │  │  Service                    │  │
│  └─────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌─────────────┐   ┌───────────────┐
            │ ChromaDB  │   │ LlamaIndex  │   │ Anthropic     │
            │ (Vectors) │   │ (Indexing)  │   │ Claude API    │
            └───────────┘   └─────────────┘   └───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      File System              │
                    │  data/estimates/<year>/       │
                    │    ├── Proposals New/         │
                    │    └── Proposals Approved/    │
                    └───────────────────────────────┘
```

---

## Component Architecture

### 1. Data Ingestion Service

**Responsibilities:**
- Scan `data/estimates/<year>/` directories
- Apply versioning rules to identify latest files
- Parse Excel spreadsheets (first tab only)
- Extract feature fields and training labels
- Generate embeddings and store in ChromaDB

**Version Resolution Algorithm:**
```python
# Pseudocode
def get_latest_version(files):
    # Group by base project ID (e.g., P22-003)
    groups = group_by_project_id(files)

    for project_id, versions in groups:
        # 1. Filter out files in .versions/ folders
        versions = [f for f in versions if '.versions' not in f.path]

        # 2. Sort by major version (A < B < C)
        versions.sort(key=lambda f: f.major_version, reverse=True)

        # 3. Among same major version, sort by minor version
        versions.sort(key=lambda f: f.minor_version, reverse=True)

        yield versions[0]  # Latest version
```

**Excel Parsing:**
- Library: `openpyxl` or `pandas`
- Target: First worksheet only
- Extract: Named fields (see Key Fields below)
- Training labels: Parse tables "past projects to compare" and "Recent Proposals That are similar size and scope"

### 2. Vector Store (ChromaDB)

**Collection Schema:**
```python
{
    "id": "P22-003B",  # Project ID
    "embedding": [...],  # 384-dim vector (sentence-transformers)
    "metadata": {
        "filename": "P22-003B ABS Tracy.xlsx",
        "filepath": "data/estimates/2022/proposals new/...",
        "year": 2022,
        "total_sheets": 15,
        "engineering_hrs": 120.5,
        "drafting_hrs": 80.0,
        "manager_hrs": 40.0,
        "cd_fee": 25000.00,
        "ca_fee": 15000.00,
        "sq_ft": 50000,
        "total_spent_cd": 22000.00,
        "total_spent_ca": 14000.00,
        "has_training_labels": True,
        "similar_projects": ["P21-045A", "P21-089B"]  # From training labels
    }
}
```

### 3. Similarity Engine

**Hybrid Approach:**

1. **Feature Vector Similarity** (Primary)
   - Normalize numeric fields to [0, 1] range
   - Compute weighted Euclidean distance
   - Weights learned from training data

2. **Embedding Similarity** (Secondary)
   - Project name/description embeddings via sentence-transformers
   - Cosine similarity in vector space

3. **Combined Score:**
   ```python
   final_score = α * feature_similarity + (1 - α) * embedding_similarity
   # α determined by training/validation
   ```

**Training Process:**
- Input: Spreadsheets with filled "past projects to compare" tables
- These tables contain project IDs manually selected by domain experts
- Use as ground truth for:
  - Learning feature weights
  - Validating similarity rankings
  - Tuning α parameter

### 4. LlamaIndex Integration

**Purpose:**
- Document indexing for future RAG expansion
- Unified interface for querying across document types
- Supports future integration of *.doc, *.pdf files

**MVP Usage:**
```python
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

# Connect LlamaIndex to ChromaDB
vector_store = ChromaVectorStore(chroma_collection=collection)
index = VectorStoreIndex.from_vector_store(vector_store)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("Find similar projects to...")
```

### 5. REST API Layer

**Framework:** Flask (simpler) or FastAPI (async, auto-docs)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Find similar projects |
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Dataset statistics |
| POST | `/api/ingest` | Trigger re-indexing |

**Search Request:**
```json
POST /api/search
{
    "total_sheets": 15,
    "engineering_hrs": 120.5,
    "drafting_hrs": 80.0,
    "manager_hrs": 40.0,
    "cd_fee": 25000.00,
    "ca_fee": 15000.00,
    "sq_ft": 50000,
    "total_spent_cd": 22000.00,
    "total_spent_ca": 14000.00,
    "max_results": 5
}
```

**Search Response:**
```json
{
    "results": [
        {
            "project_id": "P22-045A",
            "filename": "P22-045A Kirk Hotel Scope.xlsx",
            "similarity_score": 0.94
        },
        // ... more results
    ],
    "query_time_ms": 145
}
```

### 6. React Frontend

**Structure:**
```
src/
├── components/
│   ├── Header.jsx          # Logo + title
│   ├── SearchForm.jsx      # Input form
│   ├── ResultsList.jsx     # Display results
│   └── LoadingSpinner.jsx
├── services/
│   └── api.js              # API client
├── App.jsx
└── index.jsx
```

**Key Libraries:**
- `react-bootstrap` for UI components
- `axios` or `fetch` for API calls

---

## Data Flow

### Ingestion Flow
```
1. Scan directories → 2. Version resolution → 3. Parse Excel →
4. Extract features → 5. Generate embeddings → 6. Store in ChromaDB
```

### Query Flow
```
1. User input → 2. Validate/normalize → 3. Generate query embedding →
4. ChromaDB similarity search → 5. Re-rank by feature similarity →
6. Return top N results
```

---

## Directory Structure

```
axiom-docs-cc/
├── CLAUDE.md
├── PRD.md
├── ARCHITECTURE.md
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   └── estimates/           # Historical bid spreadsheets
│       ├── 2016/
│       ├── ...
│       └── 2025/
│
├── backend/
│   ├── __init__.py
│   ├── app.py               # Flask/FastAPI entry point
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion.py     # Data ingestion
│   │   ├── similarity.py    # Similarity engine
│   │   └── excel_parser.py  # Excel parsing
│   ├── models/
│   │   ├── __init__.py
│   │   └── project.py       # Data models
│   └── db/
│       ├── __init__.py
│       └── vector_store.py  # ChromaDB interface
│
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── components/
│       ├── services/
│       ├── App.jsx
│       └── index.jsx
│
├── scripts/
│   ├── ingest_data.py       # One-time data ingestion
│   └── train_model.py       # Train similarity weights
│
└── tests/
    ├── test_ingestion.py
    ├── test_similarity.py
    └── test_api.py
```

---

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend | Flask | Simpler, sufficient for MVP, easy to upgrade to FastAPI |
| Vector DB | ChromaDB | Local, no server setup, Python-native |
| Embeddings | sentence-transformers | Local, no API costs, good quality |
| LLM | Anthropic Claude | User preference, high quality |
| Frontend | React + Bootstrap | Per requirements |
| Excel Parser | openpyxl | Well-maintained, handles .xlsx |

---

## Future Extensibility

### Phase 2: Multi-Document RAG
- Index *.doc, *.pdf files alongside Excel
- Use LlamaIndex document loaders
- Cross-document semantic search

### Phase 3: Project Management Integration
- Ingest contract performance data
- Track: schedule milestones, cost overruns, profitability, change orders
- Correlate bid accuracy with project outcomes

### Phase 4: Server Deployment
- Containerize with Docker
- Deploy to cloud (AWS/GCP/Azure)
- Add authentication (OAuth/JWT)

### Phase 5: Egnyte Integration
- Replace local filesystem with Egnyte API
- Real-time sync of new documents
- Handle file locking/permissions

---

## Security Considerations

- Store API keys in environment variables (`.env`)
- No sensitive data in version control
- Sanitize file paths to prevent directory traversal
- Rate limiting on API endpoints (future)
- Authentication for multi-user deployment (future)

---

## Performance Considerations

- **Indexing**: One-time batch process, can be incremental for new files
- **Query latency**: ChromaDB is optimized for similarity search
- **Memory**: sentence-transformers model (~100MB), ChromaDB index scales with data
- **Caching**: Consider caching frequent queries (future optimization)
