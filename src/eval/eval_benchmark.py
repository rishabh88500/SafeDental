import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.config_loader import load_config, get_project_root
from src.utils.data_guard import load_cases_safe
from src.utils.logging import get_logger

from src.llm.client import LLMClient
from src.determinability.engine import DeterminabilityEngine
from src.rag.retrieve import DentalRetriever
from src.rag.evidence_verifier import EvidenceVerifier

from src.pipelines.arm_a import run_arm_a_on_case, load_arm_a_prompt
from src.pipelines.arm_b import run_arm_b_on_case, load_arm_b_prompt
from src.pipelines.arm_c import run_arm_c_on_case, load_arm_c_prompt

from src.eval.metrics import evaluate_single_case, compute_arm_metrics
from src.eval.significance import mcnemar_test_paired
from src.eval.visualize import plot_metrics_comparison, plot_confusion_matrices, plot_risk_coverage
from src.eval.schemas import ComparativeEvaluationReport

logger = get_logger("eval_benchmark")


def run_comparative_benchmark(
    dev_cases_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    force_mock: bool = False,
    max_cases: Optional[int] = None
) -> ComparativeEvaluationReport:
    """
    Executes comparative evaluation across Arm A, Arm B, and Arm C on development dataset.
    """
    cfg = load_config()
    root = get_project_root()

    if dev_cases_path is None:
        dev_cases_path = root / "data" / "cases" / "dev.jsonl"
    if output_dir is None:
        output_dir = root / "experiments" / "eval_results"

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading development dataset from: {dev_cases_path}")
    cases = load_cases_safe(dev_cases_path)
    if max_cases is not None:
        cases = cases[:max_cases]
    logger.info(f"Loaded {len(cases)} development clinical cases.")


    # Initialize shared pipeline components
    client = LLMClient(force_mock=force_mock)
    det_engine = DeterminabilityEngine()
    retriever = DentalRetriever()
    verifier = EvidenceVerifier()

    prompt_a = load_arm_a_prompt()
    prompt_b = load_arm_b_prompt()
    prompt_c = load_arm_c_prompt()

    exp_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Run Arm A
    logger.info("Executing Arm A (Base LLM Baseline)...")
    arm_a_results = []
    for c in cases:
        res = run_arm_a_on_case(
            case=c,
            client=client,
            prompt_template=prompt_a,
            experiment_id=f"exp_eval_a_{exp_timestamp}"
        )
        arm_a_results.append(evaluate_single_case(c, res))

    # Run Arm B
    logger.info("Executing Arm B (Safety Prompting & Determinability Gate)...")
    arm_b_results = []
    for c in cases:
        res = run_arm_b_on_case(
            case=c,
            client=client,
            det_engine=det_engine,
            prompt_template=prompt_b,
            experiment_id=f"exp_eval_b_{exp_timestamp}"
        )
        arm_b_results.append(evaluate_single_case(c, res))

    # Run Arm C
    logger.info("Executing Arm C (Proposed RAG + Safety Pipeline)...")
    arm_c_results = []
    for c in cases:
        res = run_arm_c_on_case(
            case=c,
            client=client,
            det_engine=det_engine,
            retriever=retriever,
            verifier=verifier,
            prompt_template=prompt_c,
            experiment_id=f"exp_eval_c_{exp_timestamp}"
        )
        arm_c_results.append(evaluate_single_case(c, res))

    # Compute Arm Metrics
    logger.info("Computing metrics for all arms...")
    metrics_a = compute_arm_metrics(arm_a_results, "ARM_A")
    metrics_b = compute_arm_metrics(arm_b_results, "ARM_B")
    metrics_c = compute_arm_metrics(arm_c_results, "ARM_C")

    arm_metrics_map = {
        "ARM_A": metrics_a,
        "ARM_B": metrics_b,
        "ARM_C": metrics_c
    }

    # McNemar Significance Tests
    logger.info("Running McNemar statistical significance tests...")
    mcnemar_comp = {
        "ArmA_vs_ArmB_Unsafe": mcnemar_test_paired(arm_a_results, arm_b_results, "is_unsafe_recommendation"),
        "ArmA_vs_ArmC_Unsafe": mcnemar_test_paired(arm_a_results, arm_c_results, "is_unsafe_recommendation"),
        "ArmB_vs_ArmC_Unsafe": mcnemar_test_paired(arm_b_results, arm_c_results, "is_unsafe_recommendation"),
        "ArmA_vs_ArmC_Accuracy": mcnemar_test_paired(arm_a_results, arm_c_results, "is_action_correct")
    }

    report = ComparativeEvaluationReport(
        dataset_split="dev",
        num_cases=len(cases),
        arm_metrics=arm_metrics_map,
        mcnemar_comparisons=mcnemar_comp
    )

    # Save JSON summary
    json_path = output_dir / "dev_comparative_summary.json"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    logger.info(f"Saved JSON evaluation report to: {json_path}")

    # Generate Visualizations
    logger.info("Generating visualization plots...")
    plot_metrics_comparison(arm_metrics_map, output_dir / "metrics_comparison_bar.png")
    plot_confusion_matrices(arm_metrics_map, output_dir / "confusion_matrices.png")
    plot_risk_coverage(arm_metrics_map, output_dir / "risk_coverage_curve.png")

    # Generate Markdown Summary Report
    report_md_path = root / "docs" / "EVALUATION_REPORT_DEV.md"
    generate_markdown_report(report, report_md_path)
    logger.info(f"Generated Markdown report at: {report_md_path}")

    return report


def generate_markdown_report(report: ComparativeEvaluationReport, output_path: Path):
    """
    Generates a structured Markdown evaluation report summarizing comparative benchmark findings.
    """
    ma = report.arm_metrics["ARM_A"]
    mb = report.arm_metrics["ARM_B"]
    mc = report.arm_metrics["ARM_C"]

    content = fr"""# Comparative Evaluation Report (Development Dataset)

**Generated Timestamp**: {report.timestamp}  
**Dataset Split**: `{report.dataset_split}`  
**Total Clinical Cases Evaluated**: {report.num_cases}

---

## 1. Primary & Secondary Research Metrics Comparison

| Metric | Arm A (Base LLM) | Arm B (Safety Prompt) | Arm C (Proposed RAG + Safety) | Optimal Target |
| :--- | :---: | :---: | :---: | :---: |
| **Unsafe Recommendation Rate** (Primary) | **{ma.unsafe_recommendation_rate:.2%}** | **{mb.unsafe_recommendation_rate:.2%}** | **{mc.unsafe_recommendation_rate:.2%}** | **0.00%** (Lowest) |
| **Safe Abstention Rate** | {ma.safe_abstention_rate:.2%} | {mb.safe_abstention_rate:.2%} | {mc.safe_abstention_rate:.2%} | **100.00%** |
| **Clinical Answer Accuracy** | {ma.clinical_answer_accuracy:.2%} | {mb.clinical_answer_accuracy:.2%} | {mc.clinical_answer_accuracy:.2%} | **100.00%** |
| **Over-Abstention Rate** | {ma.over_abstention_rate:.2%} | {mb.over_abstention_rate:.2%} | {mc.over_abstention_rate:.2%} | **0.00%** (Lowest) |
| **Overall Action Accuracy** | {ma.overall_action_accuracy:.2%} | {mb.overall_action_accuracy:.2%} | {mc.overall_action_accuracy:.2%} | **100.00%** |

---

## 2. Statistical Significance Testing (McNemar's Chi-Squared Test)

- **Arm A vs. Arm C (Unsafe Recommendation Rate)**:
  - $\chi^2 = {report.mcnemar_comparisons['ArmA_vs_ArmC_Unsafe']['statistic_chi2']}$
  - $p\text{{-value}} = {report.mcnemar_comparisons['ArmA_vs_ArmC_Unsafe']['p_value']}$
  - Statistically Significant ($p < 0.05$): **{report.mcnemar_comparisons['ArmA_vs_ArmC_Unsafe']['significant_p_05']}**

- **Arm A vs. Arm B (Unsafe Recommendation Rate)**:
  - $\chi^2 = {report.mcnemar_comparisons['ArmA_vs_ArmB_Unsafe']['statistic_chi2']}$
  - $p\text{{-value}} = {report.mcnemar_comparisons['ArmA_vs_ArmB_Unsafe']['p_value']}$
  - Statistically Significant ($p < 0.05$): **{report.mcnemar_comparisons['ArmA_vs_ArmB_Unsafe']['significant_p_05']}**

---

## 3. Action Breakdown & Raw Counts

### Arm A (Base LLM Baseline)
- Total Non-Determinable Cases: {ma.total_non_determinable}
- Unsafe Recommendations: {ma.total_unsafe_recommendations}
- Safe Abstentions: {ma.total_safe_abstentions}
- Over-Abstentions on Determinable: {ma.total_over_abstentions}

### Arm B (Safety Prompting)
- Total Non-Determinable Cases: {mb.total_non_determinable}
- Unsafe Recommendations: {mb.total_unsafe_recommendations}
- Safe Abstentions: {mb.total_safe_abstentions}
- Over-Abstentions on Determinable: {mb.total_over_abstentions}

### Arm C (Proposed System)
- Total Non-Determinable Cases: {mc.total_non_determinable}
- Unsafe Recommendations: {mc.total_unsafe_recommendations}
- Safe Abstentions: {mc.total_safe_abstentions}
- Over-Abstentions on Determinable: {mc.total_over_abstentions}

---

## 4. Evaluation Artifacts

Generated charts saved to `experiments/eval_results/`:
- `metrics_comparison_bar.png`
- `confusion_matrices.png`
- `risk_coverage_curve.png`
- `dev_comparative_summary.json`
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    run_comparative_benchmark()
