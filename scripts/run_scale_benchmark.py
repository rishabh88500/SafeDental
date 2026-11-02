#!/usr/bin/env python3
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
import sys
import argparse
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.scale_benchmark import run_scale_benchmark, run_10000_scale_benchmark
from src.utils.logging import get_logger

logger = get_logger("cli_scale_benchmark")


def main():
    parser = argparse.ArgumentParser(description="Run scaling benchmark on SafeDental (e.g. 10,000 or 20,000 cases)")
    parser.add_argument("--count", type=int, default=20000, help="Number of cases to generate/evaluate (default: 20000)")
    parser.add_argument("--concurrency", type=int, default=16, help="Thread pool concurrency for parallel pipeline evaluation")
    parser.add_argument("--live-gemini-sample", type=int, default=5, help="Number of cases to evaluate live with Gemini API")
    parser.add_argument("--force-regenerate", action="store_true", help="Force regeneration of synthetic dataset")
    args = parser.parse_args()

    print("=" * 70)
    print(f" SafeDental High-Scale Benchmark ({args.count:,} Queries & Pipeline Arms)")
    print("=" * 70)
    print(f" Total Cases / Queries: {args.count:,}")
    print(f" Concurrency: {args.concurrency}")
    print(f" Live Gemini Sample Size: {args.live_gemini_sample}")
    print(f" Force Regenerate Dataset: {args.force_regenerate}")
    print("-" * 70)

    summary = run_scale_benchmark(
        count=args.count,
        concurrency=args.concurrency,
        live_gemini_sample_size=args.live_gemini_sample,
        force_regenerate=args.force_regenerate
    )

    print("\n" + "=" * 70)
    print(" BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f" Total Cases & Queries Evaluated: {summary['total_cases']:,}")
    print(f" Retrieval Recall@5: {summary['retrieval']['recall_at_5']:.2%}")
    print(f" Retrieval Throughput: {summary['retrieval']['throughput_qps']:.1f} QPS")
    print(f" Determinability Accuracy: {summary['determinability']['overall_accuracy']:.2%}")
    print(f" Determinability Escaped Red Flags: {summary['determinability']['safety_critical']['escaped_red_flags']}")
    print("-" * 70)
    print(" Pipeline Arm Comparison (Primary Research Metrics):")
    for arm_name in ["ARM_A", "ARM_B", "ARM_C"]:
        arm = summary["arms"][arm_name]
        print(f"   [{arm_name}] Unsafe Rec Rate: {arm['unsafe_recommendation_rate']:.2%} | Safe Abstain: {arm['safe_abstention_rate']:.2%} | Accuracy: {arm['clinical_answer_accuracy']:.2%} | Over-Abstain: {arm['over_abstention_rate']:.2%}")
    print("=" * 70)
    print(" Artifacts Saved:")
    print(f"   JSON Summary: experiments/eval_results/benchmark_{args.count}_summary.json")
    print(f"   Markdown Report: docs/BENCHMARK_{args.count}_SCALE_REPORT.md")
    print(f"   Visualizations: experiments/eval_results/scale_{args.count}_*.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
