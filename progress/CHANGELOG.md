# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
