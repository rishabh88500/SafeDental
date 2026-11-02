import json
import pytest
from pathlib import Path
from src.data.schema import (
    ClinicalCase,
    PatientContext,
    DeterminabilityLabel,
    ExpectedAction,
    SafetyRisk,
)
from src.utils.config_loader import get_project_root


def test_clinical_case_creation():
    case = ClinicalCase(
        case_id="SD-0001",
        patient_context=PatientContext(age=34, sex="F", relevant_history=["Hypertension"]),
        symptoms=["Throbbing tooth pain"],
        duration="3 days",
        medical_history=["Hypertension"],
        allergies=["Penicillin"],
        question="What should be done for tooth #30?",
        determinability_label=DeterminabilityLabel.DETERMINABLE,
        safety_risk=SafetyRisk.LOW,
        expected_action=ExpectedAction.ANSWER,
        expert_rationale="Patient presents with localized pulpal pain without systemic red flags."
    )
    assert case.case_id == "SD-0001"
    assert case.determinability_label == DeterminabilityLabel.DETERMINABLE
    assert case.expected_action == ExpectedAction.ANSWER
    narrative = case.to_clinical_narrative()
    assert "34F" in narrative
    assert "Penicillin" in narrative


def test_schema_json_file_exists():
    schema_path = get_project_root() / "data" / "schema" / "case_schema.json"
    assert schema_path.exists()
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    assert data["title"] == "ClinicalCase"
    assert "case_id" in data["required"]
