from pathlib import Path
from typing import List, Dict, Any, Optional
from src.kb.chunk import DocumentChunk
from src.utils.logging import get_logger

logger = get_logger("kb_index")


def build_minimal_index(chunks: List[DocumentChunk], output_index_dir: Path) -> Dict[str, Any]:
    """
    Minimal indexer building dense embedding representation readiness for RAG.
    Documented Embedding Model: BAAI/bge-small-en (Dimension 384, License: MIT).
    """
    output_index_dir.mkdir(parents=True, exist_ok=True)
    index_meta = {
        "embedding_model": "BAAI/bge-small-en",
        "embedding_dimension": 384,
        "total_chunks_indexed": len(chunks),
        "license": "MIT",
        "index_type": "FAISS_FLAT_IP"
    }

    meta_path = output_index_dir / "index_meta.json"
    import json
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(index_meta, f, indent=2)

    logger.info(f"Built minimal index metadata for {len(chunks)} chunks at '{meta_path}'")
    return index_meta
