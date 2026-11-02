import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from src.llm.schemas import ModelResponse
from src.utils.config_loader import load_config, AppConfig
from src.utils.logging import get_logger

logger = get_logger("experiment")


def get_git_commit_hash(repo_dir: Path) -> str:
    """Gets the current git commit hash, or 'uncommitted' if unavailable."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "uncommitted"


def save_experiment_run(
    experiment_id: str,
    pipeline_arm: str,
    predictions: List[ModelResponse],
    config: AppConfig,
    project_root: Path
) -> Path:
    """
    Persists experiment run artifacts in experiments/<arm_name>/<experiment_id>/
    - config.yaml
    - predictions.jsonl
    - metadata.json
    """
    exp_dir = project_root / "experiments" / pipeline_arm.lower() / experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save Predictions JSONL
    pred_file = exp_dir / "predictions.jsonl"
    with open(pred_file, "w", encoding="utf-8") as f:
        for p in predictions:
            f.write(p.model_dump_json() + "\n")

    # 2. Save Metadata JSON
    git_hash = get_git_commit_hash(project_root)
    meta = {
        "experiment_id": experiment_id,
        "pipeline_arm": pipeline_arm,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "git_commit_hash": git_hash,
        "config_version": config.project.version,
        "model_name": config.model.name,
        "model_provider": config.model.provider,
        "total_cases_evaluated": len(predictions),
        "predictions_file": str(pred_file.relative_to(project_root)),
    }

    meta_file = exp_dir / "metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 3. Copy Config
    config_file = exp_dir / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        import yaml
        yaml.dump(config.model_dump(), f, default_flow_style=False)

    logger.info(f"Saved experiment artifacts to '{exp_dir}' ({len(predictions)} predictions)")
    return exp_dir
