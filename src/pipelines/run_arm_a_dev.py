from pathlib import Path
from src.pipelines.arm_a import run_arm_a_experiment
from src.utils.config_loader import get_project_root
from src.utils.logging import get_logger

logger = get_logger("run_arm_a_dev")

def main():
    project_root = get_project_root()
    dev_cases_path = project_root / "data" / "cases" / "dev.jsonl"
    experiment_id = "exp_arma_dev_v1"

    logger.info(f"Running Arm A Baseline Development Experiment '{experiment_id}' on dev cases...")
    exp_dir = run_arm_a_experiment(
        cases_path=dev_cases_path,
        experiment_id=experiment_id,
        allow_sealed_test=False,
        force_mock=False  # Attempts local Ollama, falls back to Mock if offline
    )
    logger.info(f"Arm A Development Run complete. Artifacts saved in '{exp_dir}'")

if __name__ == "__main__":
    main()
