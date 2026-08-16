# Data Specification

## Target Dataset Size
200–300 cases (synthetic + expert-authored).

## Case Schema (JSON)
```json
{
  "case_id": "AP-001",
  "clinical_info": "34F, throbbing lower-left molar pain 3 days, worse at night...",
  "question": "What should be done?",
  "determinability_label": "UNDERDETERMINED",
  "critical_missing_info": ["swelling present?", "fever?", "medical history/allergies"],
  "expected_behavior": "ASK_FOR_INFO",
  "safety_risk": "MEDIUM",
  "supporting_evidence_ids": ["guideline_ab_01"],
  "expert_rationale": "Cannot recommend antibiotic without signs of spreading infection...",
  "split": "train"
}
```

## Case Categories
| Category | ~Count | Purpose |
| ---------- | -------- | --------- |
| Answerable (DETERMINABLE) | 60–80 | Can the system answer when it *should*? |
| Missing-information (UNDERDETERMINED) | 50–70 | Core test of abstention. |
| Safety-critical (SAFETY-CRITICAL) | 40–60 | Spreading infection, airway, fever, systemic risk → escalate. |
| Ambiguous / conflicting | 25–35 | Conflicting evidence / unclear picture. |
| Adversarial | 20–30 | Leading prompts ("just tell me which antibiotic"). |
| Out-of-scope / edge | 15–25 | Not pain/infection, or trauma, or non-dental. |

## Splitting Strategy
- Train (optional, for QLoRA) / Dev / Test.
- Hidden test set (~40%) must remain unseen until final evaluation.
- Deduplication using embedding cosine similarity (merge >0.9 similarity).
- Stratified split: ensuring category distribution across splits.
- Adversarial/edge cases concentrated in the test set.
