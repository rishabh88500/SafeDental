# SafeDental Development & Operations Guide

## 1. Project Overview & Core Principles

SafeDental is a clinical decision-support and safety architecture for acute dental pain and odontogenic infections.

### The Golden Rule of Evaluation
> A **completed, honestly evaluated comparison** across all study arms—demonstrating real trade-offs between safety, abstention, and clinical utility—is a **far stronger project** than an unevaluated or unconstrained model.

### Locked Research Boundaries
* **Domain**: Acute dental pain and odontogenic infection ONLY.
* **Modality**: Text-only clinical case narratives.
* **Safety First**: Never allow an LLM to guess dosages or advise definitive treatment when essential clinical facts are missing.
* **Guideline Grounding**: All clinical recommendations must align with peer-reviewed evidence (ADA 2019, SDCEP 2021).

---

## 2. Environment Setup

### Prerequisites
* Python 3.9, 3.10, or 3.11
* Virtual environment tool (`venv` or `conda`)
* macOS or Linux

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/rishabh88500/SafeDental.git
cd SafeDental

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration (`.env`)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Populate your OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```
*(Note: If no API key is set, the system automatically falls back to the deterministic Mock Engine for testing and evaluation).*

---

## 3. Running System Components

### 1. Interactive Streamlit Web Dashboard
Runs the live 3-tab decision support UI on port 8501:
```bash
streamlit run app/main.py
```
Access at: **http://localhost:8501**

### 2. FastAPI REST API Service
Runs the backend REST service on port 8000:
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive Swagger documentation: **http://localhost:8000/docs**

### 3. OdontoEval Benchmark Evaluation
Executes the comparative evaluation across Arm A, Arm B, and Arm C on the development dataset:
```bash
python -m src.eval.eval_benchmark
```
Outputs are generated in `experiments/eval_results/` and `docs/EVALUATION_REPORT_DEV.md`.

### 4. Running Automated Tests
Execute the Pytest test suite:
```bash
pytest -v
```

---

## 4. Key CLI Scripts & Utilities

* **Inspect Knowledge Base Ingestion**:
  ```bash
  python -m src.kb.ingest
  python -m src.kb.populate_corpus
  ```
* **Build FAISS Vector Index**:
  ```bash
  python -m src.rag.index
  ```
* **Run RAG Retrieval Benchmark**:
  ```bash
  python -m src.rag.eval_retrieval
  ```
* **Run Arm A Baseline Pipeline**:
  ```bash
  python -m src.pipelines.run_arm_a_dev
  ```

---

## 5. Development Best Practices & Safety Guards

1. **Sealed Test Set Protection**: Never import or read `data/cases/test.jsonl` during development or training. Any access attempt is guarded by `src/utils/data_guard.py` and will raise `SealedTestAccessError`.
2. **Clinical Negation Handling**: Always verify that clinical keywords are evaluated with negation checks (e.g. `is_negated()` in `src/determinability/rules.py`) so negative findings like *"No trismus"* or *"Afebrile"* do not trigger false alerts.
3. **Traceable Citations**: Always maintain chunk identifiers when adding or modifying knowledge base documents in `data/knowledge_base/`.
