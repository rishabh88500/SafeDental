import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.config_loader import load_red_flags
from src.determinability.schemas import RuleTrigger
from src.utils.logging import get_logger

logger = get_logger("determinability_rules")


def is_negated(text: str, start_idx: int) -> bool:
    """
    Checks if a keyword occurrence starting at start_idx is preceded by a negation expression
    in the same clause without intervening adversative conjunctions.
    """
    window_start = max(0, start_idx - 60)
    preceding = text[window_start:start_idx]

    # Sentence-ending boundaries (., ;, \n, !, ?)
    boundaries = [m.end() for m in re.finditer(r"[\.\;\n\!\?]", preceding)]
    if boundaries:
        preceding = preceding[max(boundaries):]

    # Check if there is an adversative conjunction that cancels negation (e.g. "no fever, but trismus")
    adversatives = [m.end() for m in re.finditer(r"\b(but|however|although|yet|except|except\s+for)\b", preceding, re.IGNORECASE)]
    if adversatives:
        preceding = preceding[max(adversatives):]

    # Negation trigger patterns (e.g. "no", "not", "denies", "without", "negative for", "absence of", "normal")
    neg_pattern = r"\b(no|not|denies|denied|without|negative\s+for|absence\s+of|rules?\s+out|ruled\s+out|unremarkable\s+for|no\s+evidence\s+of|no\s+signs?\s+of|normal|zero|free\s+of)\b(?:\s+[\w\(\)\-\/]+){0,5}\s*$"
    return bool(re.search(neg_pattern, preceding.strip(), re.IGNORECASE))


class HardSafetyRuleEvaluator:
    """
    Evaluates hard safety red-flag rules against a clinical narrative.
    Pure deterministic keyword and regex matching with clinical negation detection.
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
                kw_lower = kw.lower()
                pattern = r"\b" + re.escape(kw_lower) + r"\b"
                match_indices = [m.start() for m in re.finditer(pattern, normalized_text)]

                if not match_indices and kw_lower in normalized_text:
                    sub_idx = normalized_text.find(kw_lower)
                    while sub_idx != -1:
                        match_indices.append(sub_idx)
                        sub_idx = normalized_text.find(kw_lower, sub_idx + 1)

                # Keyword is confirmed only if AT LEAST ONE occurrence is non-negated
                has_positive_match = False
                for idx in match_indices:
                    if not is_negated(normalized_text, idx):
                        has_positive_match = True
                        break

                if has_positive_match:
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
