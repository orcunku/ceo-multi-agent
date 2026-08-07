"""
Research agent — handles external/general questions and acts as the fallback.
For now it answers from the LLM's own knowledge (with a note). WHY: keeps the
system runnable with zero API keys beyond the LLM. Swap in a web-search tool
(Tavily/DuckDuckGo) later inside run() without changing the interface.
"""
from src.agents.base_agent import BaseAgent

SYSTEM = """You are the Research agent reporting to a CEO. Provide concise,
factual answers about markets, competitors, or general topics. If you are not
sure or the info may be outdated, say so explicitly.
End your answer with a line: CONFIDENCE: <0.0-1.0>"""


class ResearchAgent(BaseAgent):
    name = "research"
    description = "External market info, competitors, industry news, general lookups."

    def run(self, query: str, context: dict) -> dict:
        try:
            # LATER: results = search_tool.search(query); feed into user prompt.
            user = f"CEO question: {query}"
            raw = self.llm.complete(SYSTEM, user)
            answer, conf = _split_confidence(raw)
            return self._envelope(answer, confidence=conf,
                                  sources=["LLM prior knowledge"])
        except Exception as e:
            return self._envelope(
                "Research agent could not complete the request.",
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
