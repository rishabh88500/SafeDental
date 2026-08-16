import json
from pathlib import Path
from typing import Dict, List, Any
from src.utils.data_guard import load_cases_safe
from src.utils.config_loader import get_project_root
from src.data.schema import DeterminabilityLabel
from src.determinability.engine import ClinicalDeterminabilityEngine
from src.llm.client import LLMClient
from src.utils.logging import get_logger

logger = get_logger("eval_determinability_dev")


def run_dev_evaluation(force_mock: bool = True) -> Dict[str, Any]:
    """
    Evaluates ClinicalDeterminabilityEngine over data/cases/dev.jsonl (71 cases).
    Protects sealed test set.
    """
    project_root = get_project_root()
    dev_path = project_root / "data" / "cases" / "dev.jsonl"

    cases = load_cases_safe(dev_path, allow_sealed=False)
    logger.info(f"Loaded {len(cases)} dev cases from '{dev_path.name}'. Running Clinical Determinability Engine...")

    client = LLMClient(force_mock=force_mock)
    engine = ClinicalDeterminabilityEngine(llm_classifier=None)  # Uses default with LLMClient

    confusion_matrix: Dict[str, Dict[str, int]] = {
        gold.value: {pred.value: 0 for pred in DeterminabilityLabel}
        for gold in DeterminabilityLabel
    }

    total_safety_critical_gold = 0
    recalled_safety_critical = 0

    results_details: List[Dict[str, Any]] = []

    for c in cases:
        res = engine.evaluate_case(c)

        gold_lbl = c.determinability_label.value
        pred_lbl = res.label.value

        confusion_matrix[gold_lbl][pred_lbl] += 1

        if c.determinability_label == DeterminabilityLabel.SAFETY_CRITICAL:
            total_safety_critical_gold += 1
            if res.label == DeterminabilityLabel.SAFETY_CRITICAL:
                recalled_safety_critical += 1

        results_details.append({
            "case_id": c.case_id,
            "gold_label": gold_lbl,
            "predicted_label": pred_lbl,
            "gold_action": c.expected_action.value,
            "predicted_action": res.action.value,
            "is_safety_critical_correct": (gold_lbl == "SAFETY-CRITICAL" and pred_lbl == "SAFETY-CRITICAL"),
            "triggered_rules_count": len(res.triggered_rules),
            "missing_info": res.missing_info
        })

    safety_recall = (
        (recalled_safety_critical / total_safety_critical_gold) * 100.0
        if total_safety_critical_gold > 0 else 100.0
    )

    metrics = {
        "total_dev_cases": len(cases),
        "total_safety_critical_gold": total_safety_critical_gold,
        "recalled_safety_critical": recalled_safety_critical,
        "safety_recall_percentage": round(safety_recall, 2),
        "meets_safety_target": safety_recall >= 95.0,
        "confusion_matrix": confusion_matrix
    }

    logger.info(f"Dev Evaluation Complete. Safety Recall: {safety_recall:.2f}% (Target: >=95%)")

    # Save evaluation output
    out_dir = project_root / "experiments" / "determinability"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "eval_dev_results.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "case_details": results_details}, f, indent=2)

    logger.info(f"Saved evaluation results to '{out_file}'")
    return metrics


if __name__ == "__main__":
    run_dev_evaluation(force_mock=True)
