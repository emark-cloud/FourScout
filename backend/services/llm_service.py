"""LLM service for generating plain-language risk rationales.

Uses Google Gemini (free tier). Provider abstraction allows swapping to Anthropic later.
"""

from config import settings


class LLMService:
    """Generates natural language explanations for risk scores."""

    def __init__(self):
        self.provider = "gemini"
        self.client = None
        self.model = "gemini-2.0-flash"
        self._init_client()

    def _init_client(self):
        if not settings.gemini_api_key:
            print("[LLM] No GEMINI_API_KEY set — rationale generation disabled")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)
        except ImportError:
            print("[LLM] google-genai not installed")
        except Exception as e:
            print(f"[LLM] Init error: {e}")

    async def generate_rationale(self, token_data: dict, risk_signals: dict) -> str:
        """Generate a 2-3 sentence risk explanation."""
        if not self.client:
            return self._fallback_rationale(risk_signals)

        # Build signal summary for the prompt
        signal_lines = []
        for name, data in risk_signals.items():
            if isinstance(data, dict):
                signal_lines.append(f"- {name}: {data.get('score', '?')}/10 — {data.get('detail', 'N/A')}")

        token_name = token_data.get("name", "Unknown")
        token_symbol = token_data.get("symbol", "???")
        grade = "unknown"
        for data in risk_signals.values():
            if isinstance(data, dict):
                # Just get the overall grade from the data
                pass

        prompt = f"""You are a memecoin risk analyst for Four.meme (BNB Chain).
Given these risk signals for token {token_name} (${token_symbol}):

{chr(10).join(signal_lines)}

Write a 2-3 sentence plain language explanation of the risk assessment.
Be specific about the biggest concern or opportunity.
No jargon, no financial advice disclaimers.
Keep it under 80 words."""

        try:
            from google.genai import types
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                ),
            )
            return response.text.strip()
        except Exception as e:
            print(f"[LLM] Generation error: {e}")
            return self._fallback_rationale(risk_signals)

    async def classify_description(self, description: str) -> str:
        """Classify a token description as legit/scam/hype."""
        if not self.client or not description:
            return "unknown"

        prompt = f"""Classify this memecoin description into one category: legit, scam, or hype.
Only respond with one word.

Description: {description[:500]}"""

        try:
            from google.genai import types
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=10),
            )
            result = response.text.strip().lower()
            if result in ("legit", "scam", "hype"):
                return result
            return "unknown"
        except Exception:
            return "unknown"

    def _fallback_rationale(self, risk_signals: dict) -> str:
        """Generate a basic rationale without LLM."""
        worst = None
        for name, data in risk_signals.items():
            if isinstance(data, dict):
                score = data.get("score", 5)
                weight = data.get("weight", 1)
                if worst is None or (score * weight) < (worst[1] * worst[2]):
                    worst = (name, score, weight, data.get("detail", ""))

        if worst:
            return f"Primary concern: {worst[0].replace('_', ' ')} — {worst[3]}"
        return "Risk assessment computed. Check individual signal scores for details."


# Singleton
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
