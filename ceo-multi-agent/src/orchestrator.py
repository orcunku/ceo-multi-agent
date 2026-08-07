"""
Orchestrator — the "CEO's agent". Two jobs:
  1. ROUTE: pick which department agent should handle the query.
  2. RETURN: hand back the agent's answer (plus routing info for eval).

WHY routing is a separate LLM step: it's the #1 place multi-agent systems fail.
By isolating it, you can MEASURE routing accuracy independently from answer
quality — the core of your statistical evaluation.
"""
from config import settings


class Orchestrator:
    def __init__(self, llm, agents: dict):
        self.llm = llm
        self.agents = agents  # {"engineering": EngineeringAgent(...), ...}

    def route(self, query: str) -> str:
        """
        Ask the LLM to classify the query into ONE agent name.
        WHY build the prompt from AGENT_REGISTRY: descriptions live in config,
        so routing stays in sync automatically when you add/remove agents.
        """
        options = "\n".join(
            f"- {name}: {desc}" for name, desc in settings.AGENT_REGISTRY.items()
        )
        system = (
            "You are a router. Choose the single best department for the query. "
            "Reply with ONLY the department name, nothing else."
        )
        user = f"Departments:\n{options}\n\nQuery: {query}\n\nDepartment:"
        choice = self.llm.complete(system, user).strip().lower()

        # WHY normalize + fallback: LLMs sometimes add punctuation or a stray word.
        for name in self.agents:
            if name in choice:
                return name
        return "research"  # safe default: general web-capable agent

    def handle(self, query: str, context: dict | None = None) -> dict:
        """Full pipeline: route -> run agent -> attach routing info for eval."""
        context = context or {}
        chosen = self.route(query)
        result = self.agents[chosen].run(query, context)
        # WHY attach routing_agent: eval compares this to the expected agent
        # to compute routing accuracy.
        result["routing_agent"] = chosen
        # WHY flag low confidence: mirrors real product behavior — surface
        # uncertainty to the CEO instead of hiding it.
        result["uncertain"] = result.get("confidence", 0) < settings.LOW_CONFIDENCE_THRESHOLD
        return result
