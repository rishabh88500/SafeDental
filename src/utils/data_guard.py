from pathlib import Path
from typing import List
from src.data.schema import ClinicalCase
from src.utils.logging import get_logger

logger = get_logger("data_guard")


class SealedTestAccessError(PermissionError):
    """Raised when development code attempts to access the sealed test set prematurely."""
    pass


def is_sealed_test_path(file_path: Path) -> bool:
    """Returns True if file_path points to the sealed test set."""
    path_str = str(file_path.resolve())
    return "test.jsonl" in path_str and "data/cases" in path_str


def verify_not_sealed_test(file_path: Path, allow_sealed: bool = False):
    """
    Verifies that file_path is not the sealed test set unless explicitly allowed.
    Raises SealedTestAccessError if violated.
    """
    if not allow_sealed and is_sealed_test_path(file_path):
        error_msg = (
            f"ACCESS DENIED: Attempted to access sealed test set at '{file_path}'. "
            "Development scripts, Arm A baseline dev runs, and prompt tuning MUST NOT access the sealed test set. "
            "The test set is reserved exclusively for final evaluation in Chunk 8."
        )
        logger.error(error_msg)
        raise SealedTestAccessError(error_msg)


def load_cases_safe(file_path: Path, allow_sealed: bool = False) -> List[ClinicalCase]:
    """Loads cases from a JSONL file with sealed test access protection."""
    verify_not_sealed_test(file_path, allow_sealed=allow_sealed)
    if not file_path.exists():
        raise FileNotFoundError(f"Case file not found: {file_path}")

    cases = []
    import json
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(ClinicalCase(**json.loads(line.strip())))
    return cases
