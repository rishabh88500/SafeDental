import time
import re
from pathlib import Path
from typing import List, Optional
from src.kb.chunk import DocumentChunk
from src.rag.schemas import RetrievedChunk, RetrieverResult
from src.rag.embed import EmbeddingEngine
from src.rag.index import VectorIndexManager
from src.utils.config_loader import get_project_root, load_config
from src.utils.logging import get_logger

logger = get_logger("rag_retrieve")


def format_citation(chunk: DocumentChunk) -> str:
    """Formats clinical citation string e.g. [ADA 2019, DOC-0001, CHK-0001-0002]."""
    org = chunk.title.split()[0] if chunk.title else "DentalGuideline"
    return f"[{org} {chunk.publication_year}, {chunk.document_id}, {chunk.chunk_id}]"


def normalize_query(query: str) -> str:
    """Normalizes query text (strips excessive whitespace, lowercases)."""
    if not query:
        return ""
    cleaned = re.sub(r"\s+", " ", query.strip())
    return cleaned.lower()


class DentalRetriever:
    """
    Dental Evidence Retriever component for SafeDental.
    Retrieves top-k evidence chunks with preserved document metadata and traceable clinical citations.
    """

    def __init__(
        self,
        index_manager: Optional[VectorIndexManager] = None,
        embedder: Optional[EmbeddingEngine] = None,
        default_top_k: int = 5
    ):
        self.config = load_config()
        self.project_root = get_project_root()
        self.embedder = embedder or EmbeddingEngine(model_name=self.config.retrieval.embedding_model)
        self.index_manager = index_manager or VectorIndexManager(embedder=self.embedder)
        self.default_top_k = default_top_k

        # Load index from disk if available
        if not self.index_manager.chunks:
            loaded = self.index_manager.load_index()
            if not loaded:
                logger.info("Vector index not found on disk. Populating from KB chunks...")
                self._load_chunks_from_kb()

    def _load_chunks_from_kb(self):
        """Loads chunks from data/knowledge_base/chunks/*.jsonl and builds index."""
        kb_chunks_dir = self.project_root / "data" / "knowledge_base" / "chunks"
        chunks: List[DocumentChunk] = []

        if kb_chunks_dir.exists():
            import json
            for jsonl_file in sorted(kb_chunks_dir.glob("*.jsonl")):
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            c_dict = json.loads(line)
                            chunks.append(DocumentChunk(**c_dict))

        if chunks:
            self.index_manager.build_and_save_index(chunks)
        else:
            logger.warning("No KB chunks found in data/knowledge_base/chunks/.")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> RetrieverResult:
        """
        Retrieves top_k relevant evidence chunks for a query string.
        """
        start_time = time.perf_counter()
        k = top_k if top_k is not None else self.config.retrieval.top_k
        norm_q = normalize_query(query)

        if not norm_q or not self.index_manager.chunks:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RetrieverResult(
                query=query,
                normalized_query=norm_q,
                retrieved_chunks=[],
                top_k=k,
                vector_store_type="FAISS_FLAT_IP" if self.index_manager.use_faiss else "NUMPY_COSINE",
                embedding_model=self.embedder.model_name,
                execution_time_ms=elapsed_ms
            )

        q_embedding = self.embedder.embed_query(norm_q)
        search_results = self.index_manager.search(q_embedding, top_k=k)

        retrieved_list: List[RetrievedChunk] = []
        for chk, score in search_results:
            retrieved_list.append(
                RetrievedChunk(
                    chunk_id=chk.chunk_id,
                    document_id=chk.document_id,
                    title=chk.title,
                    section=chk.section,
                    text=chk.text,
                    score=float(score),
                    source_url=chk.source_url,
                    publication_year=chk.publication_year,
                    version_date=chk.version_date,
                    topic=chk.topic,
                    license_status=chk.license_status,
                    citation_str=format_citation(chk)
                )
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(f"Retrieved {len(retrieved_list)} chunks for query '{query[:40]}...' in {elapsed_ms:.2f}ms")

        return RetrieverResult(
            query=query,
            normalized_query=norm_q,
            retrieved_chunks=retrieved_list,
            top_k=k,
            vector_store_type="FAISS_FLAT_IP" if self.index_manager.use_faiss else "NUMPY_COSINE",
            embedding_model=self.embedder.model_name,
            execution_time_ms=elapsed_ms
        )
