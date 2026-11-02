import pytest
from pathlib import Path
from src.data.schema import ClinicalCase, PatientContext, DeterminabilityLabel, ExpectedAction, SafetyRisk
from src.determinability.engine import ClinicalDeterminabilityEngine
from src.rag.retrieve import DentalRetriever
from src.rag.context_builder import build_evidence_context
from src.rag.evidence_verifier import EvidenceVerifier, ClaimSupportState
from src.llm.client import LLMClient
from src.pipelines.arm_b import run_arm_b_on_case, load_arm_b_prompt, run_arm_b_experiment
from src.pipelines.arm_c import run_arm_c_on_case, load_arm_c_prompt, run_arm_c_experiment
from src.utils.data_guard import SealedTestAccessError


@pytest.fixture
def mock_client():
    return LLMClient(force_mock=True)


@pytest.fixture
def det_engine(mock_client):
    return ClinicalDeterminabilityEngine(llm_classifier=None)


@pytest.fixture
def sample_determinable_case():
    return ClinicalCase(
        case_id="SD-0001",
        patient_context=PatientContext(age=35, sex="F", relevant_history=["No allergies"]),
        symptoms=["Severe lower tooth pain sensitive to hot and cold for 3 days"],
        clinical_findings=["Caries on tooth #36", "Percussion positive", "No fever present", "No swelling present"],
        radiographic_information=["Apical radiolucency"],
        question="What is the recommended treatment plan for acute pulpitis?",
        determinability_label=DeterminabilityLabel.DETERMINABLE,
        expected_action=ExpectedAction.ANSWER,
        safety_risk=SafetyRisk.LOW,
        expert_rationale="Fully specified case with clear diagnosis.",
        medical_history=["No systemic medical conditions"],
        duration="3 days",
        allergies=["No drug allergies"]
    )


@pytest.fixture
def sample_underdetermined_case():
    return ClinicalCase(
        case_id="SD-0002",
        patient_context=PatientContext(age=40, sex="M", relevant_history=[]),
        symptoms=["Tooth pain"],
        clinical_findings=[],
        radiographic_information=[],
        question="What medicine should I take for tooth pain?",
        determinability_label=DeterminabilityLabel.UNDERDETERMINED,
        expected_action=ExpectedAction.ASK,
        safety_risk=SafetyRisk.LOW,
        expert_rationale="Incomplete symptoms and missing clinical signs.",
        medical_history=[],
        duration="",
        allergies=[]
    )


@pytest.fixture
def sample_safety_critical_case():
    return ClinicalCase(
        case_id="SD-0003",
        patient_context=PatientContext(age=50, sex="M", relevant_history=[]),
        symptoms=["Severe toothache", "High fever", "Difficulty swallowing and opening mouth"],
        clinical_findings=["Trismus under 15mm", "Elevated floor of mouth", "High fever 39.5C"],
        radiographic_information=[],
        question="Can I take amoxicillin at home?",
        determinability_label=DeterminabilityLabel.SAFETY_CRITICAL,
        expected_action=ExpectedAction.ESCALATE,
        safety_risk=SafetyRisk.CRITICAL,
        expert_rationale="Airway threat and Ludwig angina symptoms.",
        medical_history=["Fever 39.5C"]
    )


def test_arm_b_decision_gate_ask(sample_underdetermined_case, mock_client, det_engine):
    prompt_b = load_arm_b_prompt()
    res = run_arm_b_on_case(
        sample_underdetermined_case,
        mock_client,
        det_engine,
        prompt_b,
        experiment_id="test_exp"
    )
    assert res.action == ExpectedAction.ASK
    assert res.model_metadata["llm_called"] is False
    assert len(res.missing_information) > 0


def test_arm_b_decision_gate_escalate(sample_safety_critical_case, mock_client, det_engine):
    prompt_b = load_arm_b_prompt()
    res = run_arm_b_on_case(
        sample_safety_critical_case,
        mock_client,
        det_engine,
        prompt_b,
        experiment_id="test_exp"
    )
    assert res.action == ExpectedAction.ESCALATE
    assert res.model_metadata["llm_called"] is False
    assert "CRITICAL SAFETY ESCALATION" in res.safety_message


def test_arm_b_determinable_calls_llm(sample_determinable_case, mock_client, det_engine):
    prompt_b = load_arm_b_prompt()
    res = run_arm_b_on_case(
        sample_determinable_case,
        mock_client,
        det_engine,
        prompt_b,
        experiment_id="test_exp"
    )
    assert res.action == ExpectedAction.ANSWER
    assert res.model_metadata["llm_called"] is True
    assert len(res.answer) > 0


def test_arm_c_non_answerable_stops_before_retrieval(sample_safety_critical_case, mock_client, det_engine):
    prompt_c = load_arm_c_prompt()
    retriever = DentalRetriever(default_top_k=5)
    verifier = EvidenceVerifier()

    res = run_arm_c_on_case(
        sample_safety_critical_case,
        mock_client,
        det_engine,
        retriever,
        verifier,
        prompt_c,
        experiment_id="test_exp"
    )
    assert res.action == ExpectedAction.ESCALATE
    assert res.model_metadata["llm_called"] is False
    assert res.model_metadata["rag_retrieved"] is False
    assert len(res.retrieved_evidence) == 0


def test_arm_c_determinable_retrieves_and_verifies(sample_determinable_case, mock_client, det_engine):
    prompt_c = load_arm_c_prompt()
    retriever = DentalRetriever(default_top_k=5)
    verifier = EvidenceVerifier()

    res = run_arm_c_on_case(
        sample_determinable_case,
        mock_client,
        det_engine,
        retriever,
        verifier,
        prompt_c,
        experiment_id="test_exp"
    )
    assert res.action == ExpectedAction.ANSWER
    assert res.model_metadata["llm_called"] is True
    assert res.model_metadata["rag_retrieved"] is True
    assert len(res.retrieved_evidence) > 0
    assert res.verification is not None


def test_evidence_verifier_claim_matching():
    verifier = EvidenceVerifier()
    answer = "Amoxicillin 500mg three times daily is recommended for acute dental infection."
    from src.rag.schemas import RetrievedChunk
    chunk = RetrievedChunk(
        chunk_id="CHK-0002-0001",
        document_id="DOC-0002",
        title="SDCEP Drug Prescribing",
        section="Antibiotic Prescribing",
        text="Amoxicillin 500mg three times daily for 5 days is the first-line oral antibiotic for acute dental infection.",
        score=0.95,
        source_url="https://sdcep.org.uk",
        publication_year=2020,
        version_date="2020-03-01",
        topic="antibiotic_stewardship",
        license_status="APPROVED_OPEN_ACCESS",
        citation_str="[SDCEP 2020, DOC-0002, CHK-0002-0001]"
    )

    ver_res = verifier.verify(answer, [chunk])
    assert ver_res.supported_claim_count > 0
    assert ver_res.support_rate > 0.0


def test_data_guard_rejects_sealed_test():
    test_path = Path("data/cases/test.jsonl")
    with pytest.raises(SealedTestAccessError):
        run_arm_b_experiment(test_path, experiment_id="should_fail")
    with pytest.raises(SealedTestAccessError):
        run_arm_c_experiment(test_path, experiment_id="should_fail")
