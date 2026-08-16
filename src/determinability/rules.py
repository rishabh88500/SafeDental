import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.config_loader import load_red_flags
from src.determinability.schemas import RuleTrigger
from src.utils.logging import get_logger

logger = get_logger("determinability_rules")


class HardSafetyRuleEvaluator:
    """
    Evaluates hard safety red-flag rules against a clinical narrative.
    Pure deterministic keyword and regex matching.
    """

    def __init__(self, red_flags_config: Optional[Dict[str, Any]] = None):
        self.config = red_flags_config or load_red_flags()
        self.rules = self.config.get("red_flags", {})

    def evaluate(self, text: str) -> List[RuleTrigger]:
        """
        Evaluates input narrative text against configured red flag rules.

        Returns:
            List[RuleTrigger]: List of all triggered red flag rules.
        """
        if not text:
            return []

        normalized_text = text.lower()
        triggers: List[RuleTrigger] = []

        for category_name, rule_data in self.rules.items():
            keywords = rule_data.get("keywords", [])
            matched = []

            for kw in keywords:
                # Use regex word boundary or exact substring match
                pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                if re.search(pattern, normalized_text) or kw.lower() in normalized_text:
                    matched.append(kw)

            if matched:
                trigger = RuleTrigger(
                    rule_category=category_name,
                    severity=rule_data.get("severity", "HIGH_CRITICAL"),
                    action=rule_data.get("action", "ESCALATE"),
                    matched_keywords=matched,
                    rationale=rule_data.get("rationale", "Safety red flag detected.")
                )
                triggers.append(trigger)
                logger.info(f"Triggered safety red-flag rule '{category_name}' (matched: {matched})")

        return triggers
