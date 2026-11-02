import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
from pydantic import ValidationError
from src.data.schema import ClinicalCase
from src.utils.logging import get_logger

logger = get_logger("validate_schema")


def validate_case_dict(case_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates a single case dictionary against the ClinicalCase Pydantic model."""
    try:
        ClinicalCase(**case_dict)
        return True, []
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return False, errors


def validate_jsonl_file(file_path: Path) -> Tuple[bool, int, List[str]]:
    """
    Validates all cases in a JSONL file.

    Returns:
        (is_valid_file, total_cases, error_messages)
    """
    if not file_path.exists():
        return False, 0, [f"File not found: {file_path}"]

    all_errors = []
    total_cases = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str:
                continue
            total_cases += 1
            try:
                data = json.loads(line_str)
            except json.JSONDecodeError as err:
                all_errors.append(f"Line {idx}: Invalid JSON syntax ({err})")
                continue

            valid, errs = validate_case_dict(data)
            if not valid:
                all_errors.append(f"Line {idx} (ID: {data.get('case_id', 'UNKNOWN')}): {'; '.join(errs)}")

    is_valid = len(all_errors) == 0
    return is_valid, total_cases, all_errors


if __name__ == "__main__":
    from src.utils.config_loader import load_config
    cfg = load_config()
    target_file = Path(cfg.dataset.validated_path)
    logger.info(f"Validating dataset file: {target_file}")
    valid, count, errors = validate_jsonl_file(target_file)
    if valid:
        logger.info(f"SUCCESS: All {count} cases passed schema validation!")
    else:
        logger.error(f"FAILURE: {len(errors)} validation errors out of {count} cases:")
        for err in errors[:10]:
            logger.error(f"  - {err}")
