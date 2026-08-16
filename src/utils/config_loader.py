from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str = "SafeDental"
    version: str = "0.1.0"


class DomainConfig(BaseModel):
    name: str
    description: str


class ModelConfig(BaseModel):
    provider: str = "ollama"
    name: str = "llama3.1:8b-instruct"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.0
    max_tokens: int = 512
    seed: int = 42


class RetrievalConfig(BaseModel):
    enabled: bool = True
    top_k: int = 5
    embedding_model: str = "BAAI/bge-small-en"
    vector_store: str = "faiss"
    chunk_size: int = 400
    chunk_overlap: int = 50


class DatasetConfig(BaseModel):
    version: str = "1.0.0"
    raw_dir: str = "data/cases/raw"
    validated_path: str = "data/cases/validated/cases.jsonl"
    train_path: str = "data/cases/train.jsonl"
    dev_path: str = "data/cases/dev.jsonl"
    test_path: str = "data/cases/test.jsonl"


class DeterminabilityConfig(BaseModel):
    red_flags_path: str = "config/red_flags.yaml"
    required_fields_path: str = "config/required_fields.yaml"


class EvaluationConfig(BaseModel):
    seed: int = 42
    output_dir: str = "results/"
    human_eval_sample_size: int = 50


class AppConfig(BaseModel):
    project: ProjectConfig
    domain: DomainConfig
    model: ModelConfig
    retrieval: RetrievalConfig
    dataset: DatasetConfig
    determinability: DeterminabilityConfig
    evaluation: EvaluationConfig


def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    # Assuming this file is located in src/utils/config_loader.py
    return Path(__file__).resolve().parent.parent.parent


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Loads a YAML file and returns its dictionary representation."""
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Loads and validates the main application configuration.
    If no path is provided, defaults to config/config.yaml relative to project root.
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"

    raw_cfg = load_yaml(config_path)
    return AppConfig(**raw_cfg)


def load_red_flags(red_flags_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads the red flags configuration YAML."""
    if red_flags_path is None:
        red_flags_path = get_project_root() / "config" / "red_flags.yaml"
    return load_yaml(red_flags_path)


def load_required_fields(required_fields_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads the required fields configuration YAML."""
    if required_fields_path is None:
        required_fields_path = get_project_root() / "config" / "required_fields.yaml"
    return load_yaml(required_fields_path)
