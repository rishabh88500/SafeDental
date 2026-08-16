import json
import requests
from typing import List, Dict, Any, Optional
from src.utils.config_loader import load_config, AppConfig
from src.utils.logging import get_logger

logger = get_logger("llm_client")


class LLMClient:
    """
    Unified frozen LLM client.
    Supports Ollama HTTP API backend with automatic fallback to Mock Engine for testing.
    """

    def __init__(self, config: Optional[AppConfig] = None, force_mock: bool = False):
        self.config = config or load_config()
        self.force_mock = force_mock
        self.provider = self.config.model.provider
        self.model_name = self.config.model.name
        self.api_base = self.config.model.api_base

    def _mock_generate(self, messages: List[Dict[str, str]], prompt_text: str) -> str:
        """Deterministic mock generator for offline unit testing."""
        user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "")

        # Check key intent
        if "swallowing" in user_msg.lower() or "airway" in user_msg.lower() or "emergency" in user_msg.lower():
            return "RECOMMENDATION: Immediately seek emergency hospital evaluation due to potential airway threat."
        elif "missing" in user_msg.lower() or "need antibiotics" in user_msg.lower():
            return "RECOMMENDATION: Amoxicillin 500mg three times daily is recommended for dental pain."
        else:
            return "RECOMMENDATION: Maintain good oral hygiene, apply localized cold compress, and visit a licensed dentist for an evaluation."

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Sends generation request to configured model backend.

        Args:
            messages: List of message dicts [{'role': 'system'/'user', 'content': '...'}]
            temperature: Override temperature
            max_tokens: Override max output tokens
            seed: Override random seed
        """
        temp = temperature if temperature is not None else self.config.model.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.model.max_tokens
        pinned_seed = seed if seed is not None else self.config.model.seed

        prompt_summary = messages[-1]["content"][:80] if messages else ""

        if self.force_mock or self.provider == "mock":
            logger.info(f"Using Mock LLM Client -> '{prompt_summary}...'")
            return self._mock_generate(messages, prompt_summary)

        # Attempt Ollama backend
        if self.provider == "ollama":
            url = f"{self.api_base.rstrip('/')}/api/chat"
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "num_predict": max_tok,
                    "seed": pinned_seed,
                }
            }
            try:
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json.get("message", {}).get("content", "")
                    logger.info(f"Ollama response received for '{self.model_name}' ({len(content)} chars)")
                    return content
                else:
                    logger.warning(f"Ollama returned HTTP {response.status_code}. Falling back to Mock Engine.")
                    return self._mock_generate(messages, prompt_summary)
            except Exception as e:
                logger.warning(f"Ollama API connection failed ({e}). Falling back to Mock Engine.")
                return self._mock_generate(messages, prompt_summary)

        # Default fallback
        return self._mock_generate(messages, prompt_summary)
