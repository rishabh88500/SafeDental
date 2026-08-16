import os
from src.llm.client import LLMClient, OpenRouterClient


def test_llm_client_mock():
    client = LLMClient(force_mock=True)
    messages = [{"role": "user", "content": "Patient presenting with sharp localized pain in tooth #30."}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert len(resp) > 10
    assert "RECOMMENDATION:" in resp


def test_openrouter_client_init():
    or_client = OpenRouterClient(
        api_base="https://openrouter.ai/api/v1",
        model_name="meta-llama/llama-3.1-8b-instruct",
        timeout=120
    )
    assert or_client.api_base == "https://openrouter.ai/api/v1"
    assert or_client.model_name == "meta-llama/llama-3.1-8b-instruct"


def test_openrouter_client_fallback_without_key(monkeypatch):
    # Ensure OPENROUTER_API_KEY is unset for test
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = LLMClient(force_mock=False)
    messages = [{"role": "user", "content": "Test prompt"}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert "RECOMMENDATION:" in resp
