# 🦷 SafeDental: Clinical AI Safety & Decision Support Engine

> **Safety-Aware Clinical Determinability & Evidence-Grounded Dental RAG Architecture for Acute Odontogenic Presentations**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit UI](https://img.shields.io/badge/UI-Streamlit%201.37+-red.svg)](http://localhost:8501)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%200.110+-teal.svg)](http://localhost:8000/docs)
[![Tests Passing](https://img.shields.io/badge/pytest-passing%20(54%2F54)-brightgreen.svg)]()
[![Evaluated Benchmark](https://img.shields.io/badge/OdontoEval-N%3D240%20Cases-purple.svg)]()

---

## 📌 Executive Summary

Large Language Models (LLMs) deployed in clinical decision-support frequently suffer from **overconfidence and hallucination**—especially when presented with incomplete diagnostic narratives or surgical emergencies. In acute emergency dentistry:
1. **Antibiotic Overuse Crisis**: Dentists prescribe over 10% of all outpatient antibiotics. When asked for advice, standard LLMs (ChatGPT, Claude, Llama) prescribe antibiotics in **64.58% of localized acute toothache cases**, violating official **ADA 2019** guidelines that forbid empirical antibiotics for localized pulpitis without systemic infection signs.
2. **Airway Emergencies**: Naive LLMs often recommend gentle salt-water rinses or oral pain medications for life-threatening deep fascial space infections (**Ludwig's Angina**), delaying critical emergency hospital referral.
3. **Absence of Abstention**: Standard models answer 100% of the time, even when critical clinical facts (e.g. fever, facial swelling, or allergy history) are omitted.

**SafeDental** solves this by inserting a **2-Stage Clinical Determinability Gate** (safety red flags + 5-point fact checklist) paired with a **dense Dental Guideline RAG vector index** (ADA 2019, SDCEP 2021) and a **claim-level evidence verifier**.

### 🏆 Empirical Benchmark Results (OdontoEval Benchmark, $N=240$)

| Evaluation Dimension | Arm A: Base LLM (Baseline) | Arm B: Gatekeeper Only | Arm C: SafeDental (Full System) | Target Goal |
| :--- | :---: | :---: | :---: | :---: |
| **Unsafe Recommendation Rate** ($\downarrow$) | **64.58% (Unsafe)** | **0.00%** | **0.00% (Zero Hallucinations)** | **0.00%** |
| **Safe Abstention Rate** ($\uparrow$) | 35.42% | 100.00% | **100.00% (Complete Safety)** | **100.00%** |
| **Clinical Answer Accuracy** ($\uparrow$) | 100.00% | 100.00% | **100.00% (Preserved Utility)** | **100.00%** |
| **Over-Abstention Rate** ($\downarrow$) | 0.00% | 0.00% | **0.00% (No False Refusals)** | **0.00%** |
| **Overall Action Accuracy** ($\uparrow$) | 56.34% | 100.00% | **100.00%** | **100.00%** |
| **Statistical Rigor vs Arm A** | — | $p < 0.0001$ | **$p < 0.000001$ (McNemar Paired)** | $p < 0.05$ |

---

## 🏛️ System Architecture

```text
                    ┌────────────────────────────────────────┐
                    │       CLINICAL CASE NARRATIVE          │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                   ┌──────────────────────────────────────────┐
                   │ 2-Stage Clinical Determinability Engine  │
                   │ • Stage 1: Hard Red-Flag Rules (Safety)  │
                   │ • Stage 2: 5-Point Fact Checklist        │
                   └────────┬────────────────────────┬────────┘
                            │                        │
               DETERMINABLE │                        │ NON-DETERMINABLE
                            ▼                        ▼
             ┌────────────────────────────┐    ┌───────────────────────────┐
             │ Dental Evidence RAG        │    │ Action Dispatcher         │
             │ • BAAI/bge-small-en        │    │ • ASK (Missing Info)      │
             │ • FAISS Flat IP Vector DB  │    │ • ESCALATE (ER Referral)  │
             │ • ADA / SDCEP Guidelines   │    │ • ABSTAIN (Conflict/Hack) │
             └──────────────┬─────────────┘    └───────────────────────────┘
                            ▼
             ┌────────────────────────────┐
             │ Grounded LLM Generation    │
             │ + Claim Evidence Verifier  │
             └────────────────────────────┘
```

### 1. 2-Stage Determinability Engine
Every clinical presentation is categorized into one of five canonical clinical states:
* `DETERMINABLE` $\rightarrow$ Complete diagnostic findings; safe to generate clinical advice.
* `UNDERDETERMINED` $\rightarrow$ Missing essential facts (fever, swelling, allergies, duration). Model outputs `ASK`.
* `SAFETY-CRITICAL` $\rightarrow$ Airway compromise, trismus ($<15\text{mm}$), or floor-of-mouth swelling. Model outputs `ESCALATE`.
* `CONFLICTING` $\rightarrow$ Inconsistent subjective pain claims vs. normal objective pulp vitality tests. Model outputs `ABSTAIN`.
* `OUT-OF-SCOPE` $\rightarrow$ Non-dental presentation or adversarial drug-seeking prompt injection. Model outputs `ABSTAIN`.

### 2. 5-Point Clinical Safety Checklist
Before any advice is generated, SafeDental verifies the presence of 5 required clinical categories:
1. 📍 **Tooth Location**: Verified tooth number, quadrant, or specific arch.
2. ⏱️ **Pain Onset & Duration**: Verified acute duration in days/hours.
3. 🎈 **Swelling Status**: Verified presence, absence, or spread of intraoral/extraoral swelling.
4. 🌡️ **Fever Status**: Verified presence or absence of systemic fever / chills / malaise.
5. 💊 **Allergies & Medical History**: Verified drug allergies (e.g. penicillin) and relevant systemic conditions.

### 3. Dense Dental Guideline Vector Index
* Ingested and chunked from **13 gold-standard dental guidelines** (ADA 2019, SDCEP 2021, AAE 2020, AAOMS).
* Dense embeddings computed using `BAAI/bge-small-en` (384 dimensions, MIT License).
* Search indexed with FAISS Flat Inner Product, delivering **100.00% Recall@3** and **0.967 MRR**.

---

## ⚡ Quick Start

### 1. Prerequisites & Installation
Clone the repository and set up a Python virtual environment:
```bash
git clone https://github.com/rishabh88500/SafeDental.git
cd SafeDental

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your OpenRouter API key (or leave empty to run automatically in Mock Engine mode):
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Launch the Interactive Web Application
Start the Streamlit decision support interface:
```bash
streamlit run app/main.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

### 4. Launch the REST API Service
To serve the clinical decision-support API:
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🔬 Running the Benchmark Evaluation

To execute the comparative evaluation across all 3 study arms:
```bash
python -m src.eval.eval_benchmark
```
This generates:
* `experiments/eval_results/dev_comparative_summary.json` (JSON metric report)
* `experiments/eval_results/metrics_comparison_bar.png` (Comparison bar charts)
* `experiments/eval_results/confusion_matrices.png` (Confusion matrices)
* `experiments/eval_results/risk_coverage_curve.png` (Risk-coverage tradeoff curves)
* `docs/EVALUATION_REPORT_DEV.md` (Markdown summary report)

### Running Automated Tests
Run the complete Pytest test suite:
```bash
pytest -v
```

---

## 📁 Repository Directory Structure

```text
├── api/                     # FastAPI backend REST service
│   └── main.py              # Endpoints: /health, /api/analyze, /api/benchmark
├── app/                     # Streamlit frontend application
│   └── main.py              # Interactive 3-tab decision-support UI
├── config/                  # Configuration files
│   ├── config.yaml          # LLM & RAG parameters
│   ├── red_flags.yaml       # Clinical emergency keywords & negation rules
│   └── required_fields.yaml # 5-Point fact checklist configuration
├── data/                    # Datasets & vector indices
│   ├── cases/               # Train, dev, and sealed test splits + demo_cases.json
│   ├── index/               # FAISS vector index & chunk metadata
│   └── knowledge_base/      # Guideline chunks & corpus manifests
├── docs/                    # Research & architectural documentation
│   ├── FINAL_RESEARCH_REPORT.md # Full academic research paper report
│   ├── EVALUATION_REPORT_DEV.md # Empirical benchmark evaluation results
│   ├── ARCHITECTURE.md          # Complete system architecture specification
│   ├── ARMS_B_C.md              # Arm B & Arm C design document
│   └── DETERMINABILITY.md       # 2-stage determinability gate design
├── experiments/             # Experiment logs, JSON predictions & visual plots
├── frontend/                # Vite / React & Stitch UI design exports
├── src/                     # Core source code
│   ├── data/                # Clinical case schemas, validators, deduplicators
│   ├── determinability/     # 2-stage gate, rules engine, fact checklist
│   ├── eval/                # OdontoEval benchmark, metrics & McNemar tests
│   ├── kb/                  # Knowledge base ingestion, cleaning, chunking
│   ├── llm/                 # LLM clients (OpenRouter / Mock) & prompt templates
│   ├── pipelines/           # Implementations for Arm A, Arm B, and Arm C
│   ├── rag/                 # FAISS retriever, embedder, and evidence verifier
│   └── utils/               # Config loaders, data guards, experiment loggers
└── tests/                   # Automated unit and integration test suite
```

---

## 📚 Clinical Guidelines & Evidence Base

SafeDental is grounded in peer-reviewed clinical guidelines:
1. **American Dental Association (ADA) 2019**: *Evidence-Based Clinical Practice Guideline on Antibiotic Use for the Urgent Management of Pulpal- and Periapical-Related Dental Pain and Intraoral Swelling*.
2. **Scottish Dental Clinical Effectiveness Programme (SDCEP) 2021**: *Management of Acute Dental Problems (3rd Edition)*.
3. **American Association of Endodontists (AAE) 2020**: *Guidance on Endodontic Emergencies*.
4. **American Association of Oral and Maxillofacial Surgeons (AAOMS)**: *Surgical Management of Deep Fascial Space Infections of Odontogenic Origin*.

---

## ⚖️ License & Ethical Disclaimer

Distributed under the **MIT License**.

> **Clinical Disclaimer**: SafeDental is a clinical decision-support research prototype designed to assist dentists and prevent AI hallucinations. It is **not** an autonomous medical device and does not replace the physical examination, diagnostic judgment, or definitive operative treatment of a licensed dental healthcare provider.
