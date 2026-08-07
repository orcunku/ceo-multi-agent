"""
Engineering agent. Pattern for ALL data agents:
  1. Fetch structured data (tool).
  2. Give data + question to the LLM.
  3. Return a clean envelope.

WHY this order: the LLM never guesses numbers — it only phrases facts the tool
provided. This is how you keep agents accurate and avoid hallucinated metrics.
"""
from src.agents.base_agent import BaseAgent
from src.tools import github_tool

SYSTEM = """You are the Engineering department agent reporting to a CEO.
Answer ONLY using the data provided. Be concise and executive-friendly.
If the data doesn't cover the question, say so plainly.
End your answer with a line: CONFIDENCE: <0.0-1.0>"""


class EngineeringAgent(BaseAgent):
    name = "engineering"
    description = "GitHub PRs, issues, sprints, bugs, releases."

    def run(self, query: str, context: dict) -> dict:
        try:
            data = github_tool.get_recent_activity()  # step 1: facts
            # step 2: LLM phrases the facts to answer the question
            user = f"CEO question: {query}\n\nEngineering data:\n{data}"
            raw = self.llm.complete(SYSTEM, user)
            answer, conf = _split_confidence(raw)
            # sources = traceability: which PRs backed this answer
            sources = [f"PR#{p['num']}" for p in data["recent_prs"]]
            return self._envelope(answer, confidence=conf, sources=sources)
        except Exception as e:
            # WHY catch: one agent failing must NOT crash the system.
            return self._envelope(
                "Engineering agent could not complete the request.",
                confidence=0.0, error=str(e),
            )


def _split_confidence(raw: str):
    """
    Pull the self-rated confidence off the end of the answer.
    WHY have the LLM rate itself: gives you a confidence signal to test in the
    calibration analysis (does 0.9 confidence actually mean 90% correct?).
    """
    conf = 0.5
    lines = raw.strip().splitlines()
    if lines and lines[-1].upper().startswith("CONFIDENCE:"):
        try:
            conf = float(lines[-1].split(":", 1)[1].strip())
        except ValueError:
            pass
        raw = "\n".join(lines[:-1]).strip()
    return raw, conf
