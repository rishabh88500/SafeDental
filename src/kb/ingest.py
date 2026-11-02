import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.utils.logging import get_logger

logger = get_logger("kb_ingest")


class DocumentMetadata(BaseModel):
    document_id: str = Field(pattern=r"^DOC-[0-9]{4}$")
    title: str
    organization_authors: str
    publication_year: int
    version_date: str
    document_type: str = Field(default="clinical_guideline")
    url: str
    license_status: str = Field(default="APPROVED_OPEN_ACCESS")
    topic: str
    evidence_level: str = Field(default="Level I (Clinical Guideline)")
    retrieval_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    md5_checksum: str = Field(default="")
    raw_filepath: str = Field(default="")


def compute_md5(text_or_bytes: str) -> str:
    """Computes MD5 hash of string content."""
    return hashlib.md5(text_or_bytes.encode("utf-8")).hexdigest()


def ingest_document(
    raw_content: str,
    metadata_dict: Dict[str, Any],
    kb_root: Path
) -> DocumentMetadata:
    """
    Ingests a raw document into the knowledge base:
    1. Saves immutable raw document into kb_root/raw/DOC-XXXX.txt
    2. Writes metadata JSON to kb_root/metadata/DOC-XXXX.json
    """
    raw_dir = kb_root / "raw"
    metadata_dir = kb_root / "metadata"
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    doc_id = metadata_dict["document_id"]
    raw_file = raw_dir / f"{doc_id}.txt"
    metadata_file = metadata_dir / f"{doc_id}.json"

    # Compute checksum
    checksum = compute_md5(raw_content)
    metadata_dict["md5_checksum"] = checksum
    metadata_dict["raw_filepath"] = str(raw_file.relative_to(kb_root.parent))

    meta = DocumentMetadata(**metadata_dict)

    # Save immutable raw content
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(raw_content)

    # Save metadata
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write(meta.model_dump_json(indent=2))

    logger.info(f"Ingested document {doc_id}: '{meta.title}' ({len(raw_content)} chars)")
    return meta
