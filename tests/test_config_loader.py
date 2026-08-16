import pytest
from pathlib import Path
from src.utils.config_loader import (
    load_config,
    load_red_flags,
    load_required_fields,
    get_project_root,
    AppConfig,
)


def test_get_project_root():
    root = get_project_root()
    assert isinstance(root, Path)
    assert (root / "config" / "config.yaml").exists()


def test_load_config():
    cfg = load_config()
    assert isinstance(cfg, AppConfig)
    assert cfg.project.name == "SafeDental"
    assert cfg.model.provider == "openrouter"
    assert cfg.model.name == "meta-llama/llama-3.1-8b-instruct"
    assert cfg.model.temperature == 0.0
    assert cfg.model.seed == 42
    assert cfg.retrieval.top_k == 5
    assert cfg.retrieval.embedding_model == "BAAI/bge-small-en"


def test_load_red_flags():
    red_flags = load_red_flags()
    assert isinstance(red_flags, dict)
    assert "red_flags" in red_flags
    assert "airway" in red_flags["red_flags"]
    assert "spreading_fascial_space" in red_flags["red_flags"]


def test_load_required_fields():
    req_fields = load_required_fields()
    assert isinstance(req_fields, dict)
    assert "required_fields" in req_fields
    assert "chief_complaint" in req_fields["required_fields"]
    assert "clinical_signs" in req_fields["required_fields"]
