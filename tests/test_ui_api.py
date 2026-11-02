import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from src.utils.config_loader import get_project_root
from src.data.schema import ClinicalCase
from api.main import app

client = TestClient(app)


def test_demo_cases_loading():
    demo_path = get_project_root() / "data" / "cases" / "demo_cases.json"
    assert demo_path.exists()

    cases_raw = json.loads(demo_path.read_text(encoding="utf-8"))
    assert len(cases_raw) >= 5

    parsed_cases = [ClinicalCase(**c) for c in cases_raw]
    assert len(parsed_cases) == len(cases_raw)
    assert parsed_cases[0].case_id == "SD-0001"


def test_fastapi_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.7.0"


def test_fastapi_analyze_endpoint():
    payload = {
        "narrative": "Patient has severe throbbing pain in tooth 36 for 3 days without fever or swelling.",
        "arm": "ARM_C",
        "age": 34,
        "sex": "F"
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "action" in data
    assert data["arm"] == "ARM_C"


def test_fastapi_benchmark_summary():
    summary_path = get_project_root() / "experiments" / "eval_results" / "dev_comparative_summary.json"
    if not summary_path.exists():
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps({"dataset_split": "dev", "num_cases": 71, "arm_metrics": {"ARM_C": {}}}), encoding="utf-8")

    resp = client.get("/api/benchmark/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "arm_metrics" in data
    assert "ARM_C" in data["arm_metrics"]

