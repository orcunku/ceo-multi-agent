"""
Central configuration. WHY: one place to change model names, thresholds,
and file paths so you never hunt through code. Also makes eval reproducible —
every run records which settings produced which numbers.
"""
import os
from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
EVAL_RESULTS_DIR = ROOT / "eval" / "results"
DB_PATH = ROOT / "memory.db"

# --- LLM provider ---
# WHY a single switch: swap Groq <-> Gemini without touching agent code.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")   # "groq" or "gemini"
GROQ_MODEL = "llama-3.1-8b-instant"                # free, fast
GEMINI_MODEL = "gemini-1.5-flash"                  # free tier

# --- Behaviour thresholds ---
# WHY expose these: they are the knobs you tune during optimization.
LLM_TEMPERATURE = 0.2        # low = consistent routing/answers (good for eval)
MAX_RETRIES = 2              # retry failed LLM calls before giving up
LOW_CONFIDENCE_THRESHOLD = 0.4  # below this, orchestrator flags "uncertain"

# --- Registry of agents the orchestrator can route to ---
# WHY here: the router prompt is built from this, so adding an agent =
# one edit here, not scattered strings.
AGENT_REGISTRY = {
    "engineering": "Software development, GitHub PRs, issues, sprints, bugs, releases.",
    "sales": "Revenue, pipeline, leads, deals, forecasts, customers.",
    "research": "External market info, competitors, industry news, general web lookups.",
}
