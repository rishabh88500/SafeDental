import difflib
from typing import List, Tuple, Set
from src.data.schema import ClinicalCase
from src.utils.logging import get_logger

logger = get_logger("dedupe")

_EMBEDDING_MODEL_CACHE = None
_SENTENCE_TRANSFORMERS_AVAILABLE = True

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence_transformers not installed. Falling back to difflib text similarity.")


def get_embedding_model(model_name: str = "BAAI/bge-small-en"):
    global _EMBEDDING_MODEL_CACHE
    if not _SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    if _EMBEDDING_MODEL_CACHE is None:
        logger.info(f"Loading embedding model for deduplication: {model_name}")
        _EMBEDDING_MODEL_CACHE = SentenceTransformer(model_name)
    return _EMBEDDING_MODEL_CACHE


def compute_similarity_matrix(cases: List[ClinicalCase], model_name: str = "BAAI/bge-small-en"):
    """Computes similarity matrix using sentence_transformers if available, else difflib."""
    num_cases = len(cases)
    sim_matrix = np.zeros((num_cases, num_cases)) if _SENTENCE_TRANSFORMERS_AVAILABLE else [[0.0]*num_cases for _ in range(num_cases)]

    if _SENTENCE_TRANSFORMERS_AVAILABLE:
        model = get_embedding_model(model_name)
        texts = [case.to_clinical_narrative() for case in cases]
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        sim_matrix = np.dot(embeddings, embeddings.T)
    else:
        narratives = [case.to_clinical_narrative() for case in cases]
        for i in range(num_cases):
            for j in range(i, num_cases):
                if i == j:
                    sim_matrix[i][j] = 1.0
                else:
                    ratio = difflib.SequenceMatcher(None, narratives[i], narratives[j]).ratio()
                    sim_matrix[i][j] = ratio
                    sim_matrix[j][i] = ratio
    return sim_matrix


def find_duplicate_pairs(
    cases: List[ClinicalCase],
    similarity_threshold: float = 0.90,
    model_name: str = "BAAI/bge-small-en"
) -> List[Tuple[str, str, float]]:
    """Finds pairs of cases whose similarity exceeds the threshold."""
    if len(cases) < 2:
        return []

    sim_matrix = compute_similarity_matrix(cases, model_name=model_name)
    duplicate_pairs = []
    num_cases = len(cases)

    for i in range(num_cases):
        for j in range(i + 1, num_cases):
            sim = float(sim_matrix[i][j] if not _SENTENCE_TRANSFORMERS_AVAILABLE else sim_matrix[i, j])
            if sim >= similarity_threshold:
                duplicate_pairs.append((cases[i].case_id, cases[j].case_id, sim))

    return duplicate_pairs


def deduplicate_cases(
    cases: List[ClinicalCase],
    similarity_threshold: float = 0.90,
    model_name: str = "BAAI/bge-small-en"
) -> List[ClinicalCase]:
    """Removes near-duplicate cases, keeping the first occurrence."""
    if len(cases) < 2:
        return cases

    sim_matrix = compute_similarity_matrix(cases, model_name=model_name)
    removed_indices: Set[int] = set()
    num_cases = len(cases)

    for i in range(num_cases):
        if i in removed_indices:
            continue
        for j in range(i + 1, num_cases):
            if j in removed_indices:
                continue
            sim = float(sim_matrix[i][j] if not _SENTENCE_TRANSFORMERS_AVAILABLE else sim_matrix[i, j])
            if sim >= similarity_threshold:
                logger.warning(
                    f"Duplicate detected: {cases[j].case_id} is similar to {cases[i].case_id} "
                    f"(sim={sim:.4f}). Excluding {cases[j].case_id}."
                )
                removed_indices.add(j)

    kept_cases = [case for idx, case in enumerate(cases) if idx not in removed_indices]
    logger.info(f"Deduplication complete. Retained {len(kept_cases)} / {len(cases)} cases.")
    return kept_cases
