CEO Multi-Agent System


🌐 Try the Live Demo →
https://ceo-multi-agent-mnbhwnldk5nv2per92ovpb.streamlit.app/ A multi-agent AI assistant for a company executive. A central Orchestrator agent routes each question to the right department agent (Engineering, Sales, Research), which answers using real data — not guesses. Built with a strong focus on evaluation: the system is measured, tested, and provably improved.

Built to run on modest hardware (3 GB RAM). All model inference is remote (Groq free tier), so nothing heavy runs locally.

How it works
                 ┌─────────────────────────────┐
   CEO asks  ──▶ │      Orchestrator Agent      │
                 │  (classifies + routes query) │
                 └───────────────┬─────────────┘
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
          ┌────────────┐  ┌────────────┐  ┌────────────┐
          │Engineering │  │   Sales    │  │  Research  │
          │  (GitHub)  │  │(CRM/Sheets)│  │ (web/LLM)  │
          └────────────┘  └────────────┘  └────────────┘
Core design principle — "the tool thinks, the agent talks": Each agent fetches structured facts from a tool (which does the counting and math), then the LLM only phrases those facts. This prevents hallucinated numbers — the single most important reliability decision in the system.

Every agent returns the same output shape (an "envelope" with answer, confidence, sources, error), so the orchestrator treats them uniformly and new agents plug in without changing routing logic.

Evaluation & Results
The project includes an evaluation harness (eval/) with 20 labelled test cases covering routing, exact-number correctness, and deliberately ambiguous queries.

Three metrics are tracked: routing accuracy (did the orchestrator pick the right agent?), answer score (did the answer contain the correct facts?), and confidence calibration (do high-confidence answers actually turn out correct?).

The improvement story
Stage	Answer Score	What changed
Initial hard-quiz baseline	90%	Two failures surfaced
After fixing a real routing/data bug	95%	Tool now pre-computes "biggest deal"
After correcting the eval checks	100%	Check for facts (numbers), not phrasing
Final: Routing 100% · Answers 100% · Failures 0% · Calibration perfect.

Two distinct failure types were diagnosed along the way: a genuine system bug (the agent picked the wrong "biggest" deal because it reasoned over the list itself) and a flawed test (the checker demanded exact wording the LLM legitimately varied). Telling these apart — and fixing each correctly — is the heart of the project.

Quick start
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your free Groq API key
#    (get one at https://console.groq.com)
cp .env.example .env         # then edit .env and paste your key

# 3. Ask the system a question
python main.py "What's our biggest deal right now?"

# 4. Run the full evaluation
python -m eval.run_eval
Project structure
ceo-multi-agent/
├── main.py                 # entry point + build_system() factory
├── config/settings.py      # models, thresholds, agent registry
├── src/
│   ├── orchestrator.py     # routing + dispatch
│   ├── llm_client.py       # single LLM wrapper (retries, token tracking)
│   ├── agents/             # engineering, sales, research (+ base contract)
│   └── tools/              # data fetching (GitHub, sheets) — mock, API-ready
├── eval/
│   ├── test_cases.jsonl    # 20 labelled test queries
│   ├── metrics.py          # routing / answer / calibration metrics
│   ├── run_eval.py         # runs the suite, saves timestamped CSVs
│   └── results/            # saved run history (proof of improvement)
└── data/mock_sales.csv     # sample CRM data

Tech stack
LLM: Groq (Llama 3.1 8B) — free tier, fast. Swappable to Google Gemini in one setting.
Language: Pure Python — no heavy local dependencies.
Data: Mock GitHub + CSV "CRM" (swap in real APIs without changing agent logic).
Roadmap
Real GitHub API and Google Sheets integrations (interfaces already in place)
Web search + retrieval (RAG) for the Research agent
LLM-as-judge scoring for nuanced answer quality
Optional n8n orchestration layer — each agent maps to one sub-workflow, since every agent already shares the same input/output contract
Design decisions worth noting
Tools compute, LLMs phrase — numbers are never invented.
Routing is isolated and measured — the #1 failure point gets its own metric.
Uniform agent contract — makes the system extensible and n8n-ready.
Evaluation-first — every change is verified against a saved baseline.
