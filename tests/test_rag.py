import pytest
import numpy as np
from src.kb.chunk import DocumentChunk
from src.rag.embed import EmbeddingEngine
from src.rag.index import VectorIndexManager
from src.rag.retrieve import DentalRetriever, format_citation, normalize_query


@pytest.fixture
def sample_chunks():
    return [
        DocumentChunk(
            chunk_id="CHK-0001-0001",
            document_id="DOC-0001",
            title="ADA Antibiotic Guidelines",
            section="Indication for Antibiotics",
            text="Systemic antibiotics are not recommended for localized acute pulpitis without fever or systemic signs.",
            source_url="https://ada.org",
            publication_year=2019,
            version_date="2019-11-01",
            topic="antibiotic_stewardship",
            license_status="APPROVED_OPEN_ACCESS"
        ),
        DocumentChunk(
            chunk_id="CHK-0002-0001",
            document_id="DOC-0002",
            title="SDCEP Drug Prescribing Guidelines",
            section="First-Line Antibiotics",
            text="Amoxicillin 500mg three times daily for 5 days is the first-line oral antibiotic for acute dental infection.",
            source_url="https://sdcep.org.uk",
            publication_year=2020,
            version_date="2020-03-01",
            topic="antibiotic_stewardship",
            license_status="APPROVED_OPEN_ACCESS"
        ),
        DocumentChunk(
            chunk_id="CHK-0003-0001",
            document_id="DOC-0003",
            title="AAOMS Emergency Escalation Guidelines",
            section="Airway and Fascial Space Emergency",
            text="Trismus under 20mm, floor of mouth elevation, or difficulty swallowing dysphagia require immediate emergency referral.",
            source_url="https://aaoms.org",
            publication_year=2021,
            version_date="2021-05-01",
            topic="urgent_escalation_red_flags",
            license_status="APPROVED_OPEN_ACCESS"
        )
    ]


def test_embedding_engine_fallback():
    embedder = EmbeddingEngine(force_fallback=True)
    vecs = embedder.embed_texts(["dental pulpitis pain", "amoxicillin dosage"])
    assert isinstance(vecs, np.ndarray)
    assert vecs.shape == (2, 384)
    assert vecs.dtype == np.float32


def test_vector_index_manager_search(sample_chunks, tmp_path):
    embedder = EmbeddingEngine(force_fallback=True)
    idx_mgr = VectorIndexManager(index_dir=tmp_path, embedder=embedder)
    meta = idx_mgr.build_and_save_index(sample_chunks)

    assert meta["total_chunks"] == 3

    q_vec = embedder.embed_query("amoxicillin dosage for dental pain")
    results = idx_mgr.search(q_vec, top_k=2)

    assert len(results) == 2
    assert results[0][0].chunk_id in ["CHK-0002-0001", "CHK-0001-0001"]


def test_dental_retriever(sample_chunks, tmp_path):
    embedder = EmbeddingEngine(force_fallback=True)
    idx_mgr = VectorIndexManager(index_dir=tmp_path, embedder=embedder)
    idx_mgr.build_and_save_index(sample_chunks)

    retriever = DentalRetriever(index_manager=idx_mgr, embedder=embedder)
    res = retriever.retrieve("trismus difficulty swallowing emergency", top_k=2)

    assert res.query == "trismus difficulty swallowing emergency"
    assert len(res.retrieved_chunks) == 2
    assert "AAOMS" in res.retrieved_chunks[0].citation_str
    assert res.retrieved_chunks[0].chunk_id == "CHK-0003-0001"


def test_format_citation(sample_chunks):
    chk = sample_chunks[0]
    cit = format_citation(chk)
    assert cit == "[ADA 2019, DOC-0001, CHK-0001-0001]"


def test_normalize_query():
    raw = "  What is the  DOSE of Amoxicillin?  \n"
    norm = normalize_query(raw)
    assert norm == "what is the dose of amoxicillin?"
