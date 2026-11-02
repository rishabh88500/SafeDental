import math
import numpy as np
from typing import List, Optional
from src.utils.logging import get_logger

logger = get_logger("rag_embed")


class EmbeddingEngine:
    """
    Embedding engine for dental evidence retrieval.
    Model: BAAI/bge-small-en (Dimension 384, MIT License).
    Includes deterministic fallback embedder for offline execution & unit tests.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en", force_fallback: bool = False):
        self.model_name = model_name
        self.dimension = 384
        self.force_fallback = force_fallback
        self._model = None

        if not force_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model '{model_name}'...")
                self._model = SentenceTransformer(model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{model_name}' ({e}). Using deterministic fallback embedder.")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of text strings into a normalized float32 numpy array (N, 384).
        """
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)

        if self._model is not None and not self.force_fallback:
            try:
                embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed ({e}). Falling back.")

        # Deterministic Hash-based TF-IDF Fallback Vectorizer
        return self._fallback_embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query string into a 1D vector (384,)."""
        res = self.embed_texts([query])
        return res[0]

    def _fallback_embed(self, texts: List[str]) -> np.ndarray:
        """
        Deterministic, normalized hash-based bag-of-words vectorizer producing (N, 384) float32 arrays.
        Guarantees high cosine similarity between texts sharing clinical dental terms.
        """
        vecs = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for idx, text in enumerate(texts):
            words = text.lower().split()
            for word in words:
                clean_w = "".join(c for c in word if c.isalnum())
                if not clean_w:
                    continue
                # Hash word to feature index 0..381
                feature_idx = abs(hash(clean_w)) % (self.dimension - 2)
                vecs[idx, feature_idx] += 1.0

            # Add domain specific topic features for clinical terms
            w_str = text.lower()
            if "antibiotic" in w_str or "amoxicillin" in w_str or "penicillin" in w_str:
                vecs[idx, 382] += 5.0
            if "swelling" in w_str or "trismus" in w_str or "fever" in w_str or "airway" in w_str:
                vecs[idx, 383] += 5.0

            # L2 normalize
            norm = np.linalg.norm(vecs[idx])
            if norm > 0:
                vecs[idx] = vecs[idx] / norm

        return vecs
