# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.2.0] - 2026-10-14
### Added
- **20,000-Case Scale Benchmark Expansion**: Scaled synthetic case generation to 20,000 clinically stratified acute dental cases (`data/benchmarks/benchmark_20000_cases.jsonl`) and 20,000 retrieval queries (`data/benchmarks/retrieval_benchmark_20000.json`), doubling the evaluation scale from 10,000 to 20,000 cases.
- **Enriched Clinical Archetypes**: Expanded scenario generators in `src/data/scale_generator.py` with localized pericoronitis, cracked tooth syndrome, surgical timeline inquiries, pregnancy-specific contraindications, cavernous sinus thrombosis emergencies, and odontogenic sepsis presentations.
- **Parametric Scale Benchmark Execution**: Enhanced `src/eval/scale_benchmark.py` and `scripts/run_scale_benchmark.py` with `--count` and `--force-regenerate` parameters, supporting seamless execution at arbitrary sample counts (10,000, 20,000+).
- **20,000 Benchmark Results & Visualizations**: Produced `docs/BENCHMARK_20000_SCALE_REPORT.md`, summary JSON `experiments/eval_results/benchmark_20000_summary.json`, and 3 publication-ready 300 DPI visualizations (`scale_20000_metrics_comparison.png`, `scale_20000_confusion_matrix.png`, `scale_20000_latency_percentiles.png`).
- **Complete 20,000-Row Auditing CSV**: Built `scripts/generate_side_by_side_csv.py --count 20000` outputting a comprehensive 20,000-row audit spreadsheet (`experiments/eval_results/benchmark_20000_side_by_side_comparison.csv`, 14.9 MB) with verbatim responses and verdicts across Arm A, Arm B, and Arm C.
- **Zero-Failure Safety at 20,000 Scale**: Confirmed 0 missed red flags across 3,000 life-threatening emergencies (100% emergency escalation sensitivity), collapse of unsafe recommendation rate from 92.86% to 0.00% (McNemar $\chi^2 = 12999.0, p < 0.0001$), and sustained FAISS throughput of 814.3 QPS.
- **Updated Presentation Decks & Reports**: Re-generated `reports/SafeDental_20000_Benchmark_Presentation.pptx` and `reports/SafeDental_Complete_Project_and_Benchmark_Report.docx` incorporating 20,000 benchmark evidence.

## [1.1.0] - 2026-10-11
### Added
- **Google Gemini API Provider Integration**: Configured direct integration with Google AI Studio via `GeminiClient` in `src/llm/client.py` using `gemini-3.8-flash` with zero-latency thinking budget (`thinkingConfig: {"thinkingBudget": 0}`) and automatic resilient fallback to `gemini-3.1-flash-lite`.
- **High-Scale Clinical Dataset Generator**: Implemented `src/data/scale_generator.py` generating 10,000 evidence-anchored acute dental scenarios (`data/benchmarks/benchmark_10000_cases.jsonl`) and 10,000 dense retrieval queries (`data/benchmarks/retrieval_benchmark_10000.json`).
- **High-Throughput Scale Benchmark Engine**: Built `src/eval/scale_benchmark.py` and CLI `scripts/run_scale_benchmark.py` executing multi-tier benchmarking (FAISS vector retrieval, determinability gating, and 3-arm clinical pipeline comparison) with concurrent thread pools and LRU query vector caching.
- **10,000 Query Benchmark Report & Visualizations**: Produced `docs/BENCHMARK_10000_SCALE_REPORT.md`, summary dataset `experiments/eval_results/benchmark_10000_summary.json`, and 3 publication-ready visualizations (`scale_10000_metrics_comparison.png`, `scale_10000_confusion_matrix.png`, `scale_10000_latency_percentiles.png`).
- **Zero Missed Red Flags at Scale**: Validated 100% emergency escalation sensitivity (0 missed red flags across 1,500 acute emergencies) and complete elimination of unsafe clinical recommendations (0.00% unsafe rate in Arm C vs. 94.64% in Arm A, McNemar $\chi^2 = 6624.0, p < 0.001$).

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
