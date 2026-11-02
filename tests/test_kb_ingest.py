import tempfile
from pathlib import Path
from src.kb.ingest import ingest_document, DocumentMetadata


def test_ingest_document():
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
        content = "Systemic antibiotics are not recommended for localized pulpitis."
        doc_meta = ingest_document(content, meta_dict, kb_root)

        assert isinstance(doc_meta, DocumentMetadata)
        assert doc_meta.document_id == "DOC-0001"
        assert (kb_root / "raw" / "DOC-0001.txt").exists()
        assert (kb_root / "metadata" / "DOC-0001.json").exists()
