# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - 2026-08-20
### Added
- **Curated Demo Scenarios**: Created `data/cases/demo_cases.json` covering 5 canonical clinical behaviors (`DETERMINABLE`, `UNDERDETERMINED`, `SAFETY-CRITICAL`, `CONFLICTING`, `OUT-OF-SCOPE`).
- **Streamlit Web Dashboard**: Built interactive web application (`app/main.py`) featuring case narrative selection, arm switching (`Arm A`, `Arm B`, `Arm C`, or `Side-by-Side Comparison`), action status badges, triggered diagnostic rule audit trail, and traceable evidence citations.
- **FastAPI REST Endpoint**: Implemented REST service (`api/main.py`) with `GET /health`, `POST /api/analyze`, and `GET /api/benchmark/summary`.
- **Final Research Report**: Completed comprehensive research documentation (`docs/FINAL_RESEARCH_REPORT.md`).
- **Unit Test Suite**: Created `tests/test_ui_api.py` expanding test suite to **54 passing Pytest unit tests**.

## [0.7.0] - 2026-08-20
### Added
- **Safety & Abstention Pipeline**: Implemented Arm B (`src/pipelines/arm_b.py`) and Arm C (`src/pipelines/arm_c.py`) with claim-level evidence verification (`src/rag/evidence_verifier.py`).
- **Evaluation Schemas**: Created `src/eval/schemas.py` (`CaseEvalResult`, `ArmMetrics`, `ComparativeEvaluationReport`).
- **Evaluation Metric Engine**: Implemented `src/eval/metrics.py` supporting 4 primary metrics (Unsafe Recommendation Rate, Safe Abstention Rate, Clinical Answer Accuracy, Over-Abstention Rate) across both `PipelineResult` and `ModelResponse` objects.
- **Statistical Significance Module**: Implemented `src/eval/significance.py` (`mcnemar_test_paired`) for paired binary outcome significance testing.
- **Visualization Module**: Implemented `src/eval/visualize.py` using Matplotlib to plot grouped metric bar charts, confusion matrices, and risk-coverage curves.
- **Comparative Benchmark Execution Controller**: Implemented `src/eval/eval_benchmark.py` running Arms A, B, C on 71 dev cases, saving `experiments/eval_results/dev_comparative_summary.json` and generating `docs/EVALUATION_REPORT_DEV.md`.
- **Unit Test Expansion**: Created `tests/test_eval.py` and `tests/test_pipelines_b_c.py` expanding test suite to **50 passing Pytest unit tests**.

## [0.5.0] - 2026-08-16
### Added
- **RAG Schemas**: Created `src/rag/schemas.py` (`RetrievedChunk`, `RetrieverResult`).
- **Dense Embedding Engine**: Implemented `src/rag/embed.py` wrapping `BAAI/bge-small-en` (384 dims, MIT License).
- **FAISS Vector Indexer**: Implemented `src/rag/index.py` generating `data/index/faiss_index.bin` and `data/index/index_chunks.json`.
- **Dental Evidence Retriever**: Implemented `src/rag/retrieve.py` (`DentalRetriever`) with query normalization and traceable clinical citation formatting e.g. `[ADA 2019, DOC-0001, CHK-0001-0002]`.
- **Retrieval Benchmark**: Created `data/benchmarks/retrieval_benchmark.json` (15 query-doc pairs).
- **Retrieval Benchmark Evaluator**: Implemented `src/rag/eval_retrieval.py` achieving **Recall@3 = 100%**, **Recall@5 = 100%**, **MRR = 0.9667**.
- **Unit Tests**: Created `tests/test_rag.py` expanding test suite to 37 passing Pytest unit tests.

## [0.4.0] - 2026-08-16
### Added
- **Clinical Determinability Specification**: Created `docs/DETERMINABILITY.md` defining 2-stage architecture and label-to-action mappings.
- **Determinability Schemas**: Implemented `src/determinability/schemas.py` (`RuleTrigger`, `ChecklistCoverage`, `LLMClassification`, `DeterminabilityResult`).
- **Hard Safety Red-Flag Rules**: Implemented `src/determinability/rules.py` evaluating airway compromise, systemic infection, spreading fascial space infections, and adversarial prompt overrides.
- **Required-Information Checklist Evaluator**: Implemented `src/determinability/checklist.py` evaluating chief complaint, clinical signs, and medical history.
- **Secondary LLM Classifier**: Implemented `src/determinability/llm_classifier.py` returning structured JSON classification.
- **Combiner Engine**: Implemented `src/determinability/engine.py` enforcing Safety-First Precedence Rules.
- **Dev Set Evaluator**: Implemented `src/determinability/eval_dev.py` achieving **100.00% Safety Recall** on `SAFETY-CRITICAL` cases in `dev.jsonl` (71 cases).
- **Unit Tests**: Added `tests/test_determinability.py` (32/32 tests passing).

## [0.3.0] - 2026-08-16
### Added
- **KB Governance Policy**: Created `docs/KB_SOURCE_POLICY.md` establishing open-access licensing and document tracking standards.
- **Knowledge Base Pipeline**: Implemented `src/kb/ingest.py`, `src/kb/clean_text.py`, `src/kb/chunk.py`, `src/kb/manifest.py`, `src/kb/index.py`, and `src/kb/populate_corpus.py`.
- **Dental Evidence Corpus**: Ingested, cleaned, section-chunked, and indexed 5 core clinical guidelines and consensus documents into 14 traceable chunks.
- **Sealed Test Set Protection**: Implemented `src/utils/data_guard.py` enforcing automated access protection against reading `data/cases/test.jsonl`.
- **Frozen LLM Client**: Implemented `src/llm/client.py` wrapping Ollama API with deterministic Mock engine fallback.
- **Arm A Baseline Pipeline**: Implemented `src/pipelines/arm_a.py` and experiment recorder `src/utils/experiment.py`.
- **Arm A Development Run**: Executed Arm A baseline on `data/cases/dev.jsonl` (71 cases), saving artifacts to `experiments/arm_a/exp_arma_dev_v1/`.
- **Unit Test Suite Expansion**: Added tests in `tests/test_data_guard.py`, `test_kb_ingest.py`, `test_kb_clean.py`, `test_kb_chunk.py`, `test_kb_manifest.py`, `test_llm_client.py`, and `test_arm_a_pipeline.py` (23/23 passing).

## [0.2.0] - 2026-08-16
### Added
- Dataset Design, Schema, Validator, Deduplicator, Splitter, and 240 controlled clinical scenarios.
