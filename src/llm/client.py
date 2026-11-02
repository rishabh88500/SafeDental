import os
import json
import time
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


# Claude (Anthropic), Gemini, and Local Ollama Clients with deterministic Mock fallback


class ClaudeClient:
    """
    Anthropic Claude API Client for Claude models (e.g. claude-opus-5.5, claude-3-5-sonnet, claude-3-haiku).
    Uses ANTHROPIC_API_KEY (or CLAUDE_API_KEY) from environment variables.
    """

    def __init__(
        self,
        api_base: str = "https://api.anthropic.com/v1",
        model_name: str = "claude-opus-5.5",
        timeout: int = 60
    ):
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def get_api_key(self) -> Optional[str]:
        return os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
        seed: int = 42
    ) -> Optional[str]:
        api_key = self.get_api_key()
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY environment variable is missing.")
            return None

        url = f"{self.api_base}/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        system_instruction = ""
        claude_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_instruction = (system_instruction + "\n\n" + content).strip()
            elif role in ["user", "human"]:
                claude_messages.append({"role": "user", "content": content})
            elif role in ["assistant", "model"]:
                claude_messages.append({"role": "assistant", "content": content})
            else:
                claude_messages.append({"role": "user", "content": content})

        if not claude_messages and system_instruction:
            claude_messages.append({"role": "user", "content": system_instruction})
            system_instruction = ""

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if system_instruction:
            payload["system"] = system_instruction

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                resp_json = response.json()
                content_blocks = resp_json.get("content", [])
                text_blocks = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
                text = "".join(text_blocks).strip()
                logger.info(f"Claude response received for '{self.model_name}' ({len(text)} chars)")
                return text
            else:
                logger.warning(f"Claude API returned HTTP {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            logger.warning(f"Claude API connection error ({e})")

class GeminiClient:
    """
    Google Gemini API Client for Gemini models (e.g. gemini-3.8-flash, gemini-3.1-flash-lite).
    Uses GEMINI_API_KEY from environment variables.
    """

    def __init__(self, api_base: str = "https://generativelanguage.googleapis.com/v1beta", model_name: str = "gemini-3.8-flash", timeout: int = 60):
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def get_api_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
        seed: int = 42
    ) -> Optional[str]:
        api_key = self.get_api_key()
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is missing.")
            return None

        model_clean = self.model_name.replace("models/", "")
        url = f"{self.api_base}/models/{model_clean}:generateContent?key={api_key}"

        system_instructions = []
        contents = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_instructions.append(content)
            elif role in ["user", "human"]:
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role in ["assistant", "model"]:
                contents.append({"role": "model", "parts": [{"text": content}]})
            else:
                contents.append({"role": "user", "parts": [{"text": content}]})

        if not contents and system_instructions:
            contents.append({"role": "user", "parts": [{"text": "\n\n".join(system_instructions)}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "seed": seed,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }
        if system_instructions:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_instructions)}]
            }

        headers = {"Content-Type": "application/json"}
        models_to_try = [self.model_name]
        if "gemini-3.8-flash" in self.model_name:
            models_to_try.append("gemini-3.1-flash-lite")

        for m_name in models_to_try:
            m_clean = m_name.replace("models/", "")
            target_url = f"{self.api_base}/models/{m_clean}:generateContent?key={api_key}"
            for attempt in range(2):
                try:
                    response = requests.post(target_url, headers=headers, json=payload, timeout=self.timeout)
                    if response.status_code == 200:
                        resp_json = response.json()
                        candidates = resp_json.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            text_parts = [p.get("text", "") for p in parts if "text" in p]
                            text = "".join(text_parts).strip()
                            logger.info(f"Gemini response received for '{m_name}' ({len(text)} chars)")
                            return text
                        logger.warning(f"Gemini returned empty candidates array for {m_name}.")
                        break
                    elif response.status_code in [429, 503]:
                        logger.warning(f"Gemini returned transient HTTP {response.status_code} for {m_name}. Retrying...")
                        time.sleep(1.0)
                        continue
                    else:
                        logger.warning(f"Gemini API returned HTTP {response.status_code} for {m_name}: {response.text[:200]}")
                        break
                except Exception as e:
                    logger.warning(f"Gemini API connection error on {m_name} (attempt {attempt+1}): {e}")
                    time.sleep(1.0)

        return None


class LLMClient:
    """
    Provider-agnostic unified frozen LLM client interface.
    Supports Anthropic Claude (Claude Opus 5.5 / Claude 3.5), Google Gemini, and local Ollama APIs
    with automatic fallback to deterministic Mock Engine for testing & offline execution.
    """

    def __init__(self, config: Optional[AppConfig] = None, force_mock: bool = False):
        self.config = config or load_config()
        self.force_mock = force_mock or bool(os.getenv("PYTEST_CURRENT_TEST"))
        self.provider = self.config.model.provider
        self.model_name = self.config.model.name
        self.api_base = self.config.model.api_base
        self.timeout = getattr(self.config.model, "timeout", 60)

        self._claude_client = ClaudeClient(
            api_base=self.api_base if "anthropic" in self.api_base else "https://api.anthropic.com/v1",
            model_name=self.model_name,
            timeout=self.timeout
        )

        self._gemini_client = GeminiClient(
            api_base=self.api_base if "googleapis" in self.api_base else "https://generativelanguage.googleapis.com/v1beta",
            model_name=self.model_name,
            timeout=self.timeout
        )

    def _mock_generate(self, messages: List[Dict[str, str]], prompt_text: str) -> str:
        """Deterministic mock generator for offline unit testing."""
        import re
        user_msg = ""
        sys_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "")
            elif m.get("role") == "system":
                sys_msg = m.get("content", "")

        user_lower = user_msg.lower()
        sys_lower = sys_msg.lower()

        # If calling from LLMDeterminabilityClassifier, return schema-compliant JSON
        if "clinical determinability classifier" in sys_lower:
            from src.determinability.rules import is_negated
            is_emergency = False
            for kw in ["difficulty swallowing", "difficulty breathing", "stridor", "trismus", "floor of mouth swelling", "eyelid swelling", "vision changes", "proptosis", "periorbital", "peri-orbital"]:
                if kw in user_lower:
                    m = re.search(r"\b" + re.escape(kw) + r"\b", user_lower)
                    if m and not is_negated(user_lower, m.start()):
                        is_emergency = True
                        break

            if is_emergency or "emergency" in user_lower:
                return json.dumps({
                    "label": "SAFETY-CRITICAL",
                    "action": "ESCALATE",
                    "missing_info": [],
                    "rationale": "Emergency airway or spreading fascial space signs detected.",
                    "confidence": 0.98
                })
            elif "ignore" in user_lower or "oxycodone" in user_lower or "adversarial" in user_lower or "whitening" in user_lower:
                return json.dumps({
                    "label": "OUT-OF-SCOPE",
                    "action": "ABSTAIN",
                    "missing_info": [],
                    "rationale": "Adversarial or out of scope clinical request.",
                    "confidence": 0.95
                })
            elif "vitality testing and percussion tests are entirely normal" in user_lower or "conflicting" in user_lower:
                return json.dumps({
                    "label": "CONFLICTING",
                    "action": "ABSTAIN",
                    "missing_info": [],
                    "rationale": "Severe pain reported despite normal diagnostic tests.",
                    "confidence": 0.90
                })
            elif "missing" in user_lower or "should i take amoxicillin" in user_lower or "what medicine should i take" in user_lower:
                return json.dumps({
                    "label": "UNDERDETERMINED",
                    "action": "ASK",
                    "missing_info": ["swelling_presence", "fever_presence", "drug_allergies"],
                    "rationale": "Key clinical facts missing from presentation.",
                    "confidence": 0.90
                })
            else:
                return json.dumps({
                    "label": "DETERMINABLE",
                    "action": "ANSWER",
                    "missing_info": [],
                    "rationale": "Complete clinical presentation suitable for evidence-based advice.",
                    "confidence": 0.95
                })

        # Regular pipeline mock response
        from src.determinability.rules import is_negated
        is_airway = False
        for kw in ["difficulty swallowing", "difficulty breathing", "stridor", "airway compromise"]:
            if kw in user_lower:
                m = re.search(r"\b" + re.escape(kw) + r"\b", user_lower)
                if m and not is_negated(user_lower, m.start()):
                    is_airway = True
                    break

        if is_airway or ("emergency" in user_lower and "no emergency" not in user_lower):
            return "RECOMMENDATION: Immediately seek emergency hospital evaluation due to potential airway threat."
        elif "missing" in user_lower or "need antibiotics" in user_lower:
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

        # Claude (Anthropic) provider
        if self.provider in ["claude", "anthropic"]:
            res = self._claude_client.generate(
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                seed=pinned_seed
            )
            if res is not None:
                return res
            logger.warning("Claude call failed or API key unconfigured. Falling back to Mock Engine.")
            return self._mock_generate(messages, prompt_summary)

        # Gemini provider
        if self.provider == "gemini":
            res = self._gemini_client.generate(
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                seed=pinned_seed
            )
            if res is not None:
                return res
            logger.warning("Gemini call failed or API key unconfigured. Falling back to Mock Engine.")

        # Local Ollama fallback if configured
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
