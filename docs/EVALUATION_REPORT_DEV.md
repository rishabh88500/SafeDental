# Comparative Evaluation Report (Development Dataset)

**Generated Timestamp**: 2026-10-01T04:33:41.263127Z  
**Dataset Split**: `dev`  
**Total Clinical Cases Evaluated**: 5

---

## 1. Primary & Secondary Research Metrics Comparison

| Metric | Arm A (Base LLM) | Arm B (Safety Prompt) | Arm C (Proposed RAG + Safety) | Optimal Target |
| :--- | :---: | :---: | :---: | :---: |
| **Unsafe Recommendation Rate** (Primary) | **0.00%** | **0.00%** | **0.00%** | **0.00%** (Lowest) |
| **Safe Abstention Rate** | 0.00% | 0.00% | 0.00% | **100.00%** |
| **Clinical Answer Accuracy** | 100.00% | 100.00% | 100.00% | **100.00%** |
| **Over-Abstention Rate** | 0.00% | 0.00% | 0.00% | **0.00%** (Lowest) |
| **Overall Action Accuracy** | 100.00% | 100.00% | 100.00% | **100.00%** |

---

## 2. Statistical Significance Testing (McNemar's Chi-Squared Test)

- **Arm A vs. Arm C (Unsafe Recommendation Rate)**:
  - $\chi^2 = 0.0$
  - $p\text{-value} = 1.0$
  - Statistically Significant ($p < 0.05$): **False**

- **Arm A vs. Arm B (Unsafe Recommendation Rate)**:
  - $\chi^2 = 0.0$
  - $p\text{-value} = 1.0$
  - Statistically Significant ($p < 0.05$): **False**

---

## 3. Action Breakdown & Raw Counts

### Arm A (Base LLM Baseline)
- Total Non-Determinable Cases: 0
- Unsafe Recommendations: 0
- Safe Abstentions: 0
- Over-Abstentions on Determinable: 0

### Arm B (Safety Prompting)
- Total Non-Determinable Cases: 0
- Unsafe Recommendations: 0
- Safe Abstentions: 0
- Over-Abstentions on Determinable: 0

### Arm C (Proposed System)
- Total Non-Determinable Cases: 0
- Unsafe Recommendations: 0
- Safe Abstentions: 0
- Over-Abstentions on Determinable: 0

---

## 4. Evaluation Artifacts

Generated charts saved to `experiments/eval_results/`:
- `metrics_comparison_bar.png`
- `confusion_matrices.png`
- `risk_coverage_curve.png`
- `dev_comparative_summary.json`
