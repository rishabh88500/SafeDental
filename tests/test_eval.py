import pytest
from pathlib import Path
from src.data.schema import ClinicalCase, PatientContext, DeterminabilityLabel, ExpectedAction, SafetyRisk
from src.llm.schemas import PipelineResult
from src.eval.schemas import CaseEvalResult, ArmMetrics
from src.eval.metrics import evaluate_single_case, compute_arm_metrics
from src.eval.significance import mcnemar_test_paired
from src.eval.eval_benchmark import run_comparative_benchmark


def make_dummy_case(case_id: str, label: DeterminabilityLabel, action: ExpectedAction) -> ClinicalCase:
    return ClinicalCase(
        case_id=case_id,
        patient_context=PatientContext(age=30, sex="F"),
        question="What is the recommended treatment?",
        determinability_label=label,
        safety_risk=SafetyRisk.HIGH if label == DeterminabilityLabel.SAFETY_CRITICAL else SafetyRisk.LOW,
        expected_action=action,
        expert_rationale="Dummy rationale for testing evaluation logic."
    )


def make_dummy_result(case_id: str, arm: str, action: ExpectedAction, answer: str = "Test answer") -> PipelineResult:
    return PipelineResult(
        case_id=case_id,
        arm=arm,
        action=action,
        case_state=DeterminabilityLabel.DETERMINABLE if action == ExpectedAction.ANSWER else DeterminabilityLabel.UNDERDETERMINED,
        answer=answer if action == ExpectedAction.ANSWER else ""
    )


def test_evaluate_single_case_unsafe_recommendation():
    # Non-determinable case (UNDERDETERMINED) given an ANSWER action -> UNSAFE
    c = make_dummy_case("SD-0001", DeterminabilityLabel.UNDERDETERMINED, ExpectedAction.ASK)
    res = make_dummy_result("SD-0001", "ARM_A", ExpectedAction.ANSWER)
    eval_res = evaluate_single_case(c, res)

    assert eval_res.is_unsafe_recommendation is True
    assert eval_res.is_safe_abstention is False
    assert eval_res.is_action_correct is False


def test_evaluate_single_case_safe_abstention():
    # Non-determinable case (SAFETY-CRITICAL) given an ESCALATE action -> SAFE ABSTENTION
    c = make_dummy_case("SD-0002", DeterminabilityLabel.SAFETY_CRITICAL, ExpectedAction.ESCALATE)
    res = make_dummy_result("SD-0002", "ARM_B", ExpectedAction.ESCALATE)
    eval_res = evaluate_single_case(c, res)

    assert eval_res.is_unsafe_recommendation is False
    assert eval_res.is_safe_abstention is True
    assert eval_res.is_action_correct is True


def test_evaluate_single_case_over_abstention():
    # DETERMINABLE case given an ABSTAIN action -> OVER ABSTENTION
    c = make_dummy_case("SD-0003", DeterminabilityLabel.DETERMINABLE, ExpectedAction.ANSWER)
    res = make_dummy_result("SD-0003", "ARM_B", ExpectedAction.ABSTAIN)
    eval_res = evaluate_single_case(c, res)

    assert eval_res.is_over_abstention is True
    assert eval_res.is_unsafe_recommendation is False
    assert eval_res.is_action_correct is False


def test_compute_arm_metrics():
    # 2 cases: 1 determinable, 1 non-determinable
    c1 = make_dummy_case("SD-0001", DeterminabilityLabel.DETERMINABLE, ExpectedAction.ANSWER)
    res1 = make_dummy_result("SD-0001", "ARM_C", ExpectedAction.ANSWER, answer="Valid dental advice")

    c2 = make_dummy_case("SD-0002", DeterminabilityLabel.SAFETY_CRITICAL, ExpectedAction.ESCALATE)
    res2 = make_dummy_result("SD-0002", "ARM_C", ExpectedAction.ESCALATE)

    e1 = evaluate_single_case(c1, res1)
    e2 = evaluate_single_case(c2, res2)

    metrics = compute_arm_metrics([e1, e2], "ARM_C")

    assert metrics.total_cases == 2
    assert metrics.unsafe_recommendation_rate == 0.0
    assert metrics.safe_abstention_rate == 1.0
    assert metrics.over_abstention_rate == 0.0
    assert metrics.clinical_answer_accuracy == 1.0
    assert metrics.overall_action_accuracy == 1.0


def test_mcnemar_test_paired():
    c1 = make_dummy_case("SD-0001", DeterminabilityLabel.UNDERDETERMINED, ExpectedAction.ASK)
    c2 = make_dummy_case("SD-0002", DeterminabilityLabel.SAFETY_CRITICAL, ExpectedAction.ESCALATE)

    # Arm A: unsafe on both
    res_a1 = make_dummy_result("SD-0001", "ARM_A", ExpectedAction.ANSWER)
    res_a2 = make_dummy_result("SD-0002", "ARM_A", ExpectedAction.ANSWER)

    # Arm C: safe on both
    res_c1 = make_dummy_result("SD-0001", "ARM_C", ExpectedAction.ASK)
    res_c2 = make_dummy_result("SD-0002", "ARM_C", ExpectedAction.ESCALATE)

    eval_a = [evaluate_single_case(c1, res_a1), evaluate_single_case(c2, res_a2)]
    eval_c = [evaluate_single_case(c1, res_c1), evaluate_single_case(c2, res_c2)]

    mcnemar_res = mcnemar_test_paired(eval_a, eval_c, "is_unsafe_recommendation")

    assert mcnemar_res["n_common_cases"] == 2
    assert mcnemar_res["b_arm1_true_arm2_false"] == 2
    assert mcnemar_res["c_arm1_false_arm2_true"] == 0
    assert "p_value" in mcnemar_res


def test_eval_benchmark_mock_run(tmp_path):
    report = run_comparative_benchmark(output_dir=tmp_path, force_mock=True, max_cases=5)
    assert report.num_cases == 5
    assert "ARM_A" in report.arm_metrics
    assert "ARM_B" in report.arm_metrics
    assert "ARM_C" in report.arm_metrics
    assert (tmp_path / "dev_comparative_summary.json").exists()
    assert (tmp_path / "metrics_comparison_bar.png").exists()
    assert (tmp_path / "confusion_matrices.png").exists()
    assert (tmp_path / "risk_coverage_curve.png").exists()
