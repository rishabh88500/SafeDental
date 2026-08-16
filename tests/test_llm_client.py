from src.llm.client import LLMClient


def test_llm_client_mock():
    client = LLMClient(force_mock=True)
    messages = [{"role": "user", "content": "Patient presenting with sharp localized pain in tooth #30."}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert len(resp) > 10
    assert "RECOMMENDATION:" in resp
