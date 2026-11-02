
import os
from src.llm.client import LLMClient, ClaudeClient, GeminiClient


def test_llm_client_mock():
    client = LLMClient(force_mock=True)
    messages = [{"role": "user", "content": "Patient presenting with sharp localized pain in tooth #30."}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert len(resp) > 10
    assert "RECOMMENDATION:" in resp


def test_claude_client_init():
    cl_client = ClaudeClient(
        api_base="https://api.anthropic.com/v1",
        model_name="claude-opus-5.5",
        timeout=60
    )
    assert cl_client.model_name == "claude-opus-5.5"
    assert cl_client.timeout == 60


def test_claude_client_fallback_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    client = LLMClient(force_mock=False)
    client.provider = "claude"
    messages = [{"role": "user", "content": "Test prompt"}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert "RECOMMENDATION:" in resp


def test_gemini_client_init():
    gem_client = GeminiClient(
        api_base="https://generativelanguage.googleapis.com/v1beta",
        model_name="gemini-3.8-flash",
        timeout=60
    )
    assert gem_client.model_name == "gemini-3.8-flash"
    assert gem_client.timeout == 60


def test_gemini_client_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = LLMClient(force_mock=False)
    client.provider = "gemini"
    messages = [{"role": "user", "content": "Test prompt"}]
    resp = client.generate(messages)
    assert isinstance(resp, str)
    assert "RECOMMENDATION:" in resp
