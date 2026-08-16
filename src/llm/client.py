import os
import json
import requests
from typing import List, Dict, Any, Optional
from src.utils.config_loader import load_config, AppConfig
from src.utils.logging import get_logger

logger = get_logger("llm_client")

# Attempt to load .env if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class OpenRouterClient:
    """
    OpenRouter API Client for OpenAI-compatible chat completions.
    Uses OPENROUTER_API_KEY from environment variables.
    """

    def __init__(self, api_base: str, model_name: str, timeout: int = 120):
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def get_api_key(self) -> Optional[str]:
        return os.getenv("OPENROUTER_API_KEY")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
        seed: int = 42
    ) -> Optional[str]:
        api_key = self.get_api_key()
        if not api_key:
            logger.warning("OPENROUTER_API_KEY environment variable is missing.")
            return None

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/rishabh88500/SafeDental",
            "X-Title": "SafeDental Research Project",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                resp_json = response.json()
                choices = resp_json.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    logger.info(f"OpenRouter response received for '{self.model_name}' ({len(content)} chars)")
                    return content
                else:
                    logger.warning("OpenRouter returned empty choices array.")
                    return None
            else:
                logger.warning(f"OpenRouter API returned HTTP {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            logger.warning(f"OpenRouter API connection failed: {e}")
            return None


class LLMClient:
    """
    Provider-agnostic unified frozen LLM client interface.
    Supports OpenRouter API with automatic fallback to Mock Engine for testing & offline execution.
    """

    def __init__(self, config: Optional[AppConfig] = None, force_mock: bool = False):
        self.config = config or load_config()
        self.force_mock = force_mock
        self.provider = self.config.model.provider
        self.model_name = self.config.model.name
        self.api_base = self.config.model.api_base
        self.timeout = getattr(self.config.model, "timeout", 120)

        self._openrouter_client = OpenRouterClient(
            api_base=self.api_base,
            model_name=self.model_name,
            timeout=self.timeout
        )

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

        # OpenRouter provider
        if self.provider == "openrouter":
            res = self._openrouter_client.generate(
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                seed=pinned_seed
            )
            if res is not None:
                return res
            logger.warning("OpenRouter call failed or API key unconfigured. Falling back to Mock Engine.")
            return self._mock_generate(messages, prompt_summary)

        # Legacy Ollama fallback if configured
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
                response = requests.post(url, json=payload, timeout=self.timeout)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json.get("message", {}).get("content", "")
                    logger.info(f"Ollama response received for '{self.model_name}' ({len(content)} chars)")
                    return content
            except Exception as e:
                logger.warning(f"Ollama connection failed ({e}). Falling back to Mock Engine.")

        # Default fallback
        return self._mock_generate(messages, prompt_summary)
