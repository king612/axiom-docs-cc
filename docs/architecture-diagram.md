# Axiom Intelligent Proposal Assistant - System Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#DBEAFE', 'primaryTextColor': '#1E293B', 'primaryBorderColor': '#3B82F6', 'lineColor': '#6366F1', 'secondaryColor': '#FEF3C7', 'secondaryTextColor': '#1E293B', 'tertiaryColor': '#D1FAE5', 'tertiaryTextColor': '#1E293B', 'background': '#FFFFFF', 'mainBkg': '#FFFFFF', 'nodeBorder': '#334155', 'clusterBkg': '#F1F5F9', 'clusterBorder': '#94A3B8', 'titleColor': '#1E293B', 'nodeTextColor': '#1E293B', 'textColor': '#1E293B'}}}%%

flowchart TB
    subgraph DataSources["📁 Historical Data (2016-2024)"]
        direction TB
        Excel[("📊 ~1,200 Excel<br/>Bid Spreadsheets")]
        Labels["🏷️ Expert Labels<br/><i>'Similar Projects' tables</i><br/><small>449 labeled samples</small>"]
    end

    subgraph Ingestion["⚙️ Ingestion Pipeline"]
        direction TB
        VersionResolver["🔄 Version Resolver<br/><small>Latest versions only<br/>P22-003B > P22-003A</small>"]
        ExcelParser["📑 Excel Parser<br/><small>Extract features from<br/>first tab</small>"]

        subgraph Features["📐 Extracted Features"]
            direction LR
            F1["Square Feet"]
            F2["Total Hours<br/><small>Eng + Draft + Mgr</small>"]
            F3["Total Fee<br/><small>CD + CA</small>"]
            F4["Total Spent<br/><small>CD + CA</small>"]
            F5["Total Sheets"]
        end
    end

    subgraph Embeddings["🧠 Embedding Generation"]
        direction TB
        SentenceTransformer["🤖 SentenceTransformer<br/><b>all-MiniLM-L6-v2</b><br/><small>384-dim vectors</small>"]
        TextRep["📝 Text Representation<br/><small>Project ID + Features</small>"]
    end

    subgraph Storage["💾 Vector Store"]
        direction TB
        ChromaDB[("🗄️ ChromaDB<br/><b>axiom_proposals</b><br/><small>Persistent local storage</small>")]
        Metadata["📋 Metadata<br/><small>All features + labels<br/>+ file paths</small>"]
    end

    subgraph SearchEngine["🔍 Similarity Engine"]
        direction TB

        subgraph Scoring["Combined Scoring"]
            EmbedScore["📊 Embedding<br/>Similarity<br/><small>40% weight</small>"]
            FeatureScore["📐 Feature<br/>Similarity<br/><small>50% weight</small>"]
            RecencyScore["📅 Recency<br/>Bias<br/><small>10% weight</small>"]
        end

        Normalization["⚖️ Feature Normalization<br/><small>Min-max scaling</small>"]
        Ranking["🏆 Re-ranking & Fusion"]
    end

    subgraph Backend["🖥️ Flask Backend (Port 5001)"]
        direction TB
        API["🔌 REST API"]

        subgraph Endpoints["API Endpoints"]
            E1["/api/search"]
            E2["/api/stats"]
            E3["/api/health"]
            E4["/api/project/:id"]
        end
    end

    subgraph Frontend["🌐 React Frontend (Port 3000)"]
        direction TB
        UI["🎨 Bootstrap UI"]

        subgraph Components["Components"]
            SearchForm["📝 Search Form<br/><small>4 input fields</small>"]
            Results["📋 Results List<br/><small>Ranked matches</small>"]
            Stats["📊 Stats Display"]
        end
    end

    subgraph Training["🎯 Training & Validation"]
        direction TB
        ExpertLabels["👨‍💼 Expert Labels<br/><small>From spreadsheet tables:<br/>'Past projects to compare'</small>"]
        Validation["✅ Match Quality<br/>Validation<br/><small>Compare predictions<br/>vs expert picks</small>"]
    end

    %% Data Flow
    Excel --> VersionResolver
    Labels --> ExpertLabels
    VersionResolver --> ExcelParser
    ExcelParser --> Features
    Features --> TextRep
    TextRep --> SentenceTransformer
    SentenceTransformer --> ChromaDB
    Features --> Metadata
    Metadata --> ChromaDB

    %% Search Flow
    SearchForm --> API
    API --> E1
    E1 --> Normalization
    ChromaDB --> EmbedScore
    Normalization --> FeatureScore
    EmbedScore --> Ranking
    FeatureScore --> Ranking
    RecencyScore --> Ranking
    Ranking --> Results

    %% Training Flow
    ExpertLabels -.->|"Ground truth"| Validation
    Ranking -.->|"Predictions"| Validation
    Validation -.->|"Tune weights"| Scoring

    %% Stats Flow
    ChromaDB --> E2
    E2 --> Stats

    %% Styling
    classDef dataSource fill:#DBEAFE,stroke:#3B82F6,stroke-width:2px
    classDef processing fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px
    classDef storage fill:#D1FAE5,stroke:#10B981,stroke-width:2px
    classDef api fill:#EDE9FE,stroke:#8B5CF6,stroke-width:2px
    classDef ui fill:#FCE7F3,stroke:#EC4899,stroke-width:2px
    classDef training fill:#FFEDD5,stroke:#F97316,stroke-width:2px

    class Excel,Labels dataSource
    class VersionResolver,ExcelParser,Features,SentenceTransformer,TextRep processing
    class ChromaDB,Metadata storage
    class API,E1,E2,E3,E4 api
    class UI,SearchForm,Results,Stats ui
    class ExpertLabels,Validation training
```

## Component Details

### Data Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| Excel Spreadsheets | `.xlsx` files | Historical bid proposals (2016-2024) |
| Version Resolver | Python | Select latest version of each proposal |
| Excel Parser | `openpyxl` | Extract features from first tab |

### ML/AI Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| Embeddings | `sentence-transformers` | Generate 384-dim semantic vectors |
| Vector Store | ChromaDB | Persistent vector similarity search |
| Similarity Engine | Custom Python | Multi-factor ranking (embed + features + recency) |

### Application Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend API | Flask + CORS | REST endpoints for search & stats |
| Frontend | React + Bootstrap | User interface for searches |

### Training & Validation
| Component | Source | Purpose |
|-----------|--------|---------|
| Expert Labels | Spreadsheet tables | Ground truth for similar projects |
| Validation | Comparison | Measure prediction vs expert agreement |

## Data Flow Summary

1. **Ingestion**: Excel files → Version resolution → Feature extraction → Embedding → ChromaDB
2. **Search**: User input → API → Similarity scoring → Ranked results
3. **Training**: Expert labels from spreadsheets validate and tune similarity weights
