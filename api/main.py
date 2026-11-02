import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.utils.config_loader import load_config, get_project_root
from src.data.schema import ClinicalCase, ExpectedAction, DeterminabilityLabel, PatientContext
from src.llm.client import LLMClient
from src.determinability.engine import DeterminabilityEngine
from src.rag.retrieve import DentalRetriever
from src.rag.evidence_verifier import EvidenceVerifier

from src.pipelines.arm_a import run_arm_a_on_case, load_arm_a_prompt
from src.pipelines.arm_b import run_arm_b_on_case, load_arm_b_prompt
from src.pipelines.arm_c import run_arm_c_on_case, load_arm_c_prompt

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SafeDental API",
    description="Safety-Aware Acute Dental Decision Support REST Service",
    version="0.7.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global lazy components
_client: Optional[LLMClient] = None
_det_engine: Optional[DeterminabilityEngine] = None
_retriever: Optional[DentalRetriever] = None
_verifier: Optional[EvidenceVerifier] = None


def get_components():
    global _client, _det_engine, _retriever, _verifier
    if _client is None:
        cfg = load_config()
        _client = LLMClient(config=cfg)
        _det_engine = DeterminabilityEngine()
        _retriever = DentalRetriever()
        _verifier = EvidenceVerifier()
    return _client, _det_engine, _retriever, _verifier


class AnalyzeRequest(BaseModel):
    narrative: str = Field(min_length=5, description="Patient clinical case narrative or chief complaint")
    arm: str = Field(default="ARM_C", pattern=r"^ARM_[A-C]$", description="Pipeline arm to execute")
    age: int = Field(default=35, ge=0, le=120)
    sex: str = Field(default="F")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.7.0", "service": "SafeDental API"}


@app.post("/api/analyze")
def analyze_case(req: AnalyzeRequest):
    client, det_engine, retriever, verifier = get_components()

    # Construct ClinicalCase
    c = ClinicalCase(
        case_id="SD-9999",
        patient_context=PatientContext(age=req.age, sex=req.sex),
        question=req.narrative,
        symptoms=[req.narrative],
        determinability_label=DeterminabilityLabel.UNDERDETERMINED,
        safety_risk="MEDIUM",
        expected_action=ExpectedAction.ASK,
        expert_rationale="API request narrative."
    )

    if req.arm == "ARM_A":
        prompt_a = load_arm_a_prompt()
        res = run_arm_a_on_case(c, client, prompt_a, experiment_id="api_run")
        return {
            "case_id": c.case_id,
            "arm": "ARM_A",
            "action": res.predicted_action.value,
            "answer": res.parsed_answer,
            "missing_information": [],
            "safety_message": "",
            "citations": []
        }
    elif req.arm == "ARM_B":
        prompt_b = load_arm_b_prompt()
        res = run_arm_b_on_case(c, client, det_engine, prompt_b, experiment_id="api_run")
        return res.model_dump()
    elif req.arm == "ARM_C":
        prompt_c = load_arm_c_prompt()
        res = run_arm_c_on_case(c, client, det_engine, retriever, verifier, prompt_c, experiment_id="api_run")
        return res.model_dump()
    else:
        raise HTTPException(status_code=400, detail="Invalid arm requested.")


@app.get("/api/benchmark/summary")
def get_benchmark_summary():
    root = get_project_root()
    summary_path = root / "experiments" / "eval_results" / "dev_comparative_summary.json"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark summary file not yet generated.")
    return json.loads(summary_path.read_text(encoding="utf-8"))

