import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# Qdrant options: remote (URL/API key) or local embedded path
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_PATH = os.getenv("QDRANT_PATH", os.path.abspath("qdrant_data"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")

# Chunking defaults
CHUNK_SIZE_CHARS = int(os.getenv("CHUNK_SIZE_CHARS", "1200"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "150"))
MAX_CHUNK_TOKENS = int(os.getenv("MAX_CHUNK_TOKENS", "700"))
OVERLAP_TOKENS = int(os.getenv("OVERLAP_TOKENS", "100"))

# GPT for Q/A generation
USE_GPT_QA = os.getenv("USE_GPT_QA", "true").lower() in {"1", "true", "yes"}
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
EXPOSE_ASK = os.getenv("EXPOSE_ASK")
if EXPOSE_ASK is None:
    EXPOSE_ASK = USE_GPT_QA
else:
    EXPOSE_ASK = EXPOSE_ASK.lower() in {"1", "true", "yes"}

# RAG answering
RAG_K = int(os.getenv("RAG_K", "5"))
RAG_MAX_CONTEXT_TOKENS = int(os.getenv("RAG_MAX_CONTEXT_TOKENS", "1600"))

# Storage
DATA_DIR = os.path.abspath(os.getenv("DATA_DIR", "data"))
DECKS_DIR = os.path.join(DATA_DIR, "decks")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DECKS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
