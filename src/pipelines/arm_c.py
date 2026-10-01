from pathlib import Path
from typing import List, Optional, Dict, Any
from src.data.schema import ClinicalCase, ExpectedAction
from src.determinability.engine import DeterminabilityEngine
from src.rag.retrieve import DentalRetriever
from src.rag.context_builder import build_evidence_context
from src.rag.evidence_verifier import EvidenceVerifier, EvidenceVerificationResult
from src.llm.client import LLMClient
from src.llm.schemas import ModelResponse, PipelineResult
from src.utils.config_loader import load_config, get_project_root, AppConfig
from src.utils.data_guard import load_cases_safe, verify_not_sealed_test
from src.utils.experiment import save_experiment_run
from src.utils.logging import get_logger

logger = get_logger("arm_c_pipeline")


def load_arm_c_prompt(prompt_path: Optional[Path] = None) -> str:
    if prompt_path is None:
        prompt_path = get_project_root() / "src" / "llm" / "prompts" / "arm_c_v1.txt"
    return prompt_path.read_text(encoding="utf-8")


def run_arm_c_on_case(
    case: ClinicalCase,
    client: LLMClient,
    det_engine: DeterminabilityEngine,
    retriever: DentalRetriever,
    verifier: EvidenceVerifier,
    prompt_template: str,
    experiment_id: str,
    prompt_version: str = "arm_c_v1"
) -> PipelineResult:
    """
    Executes Arm C (Full Proposed System: Determinability + Dental RAG + Evidence Verifier).
    Pipeline Flow:
      1. Determinability Engine evaluates case.
      2. If non-answerable (ASK / ABSTAIN / ESCALATE): Stop immediately.
      3. If DETERMINABLE (ANSWER):
         - DentalRetriever fetches top-k evidence chunks
         - ContextBuilder formats evidence string
         - Base LLM generates answer using arm_c_v1.txt
         - EvidenceVerifier measures claim-level support & citation correctness
    """
    det_res = det_engine.evaluate_case(case)

    model_meta = {
        "model_name": client.model_name,
        "temperature": client.config.model.temperature,
        "max_tokens": client.config.model.max_tokens,
        "seed": client.config.model.seed,
        "llm_called": False,
        "rag_retrieved": False
    }

    exp_meta = {
        "experiment_id": experiment_id,
        "prompt_version": prompt_version,
        "determinability_label": det_res.label.value,
        "action": det_res.action.value,
        "hard_rule_triggered": det_res.primary_rule_triggered
    }

    if det_res.action == ExpectedAction.ASK:
        return PipelineResult(
            case_id=case.case_id,
            arm="ARM_C",
            action=ExpectedAction.ASK,
            case_state=det_res.label,
            answer="",
            missing_information=det_res.missing_information,
            safety_message="Additional clinical details are required before safely advising on treatment.",
            model_metadata=model_meta,
            experiment_metadata=exp_meta
        )

    elif det_res.action == ExpectedAction.ABSTAIN:
        return PipelineResult(
            case_id=case.case_id,
            arm="ARM_C",
            action=ExpectedAction.ABSTAIN,
            case_state=det_res.label,
            answer="",
            missing_information=[],
            safety_message=f"Abstain decision: {det_res.primary_rule_triggered or 'Information is conflicting or out of scope.'}",
            model_metadata=model_meta,
            experiment_metadata=exp_meta
        )

    elif det_res.action == ExpectedAction.ESCALATE:
        return PipelineResult(
            case_id=case.case_id,
            arm="ARM_C",
            action=ExpectedAction.ESCALATE,
            case_state=det_res.label,
            answer="",
            missing_information=[],
            safety_message=f"CRITICAL SAFETY ESCALATION: Emergency medical referral required. {det_res.primary_rule_triggered or 'Airway threat or severe spreading infection detected.'}",
            model_metadata=model_meta,
            experiment_metadata=exp_meta
        )

    # DETERMINABLE -> Retrieve Evidence + Call LLM + Verify Evidence
    model_meta["rag_retrieved"] = True
    query_text = case.to_clinical_narrative()
    retrieval_res = retriever.retrieve(query_text)
    evidence_context = build_evidence_context(retrieval_res.retrieved_chunks)

    model_meta["llm_called"] = True
    messages = [
        {"role": "system", "content": prompt_template},
        {
            "role": "user",
            "content": (
                f"CLINICAL CASE:\n{query_text}\n\n"
                f"RETRIEVED DENTAL EVIDENCE CONTEXT:\n{evidence_context}"
            )
        }
    ]

    raw_llm_text = client.generate(messages)

    # Verify Evidence & Citations
    verification_res = verifier.verify(raw_llm_text, retrieval_res.retrieved_chunks)
    extracted_citations = [chk.citation_str for chk in retrieval_res.retrieved_chunks]

    return PipelineResult(
        case_id=case.case_id,
        arm="ARM_C",
        action=ExpectedAction.ANSWER,
        case_state=det_res.label,
        answer=raw_llm_text,
        missing_information=[],
        safety_message="",
        retrieved_evidence=retrieval_res.retrieved_chunks,
        citations=extracted_citations,
        verification=verification_res,
        model_metadata=model_meta,
        experiment_metadata=exp_meta
    )


def run_arm_c_experiment(
    cases_path: Path,
    experiment_id: str,
    config: Optional[AppConfig] = None,
    allow_sealed_test: bool = False,
    force_mock: bool = False,
    limit: Optional[int] = None
) -> Path:
    """
    Executes Arm C full system experiment over case dataset file.
    SAFEGUARD: Rejects access to data/cases/test.jsonl unless allow_sealed_test=True.
    """
    verify_not_sealed_test(cases_path, allow_sealed=allow_sealed_test)

    cfg = config or load_config()
    project_root = get_project_root()
    cases = load_cases_safe(cases_path, allow_sealed=allow_sealed_test)

    if limit is not None and limit > 0:
        cases = cases[:limit]

    prompt_template = load_arm_c_prompt()
    client = LLMClient(config=cfg, force_mock=force_mock)
    det_engine = DeterminabilityEngine(config=cfg, llm_client=client)
    retriever = DentalRetriever(default_top_k=cfg.retrieval.top_k)
    verifier = EvidenceVerifier()

    logger.info(f"Starting Arm C proposed system experiment '{experiment_id}' on {len(cases)} cases from '{cases_path.name}'...")
    pipeline_results: List[PipelineResult] = []

    for idx, c in enumerate(cases, 1):
        res = run_arm_c_on_case(
            c,
            client,
            det_engine,
            retriever,
            verifier,
            prompt_template,
            experiment_id=experiment_id
        )
        pipeline_results.append(res)

    model_responses: List[ModelResponse] = []
    for pr in pipeline_results:
        c_found = next(c for c in cases if c.case_id == pr.case_id)
        model_responses.append(
            ModelResponse(
                case_id=pr.case_id,
                experiment_id=experiment_id,
                pipeline_arm="ARM_C",
                model_name=client.model_name,
                prompt_version="arm_c_v1",
                raw_response=pr.answer or pr.safety_message,
                parsed_answer=pr.answer or pr.safety_message,
                predicted_action=pr.action,
                predicted_missing_info=pr.missing_information,
                citations=pr.citations,
                temperature=client.config.model.temperature,
                max_tokens=client.config.model.max_tokens,
                seed=client.config.model.seed,
                gold_determinability_label=c_found.determinability_label,
                gold_expected_action=c_found.expected_action,
                gold_safety_risk=c_found.safety_risk.value
            )
        )

    exp_dir = save_experiment_run(experiment_id, "ARM_C", model_responses, cfg, project_root)
    return exp_dir
