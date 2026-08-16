import json
from pathlib import Path
from typing import Dict, List, Any
from src.rag.retrieve import DentalRetriever
from src.utils.config_loader import get_project_root
from src.utils.logging import get_logger

logger = get_logger("eval_retrieval")


def run_retrieval_evaluation() -> Dict[str, Any]:
    """
    Evaluates DentalRetriever on data/benchmarks/retrieval_benchmark.json (15 queries).
    Measures Recall@1, Recall@3, Recall@5, and MRR.
    """
    project_root = get_project_root()
    benchmark_path = project_root / "data" / "benchmarks" / "retrieval_benchmark.json"

    if not benchmark_path.exists():
        raise FileNotFoundError(f"Retrieval benchmark file not found at '{benchmark_path}'")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_queries = json.load(f)

    logger.info(f"Evaluating DentalRetriever on {len(benchmark_queries)} benchmark queries...")
    retriever = DentalRetriever(default_top_k=5)

    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0
    reciprocal_ranks: List[float] = []

    query_details: List[Dict[str, Any]] = []

    for q_item in benchmark_queries:
        q_id = q_item["query_id"]
        q_text = q_item["query"]
        target_doc_id = q_item["target_doc_id"]

        res = retriever.retrieve(q_text, top_k=5)
        retrieved_doc_ids = [chk.document_id for chk in res.retrieved_chunks]

        # Calculate Rank
        rank = 0
        if target_doc_id in retrieved_doc_ids:
            rank = retrieved_doc_ids.index(target_doc_id) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        hit_1 = (rank == 1)
        hit_3 = (0 < rank <= 3)
        hit_5 = (0 < rank <= 5)

        if hit_1:
            hits_at_1 += 1
        if hit_3:
            hits_at_3 += 1
        if hit_5:
            hits_at_5 += 1

        query_details.append({
            "query_id": q_id,
            "query": q_text,
            "target_doc_id": target_doc_id,
            "retrieved_doc_ids": retrieved_doc_ids,
            "rank": rank,
            "hit_at_1": hit_1,
            "hit_at_3": hit_3,
            "hit_at_5": hit_5,
            "execution_time_ms": res.execution_time_ms
        })

    total_q = len(benchmark_queries)
    recall_1 = (hits_at_1 / total_q) * 100.0
    recall_3 = (hits_at_3 / total_q) * 100.0
    recall_5 = (hits_at_5 / total_q) * 100.0
    mrr = (sum(reciprocal_ranks) / total_q) if total_q > 0 else 0.0

    metrics = {
        "total_benchmark_queries": total_q,
        "hits_at_1": hits_at_1,
        "hits_at_3": hits_at_3,
        "hits_at_5": hits_at_5,
        "recall_at_1": round(recall_1, 2),
        "recall_at_3": round(recall_3, 2),
        "recall_at_5": round(recall_5, 2),
        "mrr": round(mrr, 4)
    }

    logger.info(f"Retrieval Benchmark Results: Recall@1={recall_1:.1f}%, Recall@3={recall_3:.1f}%, Recall@5={recall_5:.1f}%, MRR={mrr:.4f}")

    out_dir = project_root / "experiments" / "rag"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "eval_retrieval_results.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "query_details": query_details}, f, indent=2)

    logger.info(f"Saved retrieval evaluation output to '{out_file}'")
    return metrics


if __name__ == "__main__":
    run_retrieval_evaluation()
