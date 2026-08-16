import pytest
from pathlib import Path
from src.utils.data_guard import verify_not_sealed_test, SealedTestAccessError, is_sealed_test_path


def test_is_sealed_test_path():
    test_path = Path("data/cases/test.jsonl")
    dev_path = Path("data/cases/dev.jsonl")
    assert is_sealed_test_path(test_path) is True
    assert is_sealed_test_path(dev_path) is False


def test_sealed_test_guard_raises_error():
    test_path = Path("data/cases/test.jsonl")
    with pytest.raises(SealedTestAccessError):
        verify_not_sealed_test(test_path, allow_sealed=False)


def test_sealed_test_guard_allows_dev():
    dev_path = Path("data/cases/dev.jsonl")
    verify_not_sealed_test(dev_path, allow_sealed=False)  # Should not raise
