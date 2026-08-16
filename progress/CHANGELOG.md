# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
