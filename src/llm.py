from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GEMINI_API_KEY, MODEL_NAME

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0,
    top_k=1,
    top_p=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key = GEMINI_API_KEY
)