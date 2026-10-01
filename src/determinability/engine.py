from typing import Optional, List
from src.data.schema import ClinicalCase, DeterminabilityLabel, ExpectedAction
from src.determinability.schemas import DeterminabilityResult, RuleTrigger, ChecklistCoverage, LLMClassification
from src.determinability.rules import HardSafetyRuleEvaluator
from src.determinability.checklist import RequiredInformationChecklistEvaluator
from src.determinability.llm_classifier import LLMDeterminabilityClassifier
from src.utils.logging import get_logger

logger = get_logger("determinability_engine")


class ClinicalDeterminabilityEngine:
    """
    Master Clinical Determinability Engine for SafeDental.
    Combines Hard Safety Red-Flag Rules, Information Coverage Checklist, and LLM Classification.

    Enforces the Safety-First Precedence Rule: Hard safety rules ALWAYS override LLM classification.
    """

    def __init__(
        self,
        rule_evaluator: Optional[HardSafetyRuleEvaluator] = None,
        checklist_evaluator: Optional[RequiredInformationChecklistEvaluator] = None,
        llm_classifier: Optional[LLMDeterminabilityClassifier] = None
    ):
        self.rule_evaluator = rule_evaluator or HardSafetyRuleEvaluator()
        self.checklist_evaluator = checklist_evaluator or RequiredInformationChecklistEvaluator()
        self.llm_classifier = llm_classifier or LLMDeterminabilityClassifier()

    def evaluate_case(self, case: ClinicalCase) -> DeterminabilityResult:
        """Evaluates a structured ClinicalCase instance."""
        narrative = case.to_clinical_narrative()
        return self.evaluate_text(case_id=case.case_id, text=narrative)

    def evaluate_text(self, case_id: str, text: str) -> DeterminabilityResult:
        """
        Evaluates a raw clinical narrative text.

        Returns:
            DeterminabilityResult: Contains label, action, missing_info, triggered_rules, rationale.
        """
        logger.info(f"Evaluating determinability for case '{case_id}'...")

        # Stage 1A: Hard Safety Red-Flag Rules
        triggered_rules: List[RuleTrigger] = self.rule_evaluator.evaluate(text)

        # Stage 1B: Information Coverage Checklist
        checklist_cov: ChecklistCoverage = self.checklist_evaluator.evaluate(text)

        # Stage 2: Secondary LLM Classification
        llm_class: LLMClassification = self.llm_classifier.classify(text)

        # ----------------------------------------------------
        # SAFETY-FIRST PRECEDENCE COMBINER LOGIC
        # ----------------------------------------------------

        # RULE 1: Hard Red Flags -> ALWAYS SAFETY-CRITICAL (ESCALATE)
        if triggered_rules or llm_class.predicted_label == DeterminabilityLabel.SAFETY_CRITICAL:
            rule_cats = [r.rule_category for r in triggered_rules] if triggered_rules else ["LLM detected emergency"]
            rationale = f"Emergency red flag triggered: {', '.join(rule_cats)}. Immediate escalation required."
            logger.warning(f"Case '{case_id}' flagged as SAFETY-CRITICAL ({rationale})")

            return DeterminabilityResult(
                case_id=case_id,
                label=DeterminabilityLabel.SAFETY_CRITICAL,
                action=ExpectedAction.ESCALATE,
                missing_info=[],
                triggered_rules=triggered_rules,
                checklist_status=checklist_cov,
                llm_classification=llm_class,
                final_rationale=rationale,
                is_safety_override=bool(triggered_rules)
            )

        # RULE 2: Out of Scope -> OUT-OF-SCOPE (ABSTAIN)
        if llm_class.predicted_label == DeterminabilityLabel.OUT_OF_SCOPE:
            return DeterminabilityResult(
                case_id=case_id,
                label=DeterminabilityLabel.OUT_OF_SCOPE,
                action=ExpectedAction.ABSTAIN,
                missing_info=[],
                triggered_rules=[],
                checklist_status=checklist_cov,
                llm_classification=llm_class,
                final_rationale=llm_class.clinical_rationale,
                is_safety_override=False
            )

        # RULE 3: Conflicting -> CONFLICTING (ABSTAIN)
        if llm_class.predicted_label == DeterminabilityLabel.CONFLICTING:
            return DeterminabilityResult(
                case_id=case_id,
                label=DeterminabilityLabel.CONFLICTING,
                action=ExpectedAction.ABSTAIN,
                missing_info=[],
                triggered_rules=[],
                checklist_status=checklist_cov,
                llm_classification=llm_class,
                final_rationale=llm_class.clinical_rationale,
                is_safety_override=False
            )

        # RULE 4: Missing Required Information -> UNDERDETERMINED (ASK)
        combined_missing = list(set(checklist_cov.missing_fields + llm_class.identified_missing_info))
        if not checklist_cov.is_complete or llm_class.predicted_label == DeterminabilityLabel.UNDERDETERMINED or combined_missing:
            rationale = f"Clinical case is underdetermined. Missing required fields: {', '.join(combined_missing)}"
            return DeterminabilityResult(
                case_id=case_id,
                label=DeterminabilityLabel.UNDERDETERMINED,
                action=ExpectedAction.ASK,
                missing_info=combined_missing,
                triggered_rules=[],
                checklist_status=checklist_cov,
                llm_classification=llm_class,
                final_rationale=rationale,
                is_safety_override=False
            )

        # RULE 5: Fully Specified Case -> DETERMINABLE (ANSWER)
        return DeterminabilityResult(
            case_id=case_id,
            label=DeterminabilityLabel.DETERMINABLE,
            action=ExpectedAction.ANSWER,
            missing_info=[],
            triggered_rules=[],
            checklist_status=checklist_cov,
            llm_classification=llm_class,
            final_rationale="Clinical case narrative provides sufficient structured information.",
            is_safety_override=False
        )


# Backward compatibility alias
DeterminabilityEngine = ClinicalDeterminabilityEngine

