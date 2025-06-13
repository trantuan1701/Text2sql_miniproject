from langchain.vectorstores import Qdrant
import qdrant_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import json
from src.config import EMBEDDING_MODEL, QDRANT_HOST, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, EMBEDDING_SIZE
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.qdrant import QdrantTranslator
from .llm import llm
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from typing import Optional, List
client = qdrant_client.QdrantClient(
    QDRANT_HOST, 
    api_key= QDRANT_API_KEY
)

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def load_vectordb(docs):
    collections_info = client.get_collections()
    if not any(col.name == QDRANT_COLLECTION_NAME for col in collections_info.collections):
        vectors_config = qdrant_client.http.models.VectorParams(
            size=EMBEDDING_SIZE,
            distance=qdrant_client.http.models.Distance.COSINE,
        )

        client.create_collection(
            collection_name= QDRANT_COLLECTION_NAME,
            vectors_config=vectors_config,
        )
        vector_store = Qdrant(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
        vector_store.add_documents(docs)
    else:
        vector_store = Qdrant(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
    return vector_store



with open("service_definitions.json","r",encoding="utf-8") as f:
    raw = json.load(f)

docs = [
    Document(
      page_content=f"Mã: {d['Service_pk']}. Định nghĩa: {d['Definition_long']}",
      metadata={"service_pk": str(d["Service_pk"]).strip()},
    )
    for d in raw
]

vector_store = load_vectordb(docs)

dense_retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 8})

# Sparse retriever
sparse_retriever = BM25Retriever.from_documents(docs)
sparse_retriever.k = 8



ensemble_retriever = EnsembleRetriever(
    retrievers=[dense_retriever, sparse_retriever],
    weights=[0.5, 0.5]
)

def ensemble_retrieve(query: str, service_pk: str, k: int = 3) -> Optional[List[Document]]:
    retrieved = ensemble_retriever.get_relevant_documents(query)
    #print(retrieved)
    #print(service_pk_list)
    filtered = [
        doc for doc in retrieved if doc.metadata.get("service_pk") == service_pk
    ]

    return filtered[:k] if filtered else None
