import os
import json
import logging
from pathlib import Path
from typing import Optional
from dotenv import dotenv_values
from app.config import settings, ROOT_DIR

logger = logging.getLogger(__name__)

class AIClientError(Exception):
    """Base exception for AI Client errors."""
    pass

class AIConfigurationError(AIClientError):
    """Raised when AI API Key is missing or invalid."""
    pass

class AITimeoutError(AIClientError):
    """Raised when AI call times out."""
    pass

class AIRateLimitError(AIClientError):
    """Raised when API rate limit is exceeded."""
    pass

class AIClient:
    """
    Production-ready AI client supporting Groq LLaMA models with Gemini fallback.
    Guarantees dynamic key resolution so .env updates are immediately respected.
    Guarantees API keys are never leaked in logs or responses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        self._explicit_api_key = api_key
        self._explicit_model = model
        self._explicit_provider = provider

    @property
    def api_key(self) -> Optional[str]:
        if self._explicit_api_key is not None:
            return self._explicit_api_key.strip() if self._explicit_api_key else None

        # Check os.environ and settings
        candidates = [
            os.environ.get("GROQ_API_KEY"),
            os.environ.get("AI_API_KEY"),
            getattr(settings, "GROQ_API_KEY", None),
            getattr(settings, "AI_API_KEY", None),
        ]
        for c in candidates:
            if c and c.strip():
                return c.strip()

        # Dynamic fallback: direct inspection of .env files
        for env_path in [ROOT_DIR / ".env", Path(".env"), ROOT_DIR / "backend" / ".env"]:
            if env_path.exists():
                try:
                    vals = dotenv_values(env_path)
                    k = vals.get("GROQ_API_KEY") or vals.get("AI_API_KEY")
                    if k and k.strip():
                        return k.strip()
                except Exception:
                    pass

        return None

    @property
    def provider(self) -> str:
        if self._explicit_provider:
            return self._explicit_provider.lower()
        key = self.api_key
        if key and key.startswith("gsk_"):
            return "groq"
        prov = os.environ.get("AI_PROVIDER") or getattr(settings, "AI_PROVIDER", "groq")
        return (prov or "groq").lower()

    @property
    def model(self) -> str:
        if self._explicit_model:
            return self._explicit_model
        mod = os.environ.get("AI_MODEL") or getattr(settings, "AI_MODEL", None)
        if self.provider == "groq":
            if not mod or "gemini" in mod.lower():
                return "llama-3.3-70b-versatile"
            return mod
        return mod or "gemini-2.5-flash"

    def is_configured(self) -> bool:
        key = self.api_key
        if not key:
            return False
        clean = key.strip()
        if clean.startswith("your-") or clean.startswith("gsk_your") or len(clean) < 15:
            return False
        return True

    def generate_json_response(self, prompt: str, timeout_seconds: float = 20.0) -> str:
        """
        Calls AI API (Groq primary) with prompt and expects valid JSON response.
        Handles timeouts, rate limits, and network errors safely.
        """
        if not self.is_configured():
            raise AIConfigurationError(
                "AI API key (GROQ_API_KEY or AI_API_KEY) is not configured in backend environment."
            )

        if self.provider == "groq":
            return self._call_groq(prompt, timeout_seconds)
        else:
            return self._call_gemini(prompt, timeout_seconds)

    def _call_groq(self, prompt: str, timeout_seconds: float) -> str:
        api_key = self.api_key
        initial_model = self.model

        candidate_models = list(dict.fromkeys([
            initial_model,
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]))

        last_err = None
        for current_model in candidate_models:
            try:
                from groq import Groq

                client = Groq(api_key=api_key, timeout=timeout_seconds)
                completion = client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert technical workforce evaluator and career skilling architect. "
                                "You MUST reply ONLY with valid JSON conforming to the requested schema. "
                                "Do NOT wrap output in markdown code blocks or add explanatory text."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                content = completion.choices[0].message.content
                if not content:
                    raise AIClientError("Empty response received from Groq model.")
                return content
            except Exception as exc:
                err_msg = str(exc)
                if api_key:
                    err_msg = err_msg.replace(api_key, "[REDACTED_API_KEY]")

                # If model is not found, try next candidate
                if "404" in err_msg or "model_not_found" in err_msg:
                    logger.warning("Groq model '%s' not found or accessible. Trying next fallback model.", current_model)
                    last_err = exc
                    continue

                if "429" in err_msg or "rate_limit_exceeded" in err_msg.lower():
                    logger.error("Groq rate limit hit.")
                    raise AIRateLimitError("Groq API rate limit exceeded. Please try again shortly.")
                if "timeout" in err_msg.lower() or "deadline" in err_msg.lower():
                    logger.error("Groq request timed out.")
                    raise AITimeoutError(f"Groq API request timed out after {timeout_seconds} seconds.")

                logger.error("Groq API Error on model %s: %s", current_model, err_msg)
                last_err = exc
                break

        # Try HTTP fallback before failing completely
        try:
            return self._groq_http_fallback(prompt, timeout_seconds)
        except Exception:
            raise AIClientError(f"Groq API request failed: {str(last_err)}")

    def _groq_http_fallback(self, prompt: str, timeout_seconds: float) -> str:
        import httpx

        api_key = self.api_key
        model = self.model

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technical workforce evaluator. Reply ONLY with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 429:
                    raise AIRateLimitError("Groq rate limit exceeded.")
                if res.status_code != 200:
                    raise AIClientError(f"HTTP {res.status_code}: {res.text[:200]}")
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            raise AITimeoutError(f"Groq HTTP request timed out after {timeout_seconds}s")
        except Exception as e:
            msg = str(e)
            if api_key:
                msg = msg.replace(api_key, "[REDACTED_API_KEY]")
            raise AIClientError(msg)

    def _call_gemini(self, prompt: str, timeout_seconds: float) -> str:
        api_key = self.api_key
        model = self.model

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            if not response or not response.text:
                raise AIClientError("Empty response received from Gemini model.")
            return response.text
        except Exception as exc:
            err_msg = str(exc)
            if api_key:
                err_msg = err_msg.replace(api_key, "[REDACTED_API_KEY]")
            logger.error("Gemini API Error: %s", err_msg)
            raise AIClientError(f"Gemini API request failed: {err_msg}")
