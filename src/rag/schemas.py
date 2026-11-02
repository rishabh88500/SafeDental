from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """
    Traceable retrieved evidence chunk contract preserving document metadata and citation.
    """
    chunk_id: str
    document_id: str
    title: str
    section: str = Field(default="General")
    text: str
    score: float = Field(description="Similarity relevance score")
    source_url: str
    publication_year: int
    version_date: str
    topic: str
    license_status: str
    citation_str: str = Field(description="Formatted clinical citation string e.g. [ADA 2019, DOC-0001, CHK-0001-0002]")


class RetrieverResult(BaseModel):
    """
    Normalized response returned by DentalRetriever.
    """
    query: str
    normalized_query: str
    retrieved_chunks: List[RetrievedChunk]
    top_k: int
    vector_store_type: str = Field(default="FAISS_FLAT_IP")
    embedding_model: str = Field(default="BAAI/bge-small-en")
    execution_time_ms: float = Field(default=0.0)
