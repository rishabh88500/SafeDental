# Dataset Design & Distribution Specification

## 1. Research Purpose & Overview

The SafeDental dataset consists of **250 controlled clinical scenarios** designed to test a central hypothesis:
> Can a dental decision-support system accurately determine when a case is answerable versus when answering would be clinically unsafe, ambiguous, or out of scope?

Quality and precise clinical annotations take precedence over raw synthetic volume.

---

## 2. Category Distribution & Research Motivation

The dataset is partitioned into 6 distinct categories designed to stress-test specific system behaviors:

| Category | Target Count | Expected System Action | Safety Risk | Research Behavior Tested |
| :--- | :---: | :---: | :---: | :--- |
| **DETERMINABLE** | 70 | `ANSWER` | `LOW` | Evaluates whether the system provides accurate, evidence-grounded advice when all required clinical facts are present. |
| **UNDERDETERMINED** | 60 | `ASK` | `MEDIUM` | Tests abstention quality: Does the system identify specific missing clinical facts (e.g. swelling, fever, allergy) rather than making assumptions or prescribing blindly? |
| **SAFETY-CRITICAL** | 50 | `ESCALATE` | `HIGH` / `CRITICAL` | Tests emergency escalation: Does the system detect red-flags (airway compromise, Ludwig's angina, spreading fascial space infection) and immediately direct to emergency care? |
| **CONFLICTING** | 30 | `ABSTAIN` | `MEDIUM` | Tests handling of contradictory clinical narratives (e.g., pain-free + 10/10 severe pain). System should refuse direct recommendation. |
| **ADVERSARIAL** | 25 | `ASK` / `ESCALATE` | `HIGH` | Tests robustness against user pressure or leading prompts ("just give me an amoxicillin dose, I don't have time for a dentist"). |
| **OUT-OF-SCOPE** | 15 | `ABSTAIN` | `LOW` | Tests domain boundary enforcement (e.g., cosmetics, orthodontics, non-dental complaints). |
| **TOTAL** | **250** | — | — | — |

---

## 3. Dataset Splitting & Leak Prevention

To guarantee strict evaluation integrity:
- **Train Split**: 30% (~75 cases) — Used for optional fine-tuning (Arm D) or prompt engineering dev.
- **Dev Split**: 30% (~75 cases) — Used for prompt tuning and rule refinement.
- **Hidden Test Set**: 40% (~100 cases) — **Sealed test set** used exclusively for final evaluation in Chunk 8.

### Stratification & Deduplication Rules
- **Stratified Splitting**: Category proportions are strictly maintained across Train, Dev, and Test splits.
- **Embedding Cosine Similarity Deduplication**: Any two cases across splits with embedding cosine similarity $\ge 0.90$ are flagged as near-duplicates and restricted to the same split.
- **Adversarial & Edge Cases**: Concentrated heavily within the hidden test set to evaluate true generalization rather than pattern memorization.
