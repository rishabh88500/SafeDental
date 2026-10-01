import math
from typing import List, Dict, Any
from src.eval.schemas import CaseEvalResult


def mcnemar_test_paired(
    arm1_results: List[CaseEvalResult],
    arm2_results: List[CaseEvalResult],
    target_metric: str = "is_unsafe_recommendation"
) -> Dict[str, Any]:
    """
    Computes McNemar's test for paired binary outcomes on identical cases across two experimental arms.
    
    Target metric options:
      - 'is_unsafe_recommendation'
      - 'is_action_correct'
      - 'is_safe_abstention'
    """
    # Align by case_id
    arm1_map = {r.case_id: r for r in arm1_results}
    arm2_map = {r.case_id: r for r in arm2_results}
    common_case_ids = sorted(list(set(arm1_map.keys()).intersection(set(arm2_map.keys()))))

    if not common_case_ids:
        raise ValueError("No common case_ids found between the two arms for McNemar test.")

    # Contingency Table:
    # n_11: both True
    # n_10: Arm 1 True, Arm 2 False  (b)
    # n_01: Arm 1 False, Arm 2 True  (c)
    # n_00: both False
    b = 0
    c = 0
    both_true = 0
    both_false = 0

    for cid in common_case_ids:
        v1 = bool(getattr(arm1_map[cid], target_metric))
        v2 = bool(getattr(arm2_map[cid], target_metric))

        if v1 and not v2:
            b += 1
        elif not v1 and v2:
            c += 1
        elif v1 and v2:
            both_true += 1
        else:
            both_false += 1

    total_discordant = b + c
    if total_discordant == 0:
        statistic = 0.0
        p_value = 1.0
    else:
        # Edwards' continuity correction formula
        statistic = ((abs(b - c) - 0.5) ** 2) / total_discordant
        # Compute 1-df chi-squared p-value approximation using math.erf
        # P(X^2 >= stat) = 2 * (1 - norm.cdf(sqrt(stat)))
        z = math.sqrt(statistic)
        p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(z / math.sqrt(2.0))))

    is_significant_p05 = bool(p_value < 0.05)
    is_significant_p01 = bool(p_value < 0.01)

    return {
        "target_metric": target_metric,
        "arm1": arm1_results[0].arm if arm1_results else "ARM_1",
        "arm2": arm2_results[0].arm if arm2_results else "ARM_2",
        "n_common_cases": len(common_case_ids),
        "b_arm1_true_arm2_false": b,
        "c_arm1_false_arm2_true": c,
        "both_true": both_true,
        "both_false": both_false,
        "statistic_chi2": round(statistic, 4),
        "p_value": round(p_value, 6),
        "significant_p_05": is_significant_p05,
        "significant_p_01": is_significant_p01
    }
