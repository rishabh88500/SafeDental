from typing import List
from src.data.schema import ClinicalCase, PatientContext, DeterminabilityLabel, ExpectedAction, SafetyRisk, DatasetSplit
from src.data.split import stratified_split_cases


def test_stratified_split():
    cases: List[ClinicalCase] = []
    # Create 10 DETERMINABLE and 10 SAFETY_CRITICAL cases
    for i in range(10):
        cases.append(
            ClinicalCase(
                case_id=f"SD-{i+1:04d}",
                patient_context=PatientContext(age=30, sex="F", relevant_history=[]),
                symptoms=["Pain"],
                question=f"Question {i}",
                determinability_label=DeterminabilityLabel.DETERMINABLE,
                safety_risk=SafetyRisk.LOW,
                expected_action=ExpectedAction.ANSWER,
                expert_rationale="Sufficient clinical facts present."
            )
        )
    for i in range(10, 20):
        cases.append(
            ClinicalCase(
                case_id=f"SD-{i+1:04d}",
                patient_context=PatientContext(age=50, sex="M", relevant_history=[]),
                symptoms=["Difficulty swallowing"],
                question=f"Emergency question {i}",
                determinability_label=DeterminabilityLabel.SAFETY_CRITICAL,
                safety_risk=SafetyRisk.CRITICAL,
                expected_action=ExpectedAction.ESCALATE,
                expert_rationale="Emergency escalation required."
            )
        )

    splits = stratified_split_cases(cases, train_ratio=0.30, dev_ratio=0.30, test_ratio=0.40, seed=42)

    assert len(splits[DatasetSplit.TRAIN]) == 6  # 3 of each label
    assert len(splits[DatasetSplit.DEV]) == 6    # 3 of each label
    assert len(splits[DatasetSplit.TEST]) == 8   # 4 of each label (40%)

    # Verify no case appears in multiple splits
    train_ids = set(c.case_id for c in splits[DatasetSplit.TRAIN])
    dev_ids = set(c.case_id for c in splits[DatasetSplit.DEV])
    test_ids = set(c.case_id for c in splits[DatasetSplit.TEST])

    assert len(train_ids.intersection(dev_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(dev_ids.intersection(test_ids)) == 0
