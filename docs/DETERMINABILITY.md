# Clinical Determinability Specification

## Overview

The **Clinical Determinability Engine** is a core novelty of the SafeDental architecture. Its sole objective is to evaluate whether a clinical case narrative contains sufficient, coherent, and safe information to generate a clinical answer, or whether the system must **ASK** for missing details, **ABSTAIN** due to conflicting/out-of-scope content, or **ESCALATE** due to safety-critical emergency red flags.

---

## 1. State to System Action Mappings

The engine classifies each clinical case into one of **5 Clinical Determinability Labels** and maps it to a **System Action**:

| Clinical Determinability Label | System Action | Clinical Intent & Flow |
| :--- | :--- | :--- |
| `DETERMINABLE` | `ANSWER` | Case contains sufficient facts. Proceed to Dental RAG retrieval and generate grounded recommendation. |
| `UNDERDETERMINED` | `ASK` | Key clinical facts missing (duration, swelling, allergies). Prompt patient/user with targeted missing fact questions. |
| `SAFETY-CRITICAL` | `ESCALATE` | Emergency red flags present (airway threat, trismus, high fever). Refuse routine advice and direct to Emergency Department / Maxillofacial Surgery. |
| `CONFLICTING` | `ABSTAIN` | Contradictory statements in narrative. Explain contradiction and advise professional examination. |
| `OUT-OF-SCOPE` | `ABSTAIN` | Non-dental query or out-of-domain (Trauma, Whitening, Orthodontics). Redirect to appropriate specialty. |

---

## 2. Two-Stage Engine Architecture

```text
                     ┌─────────────────────────────┐
                     │   Clinical Case Narrative   │
                     └──────────────┬──────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │     Input Normalization     │
                     └──────────────┬──────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌──────────────────────┐                         ┌──────────────────────┐
│  Hard Safety Rules   │                         │  Required Checklist  │
│ (config/red_flags)   │                         │(config/required_fields)│
└──────────┬───────────┘                         └──────────┬───────────┘
           │                                                │
           │  (Red Flag Triggered)                          │ (Fields Missing)
           ▼                                                ▼
┌──────────────────────┐                         ┌──────────────────────┐
│   SAFETY-CRITICAL    │                         │    UNDERDETERMINED   │
│      ESCALATE        │                         │          ASK         │
└──────────┬───────────┘                         └──────────┬───────────┘
           │                                                │
           └────────────────────────┬───────────────────────┘
                                    │ (If No Red Flags & Checklist Passed)
                                    ▼
                         ┌──────────────────────┐
                         │    LLM Classifier    │
                         │(Secondary Refinement)│
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Final Determinability│
                         │   Result & Action    │
                         └──────────────────────┘
```

### Safety-First Precedence Rule
- **Hard Safety Rules** (`config/red_flags.yaml`) ALWAYS take absolute precedence over the LLM classifier and checklist.
- If any red flag rule triggers (airway compromise, trismus, systemic infection signs), the final label MUST be `SAFETY-CRITICAL` and action MUST be `ESCALATE`.
