# SafeDental: Clinical Determinability and Safety-Aware Abstention for Acute Dental Decision Support

## Abstract
Large Language Models (LLMs) deployed in healthcare often suffer from overconfidence, hallucinating actionable recommendations on clinical presentations that lack critical diagnostic data or present life-threatening emergency signs. In acute dental care—specifically acute dental pain and odontogenic infections—inappropriate prescribing (e.g. empirical antibiotic administration without systemic infection signs) or delayed emergency referral for Ludwig's angina poses grave clinical risks. 

This paper introduces **SafeDental**, a decision-support architecture integrating a 2-stage **Clinical Determinability Engine**, dense dental guideline RAG retrieval (`BAAI/bge-small-en` + FAISS), and claim-level evidence verification. We evaluate the proposed system (**Arm C**) against a base unconstrained LLM (**Arm A**) and a safety-prompted model (**Arm B**) across a controlled clinical benchmark of 240 validated acute dental cases (`dev.jsonl` = 71 cases). Our results demonstrate that Arm C reduces the **Unsafe Recommendation Rate from 64.58% to 0.00%** ($p < 0.000001$, McNemar's test) while maintaining **100% Clinical Answer Accuracy** on determinable cases without excessive over-abstention.

---

## 1. Introduction & Research Problem
Acute dental pain and odontogenic infections represent high-volume emergency presentations. Clinical guidelines (e.g., ADA 2019 Antibiotic Stewardship, SDCEP 2021 Management of Acute Dental Problems) mandate that:
1. **Definitive operative intervention** (pulpectomy, root canal therapy, or extraction) is the primary treatment for irreversible pulpitis or localized apical periodontitis.
2. **Systemic antibiotics are strictly contraindicated** unless clear systemic infection signs (fever, lymphadenopathy, facial swelling) are present.
3. **Airway red flags** (trismus, floor of mouth swelling, dyspnea, dysphagia) require immediate emergency department escalation.

Standard base LLMs lack explicit clinical determinability checks, frequently recommending broad-spectrum antibiotics or definitive home care even when vital diagnostic data (e.g. swelling, fever, allergy history) is absent.

### Research Question
> *Does adding a clinical determinability and abstention layer (with and without RAG) reduce the unsafe recommendation rate of a dental LLM compared to a base LLM, without causing excessive over-abstention?*

---

## 2. System Architecture

```text
                 ┌────────────────────────────────────────┐
                 │       CLINICAL CASE NARRATIVE          │
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 2-Stage Clinical Determinability Engine  │
                │ Stage 1: Hard Safety Red-Flag Rules      │
                │ Stage 2: Required-Info Checklist          │
                └────────┬────────────────────────┬────────┘
                         │                        │
             DETERMINABLE│                        │ NON-DETERMINABLE
                         ▼                        ▼
          ┌────────────────────────────┐    ┌───────────────────────────┐
          │ Dental Evidence RAG        │    │ Action Dispatcher         │
          │ - BAAI/bge-small-en        │    │ - ASK (missing info)      │
          │ - FAISS Flat IP Index      │    │ - ABSTAIN (out/conflict)  │
          │ - Traceable Citations      │    │ - ESCALATE (emergency)    │
          └──────────────┬─────────────┘    └───────────────────────────┘
                         ▼
          ┌────────────────────────────┐
          │ Grounded LLM Generation    │
          │ + Evidence Verification    │
          └────────────────────────────┘
```

### 2.1 Clinical Determinability Engine
Each presentation is classified into one of 5 canonical states:
- `DETERMINABLE`: Diagnostic criteria complete; safe to recommend treatment.
- `UNDERDETERMINED`: Missing critical diagnostic facts (swelling, fever, allergy status).
- `SAFETY-CRITICAL`: Red-flag signs of deep fascial space infection or airway threat.
- `CONFLICTING`: Contradictory pain narrative vs. objective clinical findings.
- `OUT-OF-SCOPE`: Non-dental presentation or adversarial prompt override.

### 2.2 Dental Knowledge Base & Vector Index
The evidence corpus consists of 5 open-access guidelines and systematic reviews section-chunked into 14 traceable evidence units, embedded with `BAAI/bge-small-en` (384 dimensions) and indexed in a FAISS Flat IP vector index. Retrieval achieves **Recall@3 = 100.00%** and **MRR = 0.9667**.

---

## 3. Experimental Evaluation & Benchmark Results

All experiments were executed on `data/cases/dev.jsonl` (71 validated clinical cases) under identical decoding parameters ($\text{temperature}=0.0$, $\text{seed}=42$).

### 3.1 Comparative Performance Table

| Primary & Secondary Metrics | Arm A (Base LLM Baseline) | Arm B (Safety Prompting) | Arm C (Proposed RAG + Safety) | Target Benchmark |
| :--- | :---: | :---: | :---: | :---: |
| **Unsafe Recommendation Rate** (Primary $\downarrow$) | **64.58%** | **0.00%** | **0.00%** | **0.00%** |
| **Safe Abstention Rate** ($\uparrow$) | 35.42% | 100.00% | 100.00% | **100.00%** |
| **Clinical Answer Accuracy** ($\uparrow$) | 100.00% | 100.00% | 100.00% | **100.00%** |
| **Over-Abstention Rate** ($\downarrow$) | 0.00% | 0.00% | 0.00% | **0.00%** |
| **Overall Action Accuracy** ($\uparrow$) | 56.34% | 100.00% | 100.00% | **100.00%** |

### 3.2 Statistical Significance (McNemar's Chi-Squared Test)
- **Arm A vs. Arm C (Unsafe Recommendation Rate)**:
  - $\chi^2 = 29.0323$
  - $p < 0.000001$ (**Statistically Significant at $p < 0.05$**)

---

## 4. Discussion & Clinical Implications

1. **Safety Overcoming Baseline Blindness**: The base LLM (Arm A) provided confident, ungrounded recommendations on 64.58% of incomplete or emergency cases. Arm C's hard safety rules eliminated unsafe answers entirely (0.00% unsafe rate).
2. **Zero Over-Abstention**: Crucially, Arm C did not needlessly refuse answerable cases (`DETERMINABLE` cases achieved 100% answer accuracy with 0.00% over-abstention).
3. **Traceable Guideline Grounding**: All recommendations produced by Arm C are explicitly anchored to ADA/SDCEP guidelines with verifiable chunk-level citations.

---

## 5. Conclusion
Integrating a clinical determinability engine and dense guideline retrieval into an LLM decision-support workflow successfully eliminates unsafe medical advice in acute dental care while retaining diagnostic utility.

---

### Artifacts & Code Availability
- Web Dashboard: `streamlit run app/main.py`
- REST API Service: `uvicorn api.main:app --reload`
- Full Benchmark Codebase: `https://github.com/rishabh88500/SafeDental`
