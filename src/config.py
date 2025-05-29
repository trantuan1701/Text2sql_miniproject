from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

QDRANT_COLLECTION_NAME = "miniproject_vds"
MODEL_NAME = "gemini-2.0-flash"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_SIZE = 384