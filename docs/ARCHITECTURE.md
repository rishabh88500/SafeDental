# Architecture

## 1. Overall System
Text case → Analyzer → Determinability → {RAG+Generate+Verify | Ask/Abstain/Escalate} → unified response.

```text
                 ┌────────────────────────────────────────┐
                 │          DENTAL CASE (text)            │
                 └───────────────────┬────────────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │   Case Analyzer      │  (extract structured facts)
                          └──────────┬──────────┘
                                     ▼
                    ┌────────────────────────────────┐
                    │  Clinical Determinability Check │
                    │  → one of 5 labels             │
                    └───────┬───────────────┬────────┘
                            │               │
                DETERMINABLE│               │ UNDERDETERMINED /
                            │               │ SAFETY-CRITICAL /
                            ▼               │ CONFLICTING / OUT-OF-SCOPE
                 ┌────────────────┐        ▼
                 │  RAG Retrieval │   ┌──────────────────────────┐
                 └───────┬────────┘   │  Ask / Abstain / Escalate │
                         ▼            │  + list missing info      │
                 ┌────────────────┐   └──────────────────────────┘
                 │  LLM Generate  │
                 └───────┬────────┘
                         ▼
                 ┌────────────────────┐
                 │ Evidence Verify    │  (are claims supported by retrieved text?)
                 └───────┬────────────┘
                         ▼
                 ┌────────────────────┐
                 │ Grounded Answer +  │
                 │ citations + risk   │
                 └────────────────────┘
```

## 2. Knowledge Base Architecture (Chunk 3)
```text
  Raw Document (.txt)
        │ (ingest.py)
        ▼
  data/knowledge_base/raw/DOC-XXXX.txt + metadata/DOC-XXXX.json
        │ (clean_text.py)
        ▼
  data/knowledge_base/cleaned/DOC-XXXX.txt
        │ (chunk.py - Section Aware)
        ▼
  data/knowledge_base/chunks/DOC-XXXX.jsonl
        │ (index.py)
        ▼
  data/knowledge_base/index/index_meta.json (Dense Embedding FAISS Ready)
```

## 3. Arm A Baseline Pipeline Architecture (Chunk 4)
```text
  ClinicalCase (data/cases/dev.jsonl)
        │
  Sealed Test Access Guard (data_guard.py)
        │
  Prompt Formatter (prompts/arm_a_v1.txt)
        │
  LLMClient (Ollama / Mock Fallback)
        │
  Response Parser (parse_arm_a_response)
        │
  ModelResponse (JSONL)
        │
  Experiment Recorder (experiments/arm_a/exp_arma_dev_v1/)
```

## 4. Component-level
- **Analyzer:** extract structured facts (LLM + checklist).
- **Determinability:** rules + LLM → 1 of 5 labels + missing info.
- **RAG:** chunk/embed/index/retrieve/(rerank)/cite.
- **Generator:** grounded answer from retrieved context.
- **Evidence Verify:** claim-level support check.
- **Response Builder:** unified JSON contract.
