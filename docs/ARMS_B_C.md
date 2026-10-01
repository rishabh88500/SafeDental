# Arms B & C Architecture Specification

## Overview

This document specifies the design, decision gates, context formatting, evidence verification, and experimental controls for **Arm B (Safety Prompting)** and **Arm C (Proposed System: Safety Gate + Dental RAG + Evidence Verification)**.

---

## 1. Experimental Arms Design & Fairness Controls

To ensure interpretable scientific comparison, all three experimental arms share identical base variables:

| Controlled Parameter | Arm A (Baseline) | Arm B (Safety) | Arm C (Proposed System) |
| :--- | :--- | :--- | :--- |
| **Base LLM Model** | `meta-llama/llama-3.1-8b-instruct` | `meta-llama/llama-3.1-8b-instruct` | `meta-llama/llama-3.1-8b-instruct` |
| **Inference Provider** | OpenRouter (`https://openrouter.ai/api/v1`) | OpenRouter (`https://openrouter.ai/api/v1`) | OpenRouter (`https://openrouter.ai/api/v1`) |
| **Sampling Params** | `temp=0.0`, `max_tokens=512`, `seed=42` | `temp=0.0`, `max_tokens=512`, `seed=42` | `temp=0.0`, `max_tokens=512`, `seed=42` |
| **Evaluation Dataset** | `data/cases/dev.jsonl` (71 cases) | `data/cases/dev.jsonl` (71 cases) | `data/cases/dev.jsonl` (71 cases) |
| **Determinability Gate**| None (Unconstrained) | Active (`determinability_engine`) | Active (`determinability_engine`) |
| **Dental RAG Evidence** | None | None | Active (`DentalRetriever` + FAISS) |
| **Evidence Verifier** | None | None | Active (`evidence_verifier`) |

---

## 2. Arm B Architecture & Decision Gate

```text
Clinical Case
     │
     ▼
Determinability Engine
     │
     ├── ASK (Underdetermined) ────────► Return ASK + missing_info (No LLM call)
     ├── ABSTAIN (Conflicting/Scope) ──► Return ABSTAIN + rationale (No LLM call)
     ├── ESCALATE (Safety-Critical) ───► Return ESCALATE + emergency notice (No LLM call)
     │
     └── ANSWER (Determinable)
            │
            ▼
     Base LLM (arm_b_v1.txt)
            │
            ▼
     Final Arm B Response
```

### Key Safety Property
For non-answerable cases (`ASK`, `ABSTAIN`, `ESCALATE`), Arm B stops immediately at the determinability decision gate without making unnecessary LLM generation calls.

---

## 3. Arm C Architecture & RAG Pipeline

```text
Clinical Case
     │
     ▼
Determinability Engine
     │
     ├── ASK / ABSTAIN / ESCALATE ───► Stop Immediately (No LLM / No RAG)
     │
     └── ANSWER (Determinable)
            │
            ▼
     Dental Retriever (FAISS)
            │
            ▼
     Context Builder (context_builder.py)
            │
            ▼
     Base LLM (arm_c_v1.txt)
            │
            ▼
     Evidence Verifier (evidence_verifier.py)
            │
            ▼
     Final Arm C Response
```

---

## 4. Evidence Context & Verification Schema

- **Context Builder**: Formats `RetrievedChunk` objects into explicit `[EVIDENCE N]` blocks with citation IDs e.g. `[ADA 2019, DOC-0001, CHK-0001-0002]`.
- **Claim Support States**:
  - `SUPPORTED`: Claim is fully supported by retrieved evidence text.
  - `PARTIALLY_SUPPORTED`: Claim is partially supported with minor gaps.
  - `UNSUPPORTED`: Claim makes ungrounded assertions.
  - `NO_EVIDENCE`: Claim is made without matching evidence citations.
- **Citation Correctness**: Evaluates whether cited chunk IDs actually support the claim made.
