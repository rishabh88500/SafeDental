from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DeterminabilityLabel(str, Enum):
    DETERMINABLE = "DETERMINABLE"
    UNDERDETERMINED = "UNDERDETERMINED"
    SAFETY_CRITICAL = "SAFETY-CRITICAL"
    CONFLICTING = "CONFLICTING"
    OUT_OF_SCOPE = "OUT-OF-SCOPE"


class ExpectedAction(str, Enum):
    ANSWER = "ANSWER"
    ASK = "ASK"
    ABSTAIN = "ABSTAIN"
    ESCALATE = "ESCALATE"


class SafetyRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SourceType(str, Enum):
    EXPERT_AUTHORED = "expert_authored"
    SYNTHETIC_DRAFTED = "synthetic_drafted"
    PUBLIC_REFERENCE = "public_reference"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    EXPERT_REVIEWED = "expert_reviewed"
    VALIDATED = "validated"


class DatasetSplit(str, Enum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"
    UNASSIGNED = "unassigned"


class PatientContext(BaseModel):
    age: int = Field(ge=0, le=120, description="Patient age in years")
    sex: str = Field(pattern="^(M|F|Other|Unknown)$", description="Biological sex")
    relevant_history: List[str] = Field(default_factory=list, description="Key past dental/medical context")


class ClinicalCase(BaseModel):
    case_id: str = Field(pattern=r"^SD-[0-9]{4}$", description="Canonical case ID (e.g. SD-0001)")
    dataset_version: str = Field(default="0.1.0", description="Dataset schema version")
    clinical_domain: str = Field(default="acute_dental_pain_odontogenic_infection")

    patient_context: PatientContext
    symptoms: List[str] = Field(default_factory=list)
    duration: str = Field(default="")
    medical_history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    clinical_findings: List[str] = Field(default_factory=list)
    radiographic_information: List[str] = Field(default_factory=list)

    question: str = Field(min_length=5, description="Query or problem text")

    determinability_label: DeterminabilityLabel
    critical_missing_information: List[str] = Field(default_factory=list)

    safety_risk: SafetyRisk
    expected_action: ExpectedAction

    supporting_evidence_ids: List[str] = Field(default_factory=list)
    expert_rationale: str = Field(min_length=10, description="Clinical justification")

    source_type: SourceType = Field(default=SourceType.EXPERT_AUTHORED)
    review_status: ReviewStatus = Field(default=ReviewStatus.VALIDATED)
    reviewer_notes: str = Field(default="")

    split: DatasetSplit = Field(default=DatasetSplit.UNASSIGNED)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_clinical_narrative(self) -> str:
        """Constructs a consolidated clinical narrative from structured case fields."""
        parts = [
            f"Patient Context: {self.patient_context.age}{self.patient_context.sex}.",
            f"Chief Complaint / Question: {self.question}",
            f"Symptoms: {', '.join(self.symptoms) if self.symptoms else 'None reported'}.",
            f"Duration: {self.duration if self.duration else 'Unstated'}.",
            f"Medical History: {', '.join(self.medical_history) if self.medical_history else 'None reported'}.",
            f"Allergies: {', '.join(self.allergies) if self.allergies else 'None reported'}.",
            f"Clinical Findings: {', '.join(self.clinical_findings) if self.clinical_findings else 'None reported'}."
        ]
        return "\n".join(parts)
