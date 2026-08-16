import tempfile
from pathlib import Path
from src.kb.ingest import ingest_document
from src.kb.clean_text import clean_document_file
from src.kb.chunk import process_and_save_chunks
from src.kb.manifest import generate_kb_manifest, KBManifest


def test_generate_kb_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_root = Path(tmpdir) / "knowledge_base"
        meta_dict = {
            "document_id": "DOC-0001",
            "title": "ADA Antibiotic Guidelines",
            "organization_authors": "ADA",
            "publication_year": 2019,
            "version_date": "2019-11-01",
            "document_type": "clinical_guideline",
            "url": "https://ada.org",
            "license_status": "APPROVED_OPEN_ACCESS",
            "topic": "antibiotic_stewardship",
            "evidence_level": "Level I"
        }
        content = "## Section 1\nSystemic antibiotics are not recommended for localized pulpitis."
        doc_meta = ingest_document(content, meta_dict, kb_root)

        raw_path = kb_root / "raw" / "DOC-0001.txt"
        clean_path = kb_root / "cleaned" / "DOC-0001.txt"
        clean_document_file(raw_path, clean_path)

        meta_file = kb_root / "metadata" / "DOC-0001.json"
        chunk_file = kb_root / "chunks" / "DOC-0001.jsonl"
        process_and_save_chunks(clean_path, meta_file, chunk_file)

        manifest = generate_kb_manifest(kb_root)
        assert isinstance(manifest, KBManifest)
        assert manifest.total_documents == 1
        assert manifest.total_chunks == 1
        assert manifest.topic_distribution.get("antibiotic_stewardship") == 1
