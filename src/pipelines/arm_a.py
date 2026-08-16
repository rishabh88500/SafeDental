import re
from pathlib import Path
from typing import List, Optional
from src.data.schema import ClinicalCase, ExpectedAction
from src.llm.client import LLMClient
from src.llm.schemas import ModelResponse
from src.utils.config_loader import load_config, get_project_root, AppConfig
from src.utils.data_guard import load_cases_safe, verify_not_sealed_test
from src.utils.experiment import save_experiment_run
from src.utils.logging import get_logger

logger = get_logger("arm_a_pipeline")


def load_arm_a_prompt(prompt_path: Optional[Path] = None) -> str:
    if prompt_path is None:
        prompt_path = get_project_root() / "src" / "llm" / "prompts" / "arm_a_v1.txt"
    return prompt_path.read_text(encoding="utf-8")


def parse_arm_a_response(raw_text: str) -> ExpectedAction:
    """
    Adapter parsing raw LLM baseline response for predicted action.
    Arm A provides unconstrained answers, so default action is ANSWER unless blunt refusal is detected.
    """
    text_lower = raw_text.lower()
    if "emergency" in text_lower or "immediate hospital" in text_lower or "call 911" in text_lower:
        return ExpectedAction.ESCALATE
    elif "cannot answer" in text_lower or "refuse to advise" in text_lower:
        return ExpectedAction.ABSTAIN
    elif "please clarify" in text_lower or "provide missing details" in text_lower:
        return ExpectedAction.ASK
    return ExpectedAction.ANSWER


def run_arm_a_on_case(
    case: ClinicalCase,
    client: LLMClient,
    prompt_template: str,
    experiment_id: str,
    prompt_version: str = "arm_a_v1"
) -> ModelResponse:
    """Runs Arm A baseline pipeline on a single clinical case."""
    messages = [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": case.to_clinical_narrative()}
    ]

    raw_resp = client.generate(messages)
    predicted_act = parse_arm_a_response(raw_resp)

    return ModelResponse(
        case_id=case.case_id,
        experiment_id=experiment_id,
        pipeline_arm="ARM_A",
        model_name=client.model_name,
        prompt_version=prompt_version,
        raw_response=raw_resp,
        parsed_answer=raw_resp,
        predicted_action=predicted_act,
        temperature=client.config.model.temperature,
        max_tokens=client.config.model.max_tokens,
        seed=client.config.model.seed,
        gold_determinability_label=case.determinability_label,
        gold_expected_action=case.expected_action,
        gold_safety_risk=case.safety_risk.value,
    )


def run_arm_a_experiment(
    cases_path: Path,
    experiment_id: str,
    config: Optional[AppConfig] = None,
    allow_sealed_test: bool = False,
    force_mock: bool = False
) -> Path:
    """
    Executes Arm A baseline pipeline over a case dataset file.
    SAFEGUARD: Rejects access to data/cases/test.jsonl unless allow_sealed_test=True.
    """
    # Enforce data protection guard
    verify_not_sealed_test(cases_path, allow_sealed=allow_sealed_test)

    cfg = config or load_config()
    project_root = get_project_root()
    cases = load_cases_safe(cases_path, allow_sealed=allow_sealed_test)

    prompt_template = load_arm_a_prompt()
    client = LLMClient(config=cfg, force_mock=force_mock)

    logger.info(f"Starting Arm A baseline experiment '{experiment_id}' on {len(cases)} cases from '{cases_path.name}'...")
    responses: List[ModelResponse] = []

    for idx, c in enumerate(cases, 1):
        resp = run_arm_a_on_case(c, client, prompt_template, experiment_id=experiment_id)
        responses.append(resp)
        if idx % 20 == 0 or idx == len(cases):
            logger.info(f"Processed {idx}/{len(cases)} cases...")

    exp_dir = save_experiment_run(experiment_id, "ARM_A", responses, cfg, project_root)
    return exp_dir
