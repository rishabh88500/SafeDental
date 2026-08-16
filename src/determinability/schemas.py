from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.data.schema import DeterminabilityLabel, ExpectedAction


class RuleTrigger(BaseModel):
    """Represents a hard safety rule triggered by keyword/pattern match."""
    rule_category: str
    severity: str
    action: str
    matched_keywords: List[str]
    rationale: str


class ChecklistCoverage(BaseModel):
    """Evaluates coverage of required clinical fields."""
    total_required_categories: int
    present_categories: List[str]
    missing_fields: List[str]
    is_complete: bool


class LLMClassification(BaseModel):
    """Structured response output from secondary LLM classifier."""
    predicted_label: DeterminabilityLabel
    predicted_action: ExpectedAction
    identified_missing_info: List[str] = Field(default_factory=list)
    clinical_rationale: str
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class DeterminabilityResult(BaseModel):
    """Normalized output contract of the Clinical Determinability Engine."""
    case_id: str
    label: DeterminabilityLabel
    action: ExpectedAction
    missing_info: List[str] = Field(default_factory=list)
    triggered_rules: List[RuleTrigger] = Field(default_factory=list)
    checklist_status: Optional[ChecklistCoverage] = None
    llm_classification: Optional[LLMClassification] = None
    final_rationale: str
    is_safety_override: bool = False
