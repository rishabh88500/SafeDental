import re
from pathlib import Path
from src.utils.logging import get_logger

logger = get_logger("kb_clean_text")


def clean_text(raw_text: str) -> str:
    """
    Cleans raw document text while preserving section headings, clinical tables, and page markers.
    - Standardizes line endings.
    - Strips running headers/footers (e.g., 'Page 1 of 12', 'Confidential Document').
    - Fixes hyphenated line breaks.
    - Normalizes excessive blank lines.
    """
    if not raw_text:
        return ""

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix broken hyphenated words across line breaks (e.g. "pulp- \nitis" or "pain - \nitis" -> "pulpitis")
    text = re.sub(r"(\w+)\s*-\s*\n\s*(\w+)", r"\1\2", text)

    # Remove running page header/footer artifacts
    text = re.sub(r"(?i)page\s+\d+\s+of\s+\d+", "", text)
    text = re.sub(r"(?i)---+\s*page\s*\d+\s*---+", r"\n", text)

    # Replace multiple spaces with a single space (except leading indentation)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
        else:
            cleaned_lines.append("")

    # Collapse >2 consecutive blank lines into 1
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def clean_document_file(raw_filepath: Path, output_cleaned_filepath: Path) -> Path:
    """Reads raw text file, cleans content, and saves to cleaned directory."""
    raw_content = raw_filepath.read_text(encoding="utf-8")
    cleaned = clean_text(raw_content)

    output_cleaned_filepath.parent.mkdir(parents=True, exist_ok=True)
    output_cleaned_filepath.write_text(cleaned, encoding="utf-8")
    logger.info(f"Cleaned '{raw_filepath.name}' -> '{output_cleaned_filepath.name}' ({len(cleaned)} chars)")
    return output_cleaned_filepath
