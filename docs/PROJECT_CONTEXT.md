# Project Context: SafeDental

**One sentence:** A dental decision-support prototype for **acute dental pain + odontogenic infection** that decides *whether it can safely answer a case*, and if not, asks for missing info or escalates — instead of confidently producing an unsafe answer.

## Research Question
> Does adding a clinical determinability + abstention layer (with and without RAG) reduce the unsafe recommendation rate of a dental LLM, compared to a base LLM, without causing excessive over-abstention?

## Hypotheses
| ID | Hypothesis | How it's tested |
| ---- | ----------- | ----------------- |
| **H1** | The base LLM (A) produces unsafe recommendations on a meaningful fraction of missing-info and safety-critical cases. | Unsafe recommendation rate on A. |
| **H2** | A safety-aware prompt (B) reduces unsafe rate vs. A, but tends to over-abstain (blunt refusal). | Compare unsafe rate + over-abstention rate A vs. B. |
| **H3** | RAG + structured safety assessment (C) achieves the best trade-off: lowest unsafe rate with acceptable over-abstention and better evidence grounding. | Compare A vs. B vs. C on all 4 metrics. |
| **H4 (opt)**| QLoRA safety fine-tuning improves abstention *calibration* over prompting alone. | Only if time permits. |

**Null hypothesis:** Abstention layers do NOT significantly reduce unsafe rate (or reduce it only by destroying usefulness through over-abstention).

## Locked Boundaries
- Domain: acute dental pain + odontogenic (tooth-origin) infection ONLY.
- Text-only. No images, no CBCT, no radiograph reasoning.
- No real patient data. Synthetic + expert-authored + public evidence only.
- QLoRA is **optional** and must never block completion.
- Not autonomous. Every output is framed as "decision-support / educational."
