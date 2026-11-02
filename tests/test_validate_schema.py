import tempfile
import json
from pathlib import Path
from src.data.validate_schema import validate_case_dict, validate_jsonl_file
from src.data.schema import ClinicalCase, PatientContext, DeterminabilityLabel, ExpectedAction, SafetyRisk


def test_validate_case_dict_valid():
    valid_dict = {
        "case_id": "SD-0001",
        "patient_context": {"age": 30, "sex": "M", "relevant_history": []},
        "symptoms": ["pain"],
        "duration": "1 day",
        "medical_history": [],
        "medications": [],
        "allergies": [],
        "clinical_findings": [],
        "radiographic_information": [],
        "question": "What to do for pain?",
        "determinability_label": "DETERMINABLE",
        "critical_missing_information": [],
        "safety_risk": "LOW",
        "expected_action": "ANSWER",
        "supporting_evidence_ids": [],
        "expert_rationale": "Sufficient facts to provide localized dental recommendation."
    }
    is_valid, errors = validate_case_dict(valid_dict)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_case_dict_invalid():
    invalid_dict = {
        "case_id": "INVALID_ID",
        "patient_context": {"age": -5, "sex": "InvalidSex"},
        "question": "short",
        "determinability_label": "UNKNOWN_LABEL"
    }
    is_valid, errors = validate_case_dict(invalid_dict)
    assert is_valid is False
    assert len(errors) > 0


def test_validate_jsonl_file():
    case = ClinicalCase(
        case_id="SD-0002",
        patient_context=PatientContext(age=25, sex="F", relevant_history=[]),
        symptoms=["Pain"],
        duration="2 days",
        question="What to do for molar tooth pain?",
        determinability_label=DeterminabilityLabel.DETERMINABLE,
        safety_risk=SafetyRisk.LOW,
        expected_action=ExpectedAction.ANSWER,
        expert_rationale="Sufficient facts present for standard evaluation advice."
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_cases.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(case.model_dump_json() + "\n")

        is_valid, count, errors = validate_jsonl_file(file_path)
        assert is_valid is True
        assert count == 1
        assert len(errors) == 0
