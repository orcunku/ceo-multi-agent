"""
LLM client — the ONLY place that talks to a model provider.

WHY a wrapper instead of calling the API directly in each agent:
  1. Swap providers (Groq/Gemini) in one place.
  2. Add retries once, everywhere benefits.
  3. Track tokens/latency once -> you get cost+speed metrics for free in eval.
  4. When you migrate to n8n later, this is the piece n8n's LLM node replaces.
"""
import time
import os
from config import settings


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        # Running totals -> these feed your eval cost/latency charts.
        self.total_calls = 0
        self.total_tokens = 0
        self.total_seconds = 0.0
        self._init_provider()

    def _init_provider(self):
        # Lazy imports: only load the SDK you actually use (saves RAM on a 3GB box).
        if self.provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
            self.model = settings.GROQ_MODEL
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            self.client = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.model = settings.GEMINI_MODEL
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def complete(self, system: str, user: str) -> str:
        """
        One text-in -> text-out call, with retries and metric tracking.
        WHY system+user split: the system message pins the agent's role,
        the user message carries the task. Keeps prompts clean and testable.
        """
        last_err = None
        for attempt in range(settings.MAX_RETRIES + 1):
            try:
                start = time.time()
                text, tokens = self._call(system, user)
                # record metrics
                self.total_calls += 1
                self.total_tokens += tokens
                self.total_seconds += time.time() - start
                return text
            except Exception as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))  # simple backoff
        # WHY raise after retries: agents catch this and return an error
        # envelope instead of crashing the whole system.
        raise RuntimeError(f"LLM failed after retries: {last_err}")

    def _call(self, system: str, user: str):
        if self.provider == "groq":
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens
            return text, tokens
        else:  # gemini
            resp = self.client.generate_content(f"{system}\n\n{user}")
            text = resp.text
            # Gemini free tier doesn't always return token counts cleanly;
            # approximate so cost tracking still works.
            tokens = len((system + user + text).split())
            return text, tokens

    def stats(self) -> dict:
        """Snapshot for eval reporting."""
        return {
            "calls": self.total_calls,
            "tokens": self.total_tokens,
            "avg_latency_s": round(self.total_seconds / max(self.total_calls, 1), 3),
        }
