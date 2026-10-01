import json
import re
from typing import Optional, Dict, Any, List
from src.data.schema import DeterminabilityLabel, ExpectedAction
from src.llm.client import LLMClient
from src.determinability.schemas import LLMClassification
from src.utils.logging import get_logger

logger = get_logger("determinability_llm_classifier")

SYSTEM_PROMPT = """You are a clinical determinability classifier for acute dental pain and odontogenic infection.
Analyze the clinical narrative provided and evaluate whether the information is sufficient to safely answer.

Classify the case into EXACTLY ONE of these 5 labels:
1. DETERMINABLE - Narrative has sufficient facts (location, duration, swelling/fever status, allergy history) to advise safely. (Action: ANSWER)
2. UNDERDETERMINED - Key clinical facts missing (duration, swelling status, fever, or allergy history). (Action: ASK)
3. SAFETY-CRITICAL - Emergency red flags present (trismus, difficulty swallowing/breathing, high fever >101F, facial/eye swelling). (Action: ESCALATE)
4. CONFLICTING - Contradictory statements in narrative (e.g. pain-free yet 10/10 pain). (Action: ABSTAIN)
5. OUT-OF-SCOPE - Query is non-dental or outside acute pain/infection domain (whitening, clear aligners, trauma/fracture). (Action: ABSTAIN)

You MUST respond in JSON format ONLY:
{
  "label": "DETERMINABLE" | "UNDERDETERMINED" | "SAFETY-CRITICAL" | "CONFLICTING" | "OUT-OF-SCOPE",
  "action": "ANSWER" | "ASK" | "ESCALATE" | "ABSTAIN",
  "missing_info": ["list", "of", "missing", "facts"],
  "rationale": "Brief clinical explanation",
  "confidence": 0.95
}
"""


class LLMDeterminabilityClassifier:
    """
    Secondary LLM-assisted classifier that evaluates clinical cases
    and extracts present/missing facts, returning structured json classification.
    """

    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()

    def classify(self, text: str) -> LLMClassification:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Clinical Case Narrative:\n{text}"}
        ]

        raw_resp = self.client.generate(messages, temperature=0.0)
        return self._parse_response(raw_resp, text)

    def _parse_response(self, raw_resp: str, original_text: str) -> LLMClassification:
        """Parses JSON output from LLM, with robust fallback regex matching."""
        try:
            # Extract JSON block
            json_str = raw_resp
            if "```json" in raw_resp:
                json_str = raw_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_resp:
                json_str = raw_resp.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)

            label_str = data.get("label", "").upper()
            action_str = data.get("action", "").upper()
            missing_info = data.get("missing_info", [])
            rationale = data.get("rationale", "LLM classified determinability.")
            confidence = float(data.get("confidence", 0.9))

            # Validate Enum values
            label = DeterminabilityLabel(label_str)
            action = ExpectedAction(action_str)

            return LLMClassification(
                predicted_label=label,
                predicted_action=action,
                identified_missing_info=missing_info,
                clinical_rationale=rationale,
                confidence_score=confidence
            )

        except Exception as e:
            logger.warning(f"Failed to parse LLM classifier JSON response ({e}). Using heuristic fallback.")
            return self._heuristic_fallback(original_text, raw_resp)

    def _heuristic_fallback(self, original_text: str, raw_resp: str) -> LLMClassification:
        """Heuristic text matcher if JSON parsing fails."""
        text_lower = original_text.lower()
        resp_lower = raw_resp.lower()

        # Check emergency keywords with negation detection
        from src.determinability.rules import is_negated
        has_emergency_keyword = False
        for kw in ["difficulty swallowing", "difficulty breathing", "dysphagia", "dyspnea", "stridor", "trismus", "floor of mouth swelling"]:
            if kw in text_lower:
                m = re.search(r"\b" + re.escape(kw) + r"\b", text_lower)
                if m and not is_negated(text_lower, m.start()):
                    has_emergency_keyword = True
                    break

        if "safety-critical" in resp_lower or "emergency" in resp_lower or has_emergency_keyword:
            return LLMClassification(
                predicted_label=DeterminabilityLabel.SAFETY_CRITICAL,
                predicted_action=ExpectedAction.ESCALATE,
                identified_missing_info=[],
                clinical_rationale="Emergency signs or fallback classification.",
                confidence_score=0.8
            )
        elif "underdetermined" in resp_lower or "missing" in text_lower or "what should i take" in text_lower:
            return LLMClassification(
                predicted_label=DeterminabilityLabel.UNDERDETERMINED,
                predicted_action=ExpectedAction.ASK,
                identified_missing_info=["pain_duration", "drug_allergies"],
                clinical_rationale="Missing clinical information detected in text.",
                confidence_score=0.8
            )
        elif "conflicting" in resp_lower or "contradict" in resp_lower:
            return LLMClassification(
                predicted_label=DeterminabilityLabel.CONFLICTING,
                predicted_action=ExpectedAction.ABSTAIN,
                identified_missing_info=[],
                clinical_rationale="Contradictory clinical statements.",
                confidence_score=0.8
            )
        elif "out-of-scope" in resp_lower or "whitening" in text_lower or "aligners" in text_lower:
            return LLMClassification(
                predicted_label=DeterminabilityLabel.OUT_OF_SCOPE,
                predicted_action=ExpectedAction.ABSTAIN,
                identified_missing_info=[],
                clinical_rationale="Out of acute pain/infection domain.",
                confidence_score=0.8
            )

        return LLMClassification(
            predicted_label=DeterminabilityLabel.DETERMINABLE,
            predicted_action=ExpectedAction.ANSWER,
            identified_missing_info=[],
            clinical_rationale="Fully specified clinical case.",
            confidence_score=0.7
        )
