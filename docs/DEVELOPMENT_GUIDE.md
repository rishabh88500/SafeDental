# Development Guide

## Project Phases
- **Phase 0:** Project comprehension.
- **Phase 1:** Project memory & scaffold setup.
- **Phase 2:** Chunk 1 implementation (protocol, config).
- **Phase 3+:** Follow the 10 chunks from `wholeplan.md`.

## The Golden Rule
> A **completed, honestly evaluated A/B/C comparison** — even if it concludes "safety prompting helps but RAG adds little" — is a **far stronger final-year project** than a half-finished, impressive-looking multi-agent system.

**If we fall behind:** 
- Drop QLoRA (Arm D)
- Drop reranker
- Drop FastAPI
- Drop multi-reviewer eval

**NEVER drop:**
- The dataset quality
- The determinability safety recall
- The hidden-test comparison

## Environment & Run Instructions
*(To be populated in Chunk 1)*
- Activate virtual environment: `...`
- Install dependencies: `pip install -r requirements.txt`
- Run Streamlit: `streamlit run app/streamlit_app.py`
- Run LLM: `ollama run llama3.1:8b-instruct` (or similar depending on config).
