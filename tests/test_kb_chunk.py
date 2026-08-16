from src.kb.ingest import DocumentMetadata
from src.kb.chunk import chunk_text_section_aware, DocumentChunk


def test_chunk_text_section_aware():
    meta = DocumentMetadata(
        document_id="DOC-0001",
        title="Test Guideline",
        organization_authors="ADA",
        publication_year=2020,
        version_date="2020-01-01",
        document_type="guideline",
        url="https://ada.org",
        license_status="APPROVED_OPEN_ACCESS",
        topic="pulpitis",
        evidence_level="Level I"
    )
    text = "## Section 1: Intro\nThis is the intro section text.\n\n## Section 2: Management\nOperative pulpitis management."
    chunks = chunk_text_section_aware(text, meta, target_chunk_size=100, overlap=10)

    assert len(chunks) == 2
    assert isinstance(chunks[0], DocumentChunk)
    assert chunks[0].section == "Section 1: Intro"
    assert "intro section text" in chunks[0].text
    assert chunks[1].section == "Section 2: Management"
    assert "Operative pulpitis" in chunks[1].text
