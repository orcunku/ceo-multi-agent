from dotenv import load_dotenv
load_dotenv()


"""
Entry point. WHY a build_system() factory: both main.py AND the eval script
need an identical, freshly-wired system. One factory = no duplicated setup and
guarantees eval tests the same system you demo.

Run:  python main.py "How many PRs were merged last week?"
"""
import sys
from src.llm_client import LLMClient
from src.orchestrator import Orchestrator
from src.agents.engineering import EngineeringAgent
from src.agents.sales import SalesAgent
from src.agents.research import ResearchAgent


def build_system():
    llm = LLMClient()  # shared -> one token counter across all agents
    agents = {
        "engineering": EngineeringAgent(llm),
        "sales": SalesAgent(llm),
        "research": ResearchAgent(llm),
    }
    return Orchestrator(llm, agents), llm


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What's our open pipeline value?"
    orch, llm = build_system()
    result = orch.handle(query)

    print(f"\nQuery : {query}")
    print(f"Routed: {result['routing_agent']}")
    print(f"Conf  : {result['confidence']}  Uncertain: {result['uncertain']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")
    print(f"LLM stats: {llm.stats()}")
