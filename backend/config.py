import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data" / "estimates"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", BASE_DIR / "chroma_db"))

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Flask
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers model
EMBEDDING_DIMENSION = 384

# Search settings
DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 10
MIN_RESULTS = 1

# Feature weights for combined fields (initial values, can be tuned)
FEATURE_WEIGHTS = {
    "total_sheets": 1.0,  # Used for training but not in UI
    "total_hours": 1.0,   # Engineering + Drafting + Manager hours
    "total_fee": 1.0,     # SD + DD + CD fee
    "sq_ft": 1.0,
    "total_spent": 1.0,   # SD + DD + CD spent
}

# Recency bias weight (0-1, higher = more recent preference)
RECENCY_WEIGHT = 0.1

# ChromaDB collection name
COLLECTION_NAME = "axiom_proposals"
