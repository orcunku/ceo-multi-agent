"""
BaseAgent — the shared contract EVERY agent obeys.

WHY this matters most:
  - Same input (query, context) -> same output shape (envelope) for all agents.
  - The orchestrator can treat every agent identically -> clean routing.
  - When you move to n8n, each agent's run() becomes one sub-workflow with
    the SAME input/output, so no logic rewrite.
This "standard envelope" is the backbone of the whole system.
"""
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base"
    description: str = "base agent"

    def __init__(self, llm):
        # WHY inject the llm: agents don't create their own client. Makes them
        # testable (you can pass a fake llm in eval) and share one token counter.
        self.llm = llm

    @abstractmethod
    def run(self, query: str, context: dict) -> dict:
        """Subclasses implement this. Must return an envelope via self._envelope()."""
        ...

    def _envelope(self, answer, confidence=0.5, sources=None, error=None) -> dict:
        """
        The ONE output shape used everywhere.
        WHY each field:
          answer     -> the response text
          confidence -> agent's self-rating; feeds calibration analysis
          sources    -> traceability (which PR, which row, which URL)
          error      -> non-None means this agent failed; orchestrator can fall back
        """
        return {
            "agent": self.name,
            "answer": answer,
            "confidence": confidence,
            "sources": sources or [],
            "error": error,
        }
