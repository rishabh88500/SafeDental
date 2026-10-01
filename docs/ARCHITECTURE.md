# SafeDental System Architecture Specification

## 1. High-Level Architectural Flow

SafeDental is structured as an end-to-end clinical decision-support pipeline that intercepts raw patient presentations, performs a two-stage determinability analysis, retrieves verifiable dental clinical evidence, and generates grounded advice while strictly abstaining or escalating when appropriate.

```text
                  ┌────────────────────────────────────────┐
                  │       CLINICAL CASE NARRATIVE          │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                 ┌──────────────────────────────────────────┐
                 │ 2-Stage Clinical Determinability Engine  │
                 │ Stage 1: Hard Safety Red-Flag Rules      │
                 │ Stage 2: 5-Point Fact Checklist          │
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

---

## 2. Clinical Determinability Subsystem

The determinability engine evaluates incoming cases against clinical guidelines to prevent ungrounded or dangerous AI generation.

### 2.1 Stage 1: Hard Safety Red-Flag Rules
Evaluates immediate life-threats and emergency presentations using regex patterns and semantic matching with clinical negation handling:
* **Airway Compromise**: Dyspnea, stridor, muffled voice, floor-of-mouth swelling, elevation of tongue.
* **Severe Trismus**: Maximum mouth opening $< 15\text{mm}$.
* **Spreading Deep Fascial Space Infections**: Bilateral submandibular, submental, or lateral pharyngeal swelling.
* **Systemic Sepsis Signs**: High fever ($> 38.5^\circ\text{C}$), lethargy, rapid progression.
* **Adversarial Prescribing Overrides**: Drug-seeking prompt injections (e.g. demanding controlled substances).
* **Clinical Negation Engine**: Employs lookback windows to prevent negative findings (e.g., *"No trismus"*, *"Afebrile"*, *"No swelling"*, *"Normal swallowing"*) from triggering false-positive emergency alerts.

### 2.2 Stage 2: 5-Point Clinical Safety Checklist
If no emergency red flags trigger, the engine evaluates completeness across 5 mandatory categories:
1. `pain_location`: Tooth number, arch, or quadrant.
2. `pain_onset_duration`: Duration in hours/days and onset characteristics.
3. `swelling_presence`: Documentation of presence, absence, or spread of swelling.
4. `fever_presence`: Measured temperature or explicit afebrile status.
5. `medical_history_allergies`: Drug allergies (penicillin, NSAIDs) and systemic conditions (diabetes, immunocompromised).

If any required item is missing $\rightarrow$ Classifies as `UNDERDETERMINED` and dispatches `ASK` with the missing categories.

### 2.3 Secondary LLM Classifier
For ambiguous narratives where regex rules are inconclusive, a lightweight prompt calls `meta-llama/llama-3.1-8b-instruct` with strict JSON schema enforcement to determine if subtle contradictions or out-of-scope conditions exist.

---

## 3. Dental Evidence Knowledge Base & RAG Subsystem

The retrieval-augmented generation subsystem grounds clinical advice in authoritative dental guidelines.

### 3.1 Guideline Corpus
Ingested from 13 open-access guidelines and systematic reviews:
* **ADA 2019**: Antibiotic Use for Urgent Management of Pulpal and Periapical Related Pain and Swelling.
* **SDCEP 2021**: Management of Acute Dental Problems (3rd Edition).
* **AAE 2020**: Guidance on Endodontic Emergencies.
* **AAOMS**: Surgical Management of Deep Fascial Space Infections.

### 3.2 Ingestion & Section-Aware Chunking
* Text documents are cleaned, stripped of navigation boilerplate, and chunked along clinical section headers (Indications, Contraindications, Dosages, Surgical Drainage).
* Chunk metadata includes source document ID, section name, guideline authority, and publication year.

### 3.3 Vector Indexing & Retrieval
* **Embedding Model**: `BAAI/bge-small-en` (384 dimensions, sentence-transformers, MIT License).
* **Index**: FAISS IndexFlatIP (Inner Product over normalized embeddings, cosine similarity equivalent).
* **Performance**: Achieves **100.00% Recall@3** and **0.967 MRR** on retrieval benchmarks.
* **Citation Formatter**: Formats retrieved evidence as traceable citations (e.g., `[ADA 2019, DOC-0001, CHK-0001-0002]`).

---

## 4. Evidence Verification Subsystem

SafeDental implements claim-level evidence verification (`src/rag/evidence_verifier.py`):
1. **Claim Extraction**: Deconstructs generated answers into discrete clinical claims.
2. **Support Verification**: Computes semantic similarity between claims and retrieved guideline chunks.
3. **Status Classification**: Classifies claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, or `NO_EVIDENCE`.
4. **Citation Audit**: Validates that all guideline citations present in the text correspond to verified chunks in the context.

---

## 5. Experimental Study Arms

To assess the impact of each subsystem, SafeDental implements three distinct experimental arms:

### Arm A: Base LLM (Baseline)
* **Pipeline**: Unconstrained prompt (`src/llm/prompts/arm_a_v1.txt`) sent directly to `meta-llama/llama-3.1-8b-instruct`.
* **Behavior**: Answers 100% of cases without determinability filtering or retrieval. Frequently recommends antibiotics for localized pulpitis (64.58% unsafe rate).

### Arm B: Determinability Gate Only (Ablation)
* **Pipeline**: 2-stage determinability gate evaluates case. If non-determinable, dispatches `ASK`, `ABSTAIN`, or `ESCALATE` immediately. If determinable, prompts LLM with safety instructions (`arm_b_v1.txt`).
* **Behavior**: Eliminates unsafe recommendations by halting on incomplete cases.

### Arm C: SafeDental Full System (Gate + RAG + Verifier)
* **Pipeline**: 2-stage determinability gate $\rightarrow$ FAISS Dental RAG retrieval $\rightarrow$ Evidence-grounded generation (`arm_c_v1.txt`) $\rightarrow$ Claim verification.
* **Behavior**: Safely answers determinable cases with guideline citations, rejects antibiotics for localized pulpitis, asks questions on missing data, and escalates emergency cases.

---

## 6. Evaluation Subsystem (OdontoEval Benchmark)

Located in `src/eval/`:
* **Dataset**: $N=240$ validated cases with stratified splits. Development evaluation conducted on $N=71$ cases (`dev.jsonl`).
* **Metrics**:
  * **Unsafe Recommendation Rate (URR)**: Primary safety metric; percentage of non-determinable cases inappropriately answered.
  * **Safe Abstention Rate (SAR)**: Percentage of non-determinable cases safely withheld, questioned, or escalated.
  * **Clinical Answer Accuracy (CAA)**: Clinical correctness on determinable cases.
  * **Over-Abstention Rate (OAR)**: Percentage of determinable cases needlessly refused.
* **Statistical Rigor**: Computes **McNemar's Paired Chi-Squared Test** with continuity correction to establish statistical significance ($p < 0.05$).

---

## 7. Application & User Interfaces

### 7.1 Streamlit Web Application (`app/main.py`)
* **Live Clinical Demonstrator**: Allows selecting between 5 validated scenarios or typing custom narratives.
* **Visual 5-Point Checklist**: Displays interactive status cards for Tooth Location, Duration, Swelling, Fever, and Allergies.
* **Side-by-Side Comparative View**: Displays Base AI (Arm A) vs SafeDental (Arm C) with risk alerts and guideline tags.
* **Benchmark & Faculty Defense Tab**: Summary KPI cards and comparative table with statistical significance metrics.
* **Guideline Knowledge Base Tab**: Summaries of ADA, SDCEP, AAE, and AAOMS clinical guidelines.

### 7.2 FastAPI REST Backend (`api/main.py`)
* `GET /health`: Health and version metadata.
* `POST /api/analyze`: Accepts case narratives and runs any pipeline arm (`ARM_A`, `ARM_B`, `ARM_C`).
* `GET /api/benchmark/summary`: Serves comparative benchmark evaluation results and metric summaries.
