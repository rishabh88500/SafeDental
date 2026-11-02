from typing import List
from src.rag.schemas import RetrievedChunk
from src.utils.logging import get_logger

logger = get_logger("context_builder")


def build_evidence_context(chunks: List[RetrievedChunk]) -> str:
    """
    Transforms a list of RetrievedChunk objects into a structured evidence context string.
    Emphasizes citation IDs and source document metadata for prompt inclusion.
    """
    if not chunks:
        return "NO EVIDENCE CHUNKS AVAILABLE."

    context_blocks = []
    for idx, chk in enumerate(chunks, 1):
        block = (
            f"[EVIDENCE {idx}]\n"
            f"Citation ID: {chk.citation_str}\n"
            f"Document Title: {chk.title}\n"
            f"Section: {chk.section}\n"
            f"Document ID: {chk.document_id}\n"
            f"Chunk ID: {chk.chunk_id}\n"
            f"Publication Year: {chk.publication_year}\n"
            f"Evidence Text:\n{chk.text}"
        )
        context_blocks.append(block)

    full_context = "\n\n" + ("\n\n" + "=" * 40 + "\n\n").join(context_blocks) + "\n\n"
    return full_context
