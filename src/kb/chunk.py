import re
import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.kb.ingest import DocumentMetadata
from src.utils.logging import get_logger

logger = get_logger("kb_chunk")


class DocumentChunk(BaseModel):
    chunk_id: str = Field(pattern=r"^CHK-[0-9]{4}-[0-9]{4}$")
    document_id: str
    title: str
    section: str = Field(default="General")
    subsection: str = Field(default="")
    page: int = Field(default=1)
    text: str = Field(min_length=10)
    source_url: str
    publication_year: int
    version_date: str
    topic: str
    license_status: str


def chunk_text_section_aware(
    cleaned_text: str,
    meta: DocumentMetadata,
    target_chunk_size: int = 400,
    overlap: int = 50
) -> List[DocumentChunk]:
    """
    Performs section-aware chunking on cleaned text.
    Splits text by markdown/text section headers (e.g. '## Section Name' or 'SECTION N:').
    """
    if not cleaned_text:
        return []

    # Detect section boundaries
    section_pattern = re.compile(r"(?m)^(#{1,4}\s+.*|[A-Z0-9\.\s]{3,40}:|SECTION\s+\d+.*)$")
    matches = list(section_pattern.finditer(cleaned_text))

    sections = []
    if not matches:
        sections.append(("General", cleaned_text))
    else:
        for idx, match in enumerate(matches):
            sec_title = match.group(0).strip("#").strip()
            start_pos = match.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(cleaned_text)
            sec_text = cleaned_text[start_pos:end_pos].strip()
            sections.append((sec_title, sec_text))

    chunks = []
    chunk_counter = 1

    for sec_title, sec_text in sections:
        if not sec_text:
            continue
        words = sec_text.split()
        if len(words) <= target_chunk_size:
            chunk_id = f"CHK-{meta.document_id.replace('DOC-', '')}-{chunk_counter:04d}"
            chunk_counter += 1
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=meta.document_id,
                    title=meta.title,
                    section=sec_title,
                    subsection="",
                    page=1,
                    text=sec_text,
                    source_url=meta.url,
                    publication_year=meta.publication_year,
                    version_date=meta.version_date,
                    topic=meta.topic,
                    license_status=meta.license_status,
                )
            )
        else:
            # Overlapping word window chunking
            start = 0
            while start < len(words):
                end = min(start + target_chunk_size, len(words))
                chunk_words = words[start:end]
                c_text = " ".join(chunk_words)

                chunk_id = f"CHK-{meta.document_id.replace('DOC-', '')}-{chunk_counter:04d}"
                chunk_counter += 1

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=meta.document_id,
                        title=meta.title,
                        section=sec_title,
                        subsection="",
                        page=1,
                        text=c_text,
                        source_url=meta.url,
                        publication_year=meta.publication_year,
                        version_date=meta.version_date,
                        topic=meta.topic,
                        license_status=meta.license_status,
                    )
                )
                start += target_chunk_size - overlap

    logger.info(f"Chunked document {meta.document_id} into {len(chunks)} traceable chunks.")
    return chunks


def process_and_save_chunks(
    cleaned_file: Path,
    metadata_file: Path,
    output_chunk_file: Path,
    target_chunk_size: int = 400,
    overlap: int = 50
) -> List[DocumentChunk]:
    """Reads cleaned text + metadata, chunks text, and saves JSONL chunks file."""
    cleaned_text = cleaned_file.read_text(encoding="utf-8")
    meta_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
    meta = DocumentMetadata(**meta_dict)

    chunks = chunk_text_section_aware(cleaned_text, meta, target_chunk_size=target_chunk_size, overlap=overlap)

    output_chunk_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_chunk_file, "w", encoding="utf-8") as f:
        for chk in chunks:
            f.write(chk.model_dump_json() + "\n")

    return chunks
