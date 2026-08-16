# Decisions Log

## Architecture & Boundaries
1. **Scope**: Acute dental pain + odontogenic (tooth-origin) infection ONLY.
2. **Input Modality**: Text-only. No images, no CBCT, no radiograph reasoning.
3. **Data Source**: Synthetic + expert-authored + public evidence only. No real patient data.
4. **Usage Context**: Educational / decision-support. Not an autonomous prescribing bot.
5. **Sealed Test Set Protection**: `data/cases/test.jsonl` is strictly sealed until Chunk 8. Automated data guard (`src/utils/data_guard.py`) enforces this boundary during development.

## Knowledge Base & Retrieval (Chunk 3)
1. **Chunking Strategy**: Section-aware chunking (~400 words per chunk with 50-word overlap) preserving document ID, section headings, page numbers, and source URLs.
2. **Embedding Model**: `BAAI/bge-small-en` (384 dimensions, MIT License).
3. **Source Policy**: Strict governance requiring `APPROVED_OPEN_ACCESS` or `APPROVED_RESEARCH_ONLY` status in `docs/KB_SOURCE_POLICY.md`.

## LLM & Baseline Pipeline (Chunk 4)
1. **Model Client Interface**: `LLMClient` supporting local Ollama (`llama3.1:8b-instruct`) with deterministic Mock engine fallback for offline unit testing.
2. **Arm A System Prompt**: `src/llm/prompts/arm_a_v1.txt` requests direct clinical advice without exposing safety rules or evaluation criteria.
3. **Experiment Storage**: `experiments/<arm_name>/<experiment_id>/` storing YAML config, predictions JSONL, git commit hash, and run metadata.

## Tech Stack
- **Language**: Python 3.10+
- **LLM Engine**: Ollama (local) or free API / Mock fallback.
- **Embeddings**: `sentence-transformers` (`BAAI/bge-small-en`).
- **Vector Store**: FAISS / ChromaDB.
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Tracking**: JSON/YAML + Git commit logging
