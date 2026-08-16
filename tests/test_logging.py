import logging
import tempfile
from pathlib import Path
from src.utils.logging import get_logger


def test_get_logger_console():
    logger = get_logger("test_logger_console")
    assert logger.name == "test_logger_console"
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1


def test_get_logger_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test.log"
        logger = get_logger("test_logger_file", log_file=log_path)
        logger.info("Test log message")
        
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert "Test log message" in content
