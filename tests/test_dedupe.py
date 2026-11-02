from src.data.schema import ClinicalCase, PatientContext, DeterminabilityLabel, ExpectedAction, SafetyRisk
from src.data.dedupe import deduplicate_cases, find_duplicate_pairs


def test_deduplicate_cases():
    case1 = ClinicalCase(
        case_id="SD-0001",
        patient_context=PatientContext(age=30, sex="F", relevant_history=[]),
        symptoms=["Sharp localized pain in tooth #30 when drinking cold water lasting 5 seconds"],
        duration="3 days",
        question="What is the recommended clinical course of action for localized pain in tooth #30?",
        determinability_label=DeterminabilityLabel.DETERMINABLE,
        safety_risk=SafetyRisk.LOW,
        expected_action=ExpectedAction.ANSWER,
        expert_rationale="Patient presents with pulpal pain without systemic red flags."
    )

    # Identical content, different ID
    case2 = ClinicalCase(
        case_id="SD-0002",
        patient_context=PatientContext(age=30, sex="F", relevant_history=[]),
        symptoms=["Sharp localized pain in tooth #30 when drinking cold water lasting 5 seconds"],
        duration="3 days",
        question="What is the recommended clinical course of action for localized pain in tooth #30?",
        determinability_label=DeterminabilityLabel.DETERMINABLE,
        safety_risk=SafetyRisk.LOW,
        expected_action=ExpectedAction.ANSWER,
        expert_rationale="Patient presents with pulpal pain without systemic red flags."
    )

    # Distinct case
    case3 = ClinicalCase(
        case_id="SD-0003",
        patient_context=PatientContext(age=55, sex="M", relevant_history=[]),
        symptoms=["Severe submandibular swelling with difficulty swallowing liquids and high fever 103F"],
        duration="1 day",
        question="What should be done for neck swelling and inability to swallow?",
        determinability_label=DeterminabilityLabel.SAFETY_CRITICAL,
        safety_risk=SafetyRisk.CRITICAL,
        expected_action=ExpectedAction.ESCALATE,
        expert_rationale="Ludwig's Angina airway threat. Immediate emergency referral."
    )

    cases = [case1, case2, case3]
    duplicates = find_duplicate_pairs(cases, similarity_threshold=0.90)
    assert len(duplicates) == 1
    assert duplicates[0][0] == "SD-0001"
    assert duplicates[0][1] == "SD-0002"

    deduped = deduplicate_cases(cases, similarity_threshold=0.90)
    assert len(deduped) == 2
    assert [c.case_id for c in deduped] == ["SD-0001", "SD-0003"]
