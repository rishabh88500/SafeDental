from src.kb.clean_text import clean_text


def test_clean_text_removes_artifacts():
    raw = "Dental pulp- \nitis symptoms. Page 1 of 12\n\n\n\nSection 1: Guidelines."
    cleaned = clean_text(raw)
    assert "pulpitis" in cleaned
    assert "Page 1 of 12" not in cleaned
    assert "Section 1: Guidelines." in cleaned
