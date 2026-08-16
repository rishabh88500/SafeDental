import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from src.kb.chunk import DocumentChunk
from src.rag.embed import EmbeddingEngine
from src.utils.config_loader import get_project_root
from src.utils.logging import get_logger

logger = get_logger("rag_index")


class VectorIndexManager:
    """
    FAISS Flat IP (Inner Product / Cosine Similarity) Vector Index Manager.
    Supports building, saving, loading, and fallback search.
    """

    def __init__(self, index_dir: Optional[Path] = None, embedder: Optional[EmbeddingEngine] = None):
        self.project_root = get_project_root()
        self.index_dir = index_dir or (self.project_root / "data" / "index")
        self.embedder = embedder or EmbeddingEngine()
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index = None
        self.use_faiss = False

    def build_and_save_index(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Embeds chunks and saves vector index and metadata mapping to disk.
        """
        if not chunks:
            raise ValueError("Cannot build vector index with zero chunks.")

        self.chunks = chunks
        texts = [f"{chk.title}\n{chk.section}\n{chk.text}" for chk in chunks]

        logger.info(f"Embedding {len(chunks)} chunks using '{self.embedder.model_name}'...")
        self.embeddings = self.embedder.embed_texts(texts)

        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Attempt FAISS index creation
        try:
            import faiss
            dim = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(self.embeddings)
            faiss_bin_path = self.index_dir / "faiss_index.bin"
            faiss.write_index(self.faiss_index, str(faiss_bin_path))
            self.use_faiss = True
            logger.info(f"Saved FAISS index to '{faiss_bin_path}'")
        except Exception as e:
            logger.warning(f"FAISS unavailable ({e}). Using normalized numpy vector matrix fallback.")
            np_matrix_path = self.index_dir / "embeddings_matrix.npy"
            np.save(np_matrix_path, self.embeddings)
            self.use_faiss = False

        # Save Chunks Metadata Mapping
        chunks_json_path = self.index_dir / "index_chunks.json"
        with open(chunks_json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps([chk.model_dump() for chk in chunks], indent=2))

        # Save Summary Index Meta
        index_meta = {
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": int(self.embeddings.shape[1]),
            "total_chunks": len(chunks),
            "use_faiss": self.use_faiss,
            "index_type": "FAISS_FLAT_IP" if self.use_faiss else "NUMPY_COSINE"
        }
        meta_json_path = self.index_dir / "index_meta.json"
        with open(meta_json_path, "w", encoding="utf-8") as f:
            json.dump(index_meta, f, indent=2)

        logger.info(f"Built vector index successfully ({len(chunks)} chunks). Saved at '{self.index_dir}'")
        return index_meta

    def load_index(self) -> bool:
        """Loads index metadata and vectors from disk."""
        chunks_json_path = self.index_dir / "index_chunks.json"
        if not chunks_json_path.exists():
            logger.warning(f"Index chunks file not found at '{chunks_json_path}'. Index not loaded.")
            return False

        # Load chunks
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            chunk_dicts = json.load(f)
            self.chunks = [DocumentChunk(**d) for d in chunk_dicts]

        # Load FAISS index if present
        faiss_bin_path = self.index_dir / "faiss_index.bin"
        if faiss_bin_path.exists():
            try:
                import faiss
                self.faiss_index = faiss.read_index(str(faiss_bin_path))
                self.use_faiss = True
                logger.info(f"Loaded FAISS vector index ({len(self.chunks)} chunks) from '{faiss_bin_path}'")
                return True
            except Exception as e:
                logger.warning(f"Failed to load FAISS index ({e}). Trying numpy matrix.")

        np_matrix_path = self.index_dir / "embeddings_matrix.npy"
        if np_matrix_path.exists():
            self.embeddings = np.load(np_matrix_path)
            self.use_faiss = False
            logger.info(f"Loaded numpy embedding matrix ({len(self.chunks)} chunks) from '{np_matrix_path}'")
            return True

        # Re-embed if embeddings file absent
        texts = [f"{chk.title}\n{chk.section}\n{chk.text}" for chk in self.chunks]
        self.embeddings = self.embedder.embed_texts(texts)
        self.use_faiss = False
        return True

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Searches index for top_k most similar chunks given a 1D or 2D query embedding vector.

        Returns:
            List[Tuple[DocumentChunk, float]]: List of (chunk, similarity_score) tuples sorted descending.
        """
        if not self.chunks:
            return []

        q_vec = query_vector.astype(np.float32)
        if q_vec.ndim == 1:
            q_vec = np.expand_dims(q_vec, axis=0)

        top_k = min(top_k, len(self.chunks))

        if self.use_faiss and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(q_vec, top_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self.chunks):
                    results.append((self.chunks[idx], float(score)))
            return results

        # Numpy Cosine Similarity Fallback
        if self.embeddings is None:
            texts = [f"{chk.title}\n{chk.section}\n{chk.text}" for chk in self.chunks]
            self.embeddings = self.embedder.embed_texts(texts)

        # Dot product of normalized vectors = Cosine similarity
        scores = np.dot(self.embeddings, q_vec[0])
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [(self.chunks[i], float(scores[i])) for i in top_indices]
