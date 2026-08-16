import pytest
from src.data.schema import DeterminabilityLabel, ExpectedAction, ClinicalCase, PatientContext, SafetyRisk
from src.determinability.rules import HardSafetyRuleEvaluator
from src.determinability.checklist import RequiredInformationChecklistEvaluator
from src.determinability.llm_classifier import LLMDeterminabilityClassifier
from src.determinability.engine import ClinicalDeterminabilityEngine


def test_hard_safety_rule_evaluator_airway():
    rule_eval = HardSafetyRuleEvaluator()
    text = "Patient having severe toothache and difficulty swallowing with floor of mouth swelling."
    triggers = rule_eval.evaluate(text)

    assert len(triggers) >= 1
    assert any(t.rule_category == "airway" for t in triggers)
    assert any("difficulty swallowing" in t.matched_keywords for t in triggers)


def test_hard_safety_rule_evaluator_trismus():
    rule_eval = HardSafetyRuleEvaluator()
    text = "Lower molar infection with severe trismus and limited mouth opening."
    triggers = rule_eval.evaluate(text)

    assert len(triggers) >= 1
    assert any(t.rule_category == "spreading_fascial_space" for t in triggers)


def test_required_information_checklist_incomplete():
    chk_eval = RequiredInformationChecklistEvaluator()
    text = "My tooth hurts and I need antibiotics."
    cov = chk_eval.evaluate(text)

    assert cov.is_complete is False
    assert "pain_duration" in cov.missing_fields
    assert "drug_allergies" in cov.missing_fields


def test_required_information_checklist_complete():
    chk_eval = RequiredInformationChecklistEvaluator()
    text = "28M with localized pain in tooth #30 for 3 days. Gums slightly tender, no swelling, temperature 98.6F. No medical history or drug allergies."
    cov = chk_eval.evaluate(text)

    assert cov.is_complete is True
    assert len(cov.missing_fields) == 0


def test_determinability_engine_safety_override():
    engine = ClinicalDeterminabilityEngine()
    text = "Tooth ache for 2 days, now having high fever 102F, chills, and difficulty breathing."
    res = engine.evaluate_text("test-001", text)

    assert res.label == DeterminabilityLabel.SAFETY_CRITICAL
    assert res.action == ExpectedAction.ESCALATE
    assert res.is_safety_override is True
    assert len(res.triggered_rules) >= 1


def test_determinability_engine_underdetermined():
    engine = ClinicalDeterminabilityEngine()
    text = "My lower tooth hurts. Can I take amoxicillin?"
    res = engine.evaluate_text("test-002", text)

    assert res.label == DeterminabilityLabel.UNDERDETERMINED
    assert res.action == ExpectedAction.ASK
    assert len(res.missing_info) > 0


def test_determinability_engine_determinable():
    engine = ClinicalDeterminabilityEngine()
    text = "35F presenting with sharp pain in lower right tooth #30 when drinking cold water, lasting 5 seconds. Pain started 2 days ago. No swelling, no fever (temp 98.4F). No medical conditions, no drug allergies."
    res = engine.evaluate_text("test-003", text)

    assert res.label == DeterminabilityLabel.DETERMINABLE
    assert res.action == ExpectedAction.ANSWER
    assert len(res.missing_info) == 0
