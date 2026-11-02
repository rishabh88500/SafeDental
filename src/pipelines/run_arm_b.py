import argparse
from pathlib import Path
from src.pipelines.arm_b import run_arm_b_experiment
from src.utils.config_loader import get_project_root
from src.utils.logging import get_logger

logger = get_logger("run_arm_b")


def main():
    parser = argparse.ArgumentParser(description="Execute SafeDental Arm B Safety Experiment")
    parser.add_argument("--cases", type=str, default="data/cases/dev.jsonl", help="Relative path to case JSONL file")
    parser.add_argument("--experiment-id", type=str, default="exp_armb_dev_v1", help="Unique experiment identifier")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to execute")
    parser.add_argument("--force-mock", action="store_true", help="Force mock LLM client execution")
    args = parser.parse_args()

    project_root = get_project_root()
    cases_path = project_root / args.cases

    exp_dir = run_arm_b_experiment(
        cases_path=cases_path,
        experiment_id=args.experiment_id,
        force_mock=args.force_mock,
        limit=args.limit
    )

    logger.info(f"Arm B Experiment completed successfully. Output saved to '{exp_dir}'")


if __name__ == "__main__":
    main()
