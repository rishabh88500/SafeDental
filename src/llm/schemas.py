from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from src.data.schema import ExpectedAction, DeterminabilityLabel


class ModelResponse(BaseModel):
    """
    Normalized response structure output by model pipeline execution.
    Distinguishes model-generated fields from evaluation-only gold fields.
    """
    # Identifiers & Metadata
    case_id: str
    experiment_id: str
    pipeline_arm: str = Field(pattern=r"^ARM_[A-D]$")
    model_name: str
    prompt_version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Model-Generated Fields
    raw_response: str = Field(description="Unprocessed text output from LLM")
    parsed_answer: str = Field(default="", description="Extracted clinical recommendation text")
    predicted_action: ExpectedAction = Field(default=ExpectedAction.ANSWER, description="Predicted action decision")
    predicted_missing_info: List[str] = Field(default_factory=list, description="Extracted missing facts if ASK")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted document citations if RAG")

    # Pipeline Generation Specs
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=512)
    seed: int = Field(default=42)

    # Evaluation-Only Gold Reference Fields (copied for scoring convenience)
    gold_determinability_label: DeterminabilityLabel
    gold_expected_action: ExpectedAction
    gold_safety_risk: str
