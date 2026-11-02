import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
from datetime import datetime
from pydantic import BaseModel, Field
from src.kb.ingest import DocumentMetadata
from src.kb.chunk import DocumentChunk
from src.utils.logging import get_logger

logger = get_logger("kb_manifest")


class KBManifest(BaseModel):
    kb_version: str = Field(default="0.1.0")
    total_documents: int
    total_chunks: int
    topic_distribution: Dict[str, int]
    license_distribution: Dict[str, int]
    source_approval_status: Dict[str, str]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    manifest_checksum: str = Field(default="")


def generate_kb_manifest(kb_root: Path) -> KBManifest:
    """Generates a master manifest for the Knowledge Base."""
    meta_dir = kb_root / "metadata"
    chunks_dir = kb_root / "chunks"

    docs: List[DocumentMetadata] = []
    if meta_dir.exists():
        for meta_file in meta_dir.glob("*.json"):
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            docs.append(DocumentMetadata(**data))

    chunks: List[DocumentChunk] = []
    if chunks_dir.exists():
        for chunk_file in chunks_dir.glob("*.jsonl"):
            with open(chunk_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        chunks.append(DocumentChunk(**json.loads(line.strip())))

    topic_counts = dict(Counter([d.topic for d in docs]))
    license_counts = dict(Counter([d.license_status for d in docs]))
    approval_status = {d.document_id: d.license_status for d in docs}

    manifest = KBManifest(
        kb_version="0.1.0",
        total_documents=len(docs),
        total_chunks=len(chunks),
        topic_distribution=topic_counts,
        license_distribution=license_counts,
        source_approval_status=approval_status,
    )

    manifest_json = manifest.model_dump_json(indent=2)
    checksum = hashlib.md5(manifest_json.encode("utf-8")).hexdigest()
    manifest.manifest_checksum = checksum

    manifests_dir = kb_root / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifests_dir / "manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    logger.info(
        f"Generated KB Manifest: {len(docs)} docs, {len(chunks)} chunks. Saved to '{manifest_path}'"
    )
    return manifest
