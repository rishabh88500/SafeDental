import re
from typing import List, Dict, Any, Optional
from src.utils.config_loader import load_required_fields
from src.determinability.schemas import ChecklistCoverage
from src.utils.logging import get_logger

logger = get_logger("determinability_checklist")


class RequiredInformationChecklistEvaluator:
    """
    Evaluates whether a clinical case narrative covers mandatory clinical facts:
    - Chief complaint (pain location, character, duration, triggers)
    - Clinical signs (swelling, fever presence)
    - Medical history (systemic conditions, drug allergies)
    """

    def __init__(self, required_fields_config: Optional[Dict[str, Any]] = None):
        self.config = required_fields_config or load_required_fields()
        self.required = self.config.get("required_fields", {})

    def evaluate(self, text: str) -> ChecklistCoverage:
        """
        Evaluates input text for required clinical field categories.
        """
        if not text:
            return ChecklistCoverage(
                total_required_categories=len(self.required),
                present_categories=[],
                missing_fields=["pain_location", "pain_duration", "swelling_presence", "drug_allergies"],
                is_complete=False
            )

        norm_text = text.lower()
        missing_fields: List[str] = []
        present_categories: List[str] = []

        # 1. Pain Location
        loc_patterns = ["tooth", "molar", "premolar", "incisor", "canine", "jaw", "quadrant", "upper right", "lower left", "upper left", "lower right"]
        if any(p in norm_text for p in loc_patterns):
            present_categories.append("pain_location")
        else:
            missing_fields.append("pain_location")

        # 2. Pain Duration / Onset
        dur_patterns = ["day", "days", "week", "weeks", "month", "hours", "yesterday", "since", "duration", "onset", "started"]
        if any(p in norm_text for p in dur_patterns):
            present_categories.append("pain_onset_duration")
        else:
            missing_fields.append("pain_duration")

        # 3. Swelling Presence/Absence
        swell_patterns = ["swelling", "swollen", "edema", "no swelling", "gums slightly tender"]
        if any(p in norm_text for p in swell_patterns):
            present_categories.append("swelling_presence")
        else:
            missing_fields.append("swelling_presence")

        # 4. Fever / Systemic Signs
        fever_patterns = ["fever", "temp", "temperature", "chills", "98.", "99.", "100.", "101.", "102.", "no fever"]
        if any(p in norm_text for p in fever_patterns):
            present_categories.append("fever_presence")
        else:
            missing_fields.append("fever_presence")

        # 5. Drug Allergies / Medical History
        allergy_patterns = ["allerg", "penicillin", "amoxicillin", "medical condition", "history", "hypertension", "no medical", "no drug"]
        if any(p in norm_text for p in allergy_patterns):
            present_categories.append("medical_history_allergies")
        else:
            missing_fields.append("drug_allergies")

        is_complete = len(missing_fields) == 0

        return ChecklistCoverage(
            total_required_categories=5,
            present_categories=present_categories,
            missing_fields=missing_fields,
            is_complete=is_complete
        )
