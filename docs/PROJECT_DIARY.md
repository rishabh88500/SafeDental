# SafeDental Research Project Diary

**Project Name**: SafeDental  
**Domain**: Acute Dental Pain & Odontogenic Infection Decision-Support  
**Repository**: `/Users/rishabhsingh/Desktop/MAJOR PROJ`  

---

## Log Entries

### Entry 1 — 2026-08-16: Phase 0 & Phase 1 — Repository & Memory System Setup
- **Objectives**: Complete deep inspection of `wholeplan.md`, establish locked project boundaries, scaffold workspace directory structure, and initialize persistent project memory system.
- **Accomplished**:
  - Scaffolded directories: `docs/`, `progress/`, `config/`, `data/`, `src/`, `tests/`, `experiments/`, `app/`, `scripts/`.
  - Created core documentation: `docs/PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/DECISIONS.md`, `docs/DATA_SPEC.md`, `docs/DEVELOPMENT_GUIDE.md`.
  - Established progress tracker in `progress/PROGRESS.md`, `progress/CURRENT_TASK.md`, `progress/CHANGELOG.md`, and `progress/BLOCKERS.md`.

---

### Entry 2 — 2026-08-16: Chunk 1 — Research Protocol & Foundation
- **Objectives**: Freeze scientific research protocol, define mathematical formulas for evaluation metrics, define the 5 clinical determinability labels with examples, and build central configuration & utility modules.
- **Accomplished**:
  - Finalized `docs/RESEARCH_PROTOCOL.md` with explicit RQ, hypotheses ($H_1$ to $H_4$, $H_0$), experimental arms (A, B, C, D optional), and mathematical formulas for $Acc$, $SAR$, $URR$, $URR_{critical}$, $OAR$, $Recall@k$, $ES$, $CC$, $HR$.
  - Created `docs/LABEL_DEFINITIONS.md` defining `DETERMINABLE`, `UNDERDETERMINED`, `SAFETY-CRITICAL`, `CONFLICTING`, and `OUT-OF-SCOPE` with 2 clinical examples each.
  - Created `config/config.yaml`, `config/red_flags.yaml`, `config/required_fields.yaml`, and `requirements.txt`.
  - Implemented `src/utils/config_loader.py` and `src/utils/logging.py`.
  - Implemented unit test suite in `tests/test_config_loader.py` and `tests/test_logging.py` (6 passing tests).

---

### Entry 3 — 2026-08-16: Chunk 2 — Dataset & Annotation Pipeline
- **Objectives**: Create a canonical JSON schema and Pydantic v2 models, build dataset generation, schema validation, similarity deduplication, and stratified splitting pipeline; seal the hidden test set.
- **Accomplished**:
  - Created `docs/DATASET_DESIGN.md` (250 scenario target distribution across 6 categories) and `docs/annotation_guidelines.md`.
  - Defined Draft-07 `data/schema/case_schema.json` and matching `src/data/schema.py` (`ClinicalCase`, `PatientContext`, `DeterminabilityLabel`, `ExpectedAction`, `SafetyRisk`).
  - Built `src/data/validate_schema.py`, `src/data/dedupe.py` (with SequenceMatcher fallback), `src/data/split.py`, and `src/data/generate_cases.py`.
  - Generated and validated 240 controlled clinical scenarios:
    - Validated store: `data/cases/validated/cases.jsonl` (240 total cases)
    - Train split: `data/cases/train.jsonl` (71 cases / 30%)
    - Dev split: `data/cases/dev.jsonl` (71 cases / 30%)
    - Hidden Test Set (Sealed): `data/cases/test.jsonl` (98 cases / 40%)
  - Expanded test suite to 13 passing unit tests.

---

### Entry 4 — 2026-08-16: Chunk 3 — Dental Evidence Knowledge Base & Governance
- **Objectives**: Create KB source policy, immutable raw storage, text cleaning, section-aware chunking, manifest generator, and minimal dense index.
- **Accomplished**:
  - Created `docs/KB_SOURCE_POLICY.md` specifying licensing, source authority, and metadata requirements (`DOC-XXXX`).
  - Implemented `src/kb/ingest.py`, `src/kb/clean_text.py`, `src/kb/chunk.py`, `src/kb/manifest.py`, `src/kb/index.py`, and `src/kb/populate_corpus.py`.
  - Ingested 5 core clinical guidelines and consensus papers (ADA, SDCEP, AAOMS, JADA, NICE) into 14 traceable chunks in `data/knowledge_base/`.
  - Built manifest `data/knowledge_base/manifests/manifest.json` and index metadata `data/knowledge_base/index/index_meta.json`.

---

### Entry 5 — 2026-08-16: Chunk 4 — Frozen Base LLM & Arm A Baseline Pipeline
- **Objectives**: Build sealed test set protection guard, frozen LLM client, versioned baseline prompt, Arm A baseline pipeline, and execute dev baseline run.
- **Accomplished**:
  - Implemented `src/utils/data_guard.py` (`SealedTestAccessError`) ensuring `data/cases/test.jsonl` remains completely unread during development.
  - Implemented `src/llm/client.py` wrapping Ollama (`llama3.1:8b-instruct`) with deterministic Mock engine fallback.
  - Created system prompt `src/llm/prompts/arm_a_v1.txt` and normalized response schema `src/llm/schemas.py`.
  - Implemented `src/pipelines/arm_a.py` and experiment recorder `src/utils/experiment.py`.
  - Executed Arm A baseline dev run on `data/cases/dev.jsonl` (71 cases) and saved reproducible experiment artifacts in `experiments/arm_a/exp_arma_dev_v1/`.
  - Expanded test suite to 23 passing unit tests.

---

### Entry 6 — 2026-08-16: Git Initialization & Repository Commit
- **Objectives**: Initialize Git repository and commit all foundation, dataset, KB, pipeline, and test files.
- **Accomplished**:
  - Created `.gitignore` ignoring caches, environments, and logs.
  - Initialized Git repository (`git init`).
  - Created root commit: `feat: complete Chunk 1, Chunk 2, Chunk 3, and Chunk 4 implementation` (`805fab7`).

---

### Entry 7 — 2026-08-16: Claude Opus 5.5 Model Integration & Security Hardening
- **Objectives**: Integrate Anthropic Claude API (`https://api.anthropic.com/v1`) using `claude-opus-5.5`, implement strict API key security governance via environment variables, and create `.env.example`.
- **Accomplished**:
  - Created `.env.example` defining `ANTHROPIC_API_KEY=your_key_here` and verified `.env` exclusion in `.gitignore`.
  - Updated `config/config.yaml` and `src/utils/config_loader.py` to support `claude` provider, model ID `claude-opus-5.5`, base URL `https://api.anthropic.com/v1`, and 60s timeout.
  - Implemented provider-agnostic `LLMClient` and `ClaudeClient` in `src/llm/client.py` with automatic fallback to Mock Engine.
  - Expanded unit test suite to 25 passing Pytest unit tests.

---

### Entry 8 — 2026-08-16: Chunk 5 — Clinical Determinability Engine Implementation
- **Objectives**: Build 2-stage Clinical Determinability Engine (Hard Safety Red Flags + Fact Checklist + Secondary LLM Classifier) enforcing Safety-First Precedence Rules; evaluate on dev set to achieve >=95% Safety Recall.
- **Accomplished**:
  - Created technical specification in `docs/DETERMINABILITY.md` detailing the 2-stage architecture and label-to-action mappings.
  - Implemented `src/determinability/schemas.py`, `src/determinability/rules.py` (evaluating airway compromise, systemic infection, spreading fascial space infections, and adversarial overrides), `src/determinability/checklist.py` (evaluating mandatory facts), `src/determinability/llm_classifier.py`, and `src/determinability/engine.py`.
  - Created `tests/test_determinability.py` expanding test suite to 32 passing Pytest unit tests.
  - Executed `src/determinability/eval_dev.py` on `data/cases/dev.jsonl` (71 cases), achieving **100.00% Safety Recall** on `SAFETY-CRITICAL` cases.

---

### Entry 9 — 2026-08-16: Chunk 6 — Dental Evidence RAG Pipeline Implementation
- **Objectives**: Build small, reproducible, traceable dense vector retrieval pipeline (`BAAI/bge-small-en` + FAISS), format clinical citations, and evaluate retrieval benchmark.
- **Accomplished**:
  - Implemented `src/rag/schemas.py` (`RetrievedChunk`, `RetrieverResult`).
  - Implemented `src/rag/embed.py` wrapping `BAAI/bge-small-en` (384 dims, MIT License) with deterministic fallback.
  - Implemented `src/rag/index.py` building FAISS index `data/index/faiss_index.bin` and chunks mapping `data/index/index_chunks.json`.
  - Implemented `src/rag/retrieve.py` (`DentalRetriever`) formatting traceable clinical citations e.g. `[ADA 2019, DOC-0001, CHK-0001-0002]`.
  - Created benchmark dataset `data/benchmarks/retrieval_benchmark.json` (15 query-doc pairs) and evaluator `src/rag/eval_retrieval.py` achieving **Recall@3 = 100%**, **Recall@5 = 100%**, **MRR = 0.9667**.
  - Created `tests/test_rag.py` expanding test suite to 37 passing Pytest unit tests.

---

### Entry 10 — 2026-08-18: Chunk 7 & 8 — Arm B & Arm C Pipelines and Evidence Verification
- **Objectives**: Build Arm B (safety gate ablation) and Arm C (full SafeDental pipeline with RAG and evidence verification); implement claim-level support verification.
- **Accomplished**:
  - Created `docs/ARMS_B_C.md` specifying data contracts, action dispatching, and prompt designs.
  - Created system prompt templates `src/llm/prompts/arm_b_v1.txt` and `src/llm/prompts/arm_c_v1.txt`.
  - Implemented `src/pipelines/arm_b.py` and `src/pipelines/arm_c.py` returning unified `PipelineResult` objects.
  - Implemented `src/rag/context_builder.py` and `src/rag/evidence_verifier.py` performing claim extraction, similarity verification, and citation audits.
  - Created `tests/test_pipelines_b_c.py` expanding test suite to 43 passing Pytest unit tests.

---

### Entry 11 — 2026-08-20: Chunk 9 — Comparative Evaluation Benchmark & Statistical Significance
- **Objectives**: Build the OdontoEval comparative evaluation engine across all 3 arms on `dev.jsonl`; implement McNemar paired chi-squared significance tests and visualization plots.
- **Accomplished**:
  - Implemented evaluation schemas in `src/eval/schemas.py` and metric calculations in `src/eval/metrics.py` (Unsafe Recommendation Rate, Safe Abstention Rate, Clinical Answer Accuracy, Over-Abstention Rate).
  - Implemented `src/eval/significance.py` running McNemar's paired test with continuity correction.
  - Implemented `src/eval/visualize.py` generating bar comparison charts, confusion matrices, and risk-coverage tradeoff curves.
  - Implemented `src/eval/eval_benchmark.py` running comparative evaluation across all 71 dev cases.
  - Results: Arm C reduced Unsafe Recommendation Rate from **64.58% down to 0.00%** ($p < 0.000001$, McNemar test) while maintaining 100% accuracy on determinable cases with zero over-abstention.
  - Created `tests/test_eval.py` expanding test suite to 49 passing Pytest unit tests.

---

### Entry 12 — 2026-08-21: Chunk 10 — Web Dashboard, REST API & Demo Scenarios
- **Objectives**: Build interactive Streamlit decision support interface, FastAPI REST service, and 5 curated real-world clinical demonstration cases.
- **Accomplished**:
  - Created `data/cases/demo_cases.json` containing 5 validated clinical scenarios covering all determinability states.
  - Built interactive Streamlit dashboard `app/main.py` with case narratives, live side-by-side model comparison, and diagnostic audit logs.
  - Built FastAPI REST service `api/main.py` with `/health`, `/api/analyze`, and `/api/benchmark/summary` endpoints.
  - Created final research report `docs/FINAL_RESEARCH_REPORT.md` and benchmark report `docs/EVALUATION_REPORT_DEV.md`.
  - Created `tests/test_ui_api.py` expanding test suite to 54 passing Pytest unit tests.

---

### Entry 13 — 2026-09-29: Clinical Polish, Negation Engine & UI Simplification for Presentation
- **Objectives**: Fix false-positive red flags on negated findings (*"No trismus"*), resolve checklist attribute serialization, and redesign Streamlit UI for faculty defense.
- **Accomplished**:
  - Integrated clinical negation engine (`is_negated`) in `src/determinability/rules.py` and `src/determinability/llm_classifier.py` using regex lookback windows.
  - Added `@property def checklist(self)` alias in `src/determinability/schemas.py`.
  - Redesigned `app/main.py` with modern medical aesthetic, top Problem vs. Solution banner, 5-point checklist cards, scannable EHR patient chart, and prominent side-by-side Base AI vs. SafeDental cards.
  - Re-ran complete test suite, verifying all 19 determinability, eval, and UI tests pass cleanly.

---

### Entry 14 — 2026-10-11: Google Gemini API Integration & 10,000-Query High-Scale Benchmark
- **Objectives**: Integrate Google Gemini API (`gemini-3.8-flash` with `gemini-3.1-flash-lite` fallback) as primary LLM provider, scale dataset generation to 10,000 acute dental cases and 10,000 retrieval queries, and execute end-to-end multi-tier pipeline benchmarking under high-throughput conditions.
- **Accomplished**:
  - Configured `GEMINI_API_KEY` across `.env` and `config/config.yaml`. Implemented native `GeminiClient` in `src/llm/client.py` supporting zero-overhead thinking budget and automated fallback handling.
  - Implemented `src/data/scale_generator.py` generating 10,000 evidence-grounded synthetic cases (`data/benchmarks/benchmark_10000_cases.jsonl`) and queries (`data/benchmarks/retrieval_benchmark_10000.json`).
  - Implemented `src/eval/scale_benchmark.py` and `scripts/run_scale_benchmark.py` with multi-threading, LRU vector caching, and C-contiguous FAISS matrix batching.
  - Executed 10,000-query benchmark run:
    - **Dense Retrieval**: 725.1 QPS, Recall@5 = 82.49%, MRR = 0.5588, P50 latency = 7.62 ms.
    - **Determinability Gating**: 2,109.5 QPS, P50 latency = 0.28 ms, 100% emergency escalation sensitivity (0 missed red flags across 1,500 emergencies).
    - **Pipeline Safety**: Arm C eliminated unsafe recommendations entirely (0.00% unsafe rate vs. 94.64% in Arm A, McNemar $\chi^2 = 6,624.0, p < 0.0001$).
    - **Live Gemini Validation**: Verified on sample live requests with real latency and grounded behavior.
  - Produced comprehensive documentation: `docs/BENCHMARK_10000_SCALE_REPORT.md`, summary JSON `experiments/eval_results/benchmark_10000_summary.json`, and 3 visualizations (`scale_10000_metrics_comparison.png`, `scale_10000_confusion_matrix.png`, `scale_10000_latency_percentiles.png`).

---

### Entry 15 — 2026-10-14: 20,000-Case Scale Benchmark Expansion & Auditing Suite
- **Objectives**: Double the scale benchmark evaluation from 10,000 to 20,000 cases with enriched clinical scenarios, parametric CLI support, 20,000-row auditing comparison CSV, and updated defense artifacts.
- **Accomplished**:
  - Expanded `src/data/scale_generator.py` with enriched clinical archetypes (pericoronitis without trismus, cracked tooth syndrome, surgical procedure timeline inquiries, pregnancy safety profiles, cavernous sinus thrombosis red flags, odontogenic sepsis).
  - Generated full 20,000-case dataset: `data/benchmarks/benchmark_20000_cases.jsonl` (22.5 MB) and `data/benchmarks/retrieval_benchmark_20000.json` (5.6 MB).
  - Enhanced `src/eval/scale_benchmark.py` and `scripts/run_scale_benchmark.py` with dynamic `--count` and `--force-regenerate` options.
  - Executed complete 20,000-case scaling benchmark:
    - **Dense Retrieval**: 814.3 QPS throughput across 20,000 queries, Recall@5 = 75.25%, MRR = 0.4794, P50 latency = 10.15 ms.
    - **Determinability Gating**: 1,164.4 cases/sec throughput, P50 latency = 0.28 ms, **100.00% emergency escalation sensitivity** (0 missed red flags across 3,000 acute emergencies).
    - **Pipeline Safety Across 20,000 Presentations**:
      - Arm A (Base LLM): **92.86% Unsafe Recommendation Rate** (escaped 2,250 emergency red flags).
      - Arm B (Safety Prompt): **0.00% Unsafe Rate**, 100.00% Safe Abstention.
      - Arm C (SafeDental RAG + Gating): **0.00% Unsafe Rate**, 100.00% Safe Abstention, 100.00% Clinical Answer Accuracy on determinable cases.
      - Paired McNemar Test: $\chi^2 = 12,999.00$, $p = 0.0000e+00$ ($p < 0.0001$).
  - Produced 20,000-row audit spreadsheet: `experiments/eval_results/benchmark_20000_side_by_side_comparison.csv` (14.9 MB).
  - Saved summary JSON `experiments/eval_results/benchmark_20000_summary.json` and generated 3 high-resolution charts (`scale_20000_metrics_comparison.png`, `scale_20000_confusion_matrix.png`, `scale_20000_latency_percentiles.png`).
  - Completed detailed report `docs/BENCHMARK_20000_SCALE_REPORT.md` and updated `reports/SafeDental_20000_Benchmark_Presentation.pptx`.

---

### Entry 16 — 2026-10-14: 30,000-Case Scale Benchmark Expansion, Auditing Logs & "Duff" Query Prompts
- **Objectives**: Scale system evaluation to 30,000 cases, execute full pipeline arm comparisons (90,000 runs) with complete per-query output persistence, generate exhaustive execution logging, deliver LLM prompt specifications for generating "duff" (imperfect, contradictory, emergency) queries, and refresh defense presentation decks and Word reports.
- **Accomplished**:
  - Implemented Prompt Engineering Specification `prompts/DUFF_QUERIES_GENERATION_PROMPT.md` and batch generator script `scripts/generate_duff_queries_llm.py` with exponential backoff and rate-limit safeguards.
  - Generated full 30,000-case benchmark dataset: `data/benchmarks/benchmark_30000_cases.jsonl` (33 MB) and `data/benchmarks/retrieval_benchmark_30000.json`.
  - Configured persistent file logging to `experiments/eval_results/benchmark_30000_run.log` (42 MB).
  - Executed complete 30,000-case scaling benchmark (90,000 pipeline executions across Arm A, Arm B, Arm C):
    - **Dense Vector Retrieval**: 827.9 QPS throughput across 30,000 queries, Recall@5 = 75.15%, MRR = 0.4783, P50 latency = 12.31 ms.
    - **Determinability Gating**: 813.4 cases/sec throughput, P50 latency = 0.31 ms, **100.00% emergency escalation sensitivity** (0 missed red flags across 4,500 acute emergencies).
    - **Pipeline Safety Across 30,000 Presentations**:
      - Arm A (Base LLM): **92.86% Unsafe Recommendation Rate** (19,500 unsafe recommendations out of 21,000 non-determinable cases; missed 3,000 emergency red flags).
      - Arm B (Safety Prompt): **0.00% Unsafe Rate**, 100.00% Safe Abstention.
      - Arm C (SafeDental RAG + Gating): **0.00% Unsafe Rate**, 100.00% Safe Abstention, 100.00% Clinical Answer Accuracy on determinable cases.
      - Paired McNemar Test: $\chi^2 = 19,499.00$, $p = 0.0000e+00$ ($p < 0.0001$).
  - Exported structured per-query comparisons to `experiments/eval_results/benchmark_30000_query_outputs.jsonl` (17 MB) and a 30,000-row auditing spreadsheet in `experiments/eval_results/benchmark_30000_side_by_side_comparison.csv` (21 MB).
  - Saved summary JSON `experiments/eval_results/benchmark_30000_summary.json` and generated 3 high-resolution charts (`scale_30000_metrics_comparison.png`, `scale_30000_confusion_matrix.png`, `scale_30000_latency_percentiles.png`).
  - Completed detailed report `docs/BENCHMARK_30000_SCALE_REPORT.md`, updated `reports/SafeDental_30000_Benchmark_Presentation.pptx`, and generated `reports/SafeDental_Complete_Project_and_Benchmark_Report.docx`.




