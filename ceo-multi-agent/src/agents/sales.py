"""
Sales agent. Same pattern as Engineering (fetch -> phrase -> envelope).
WHY reuse the pattern: consistency makes the system predictable and easy to
extend. A new agent = copy this file, swap the tool.
"""
from src.agents.base_agent import BaseAgent
from src.tools import sheets_tool

SYSTEM = """You are the Sales department agent reporting to a CEO.
Use ONLY the pipeline data provided. Never invent numbers. Be concise.
End your answer with a line: CONFIDENCE: <0.0-1.0>"""


class SalesAgent(BaseAgent):
    name = "sales"
    description = "Revenue, pipeline, leads, deals, forecasts."

    def run(self, query: str, context: dict) -> dict:
        try:
            data = sheets_tool.get_pipeline()
            user = f"CEO question: {query}\n\nPipeline data:\n{data}"
            raw = self.llm.complete(SYSTEM, user)
            answer, conf = _split_confidence(raw)
            sources = [d["deal"] for d in data["deals"]]
            return self._envelope(answer, confidence=conf, sources=sources)
        except Exception as e:
            return self._envelope(
                "Sales agent could not complete the request.",
                confidence=0.0, error=str(e),
            )


def _split_confidence(raw: str):
    conf = 0.5
    lines = raw.strip().splitlines()
    if lines and lines[-1].upper().startswith("CONFIDENCE:"):
        try:
            conf = float(lines[-1].split(":", 1)[1].strip())
        except ValueError:
            pass
        raw = "\n".join(lines[:-1]).strip()
    return raw, conf
