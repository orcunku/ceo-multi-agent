from dotenv import load_dotenv
load_dotenv()



"""
Eval runner. Runs the SAME system over every test case, records results,
prints a scorecard, and saves a timestamped CSV.

WHY timestamped CSVs: each optimization run is saved, so you can plot
before/after and PROVE your changes improved the system. That evidence is the
single most impressive thing in the repo.

Run:  python -m eval.run_eval
"""
import json
import csv
import datetime
from pathlib import Path

from main import build_system
from config import settings
from eval import metrics


def load_cases():
    path = Path(__file__).parent / "test_cases.jsonl"
    return [json.loads(line) for line in open(path) if line.strip()]


def run():
    orch, llm = build_system()
    cases = load_cases()
    records = []

    for c in cases:
        result = orch.handle(c["query"])
        answer = (result.get("answer") or "")
        # keyword check: are all expected strings present? (case-insensitive)
        contains_ok = all(
            kw.lower() in answer.lower() for kw in c.get("expected_contains", [])
        )
        records.append({
            "id": c["id"],
            "query": c["query"],
            "expected_agent": c["expected_agent"],
            "routed": result["routing_agent"],
            "confidence": result["confidence"],
            "answer": answer.replace("\n", " ")[:200],
            "contains_ok": contains_ok,
            "error": result.get("error"),
        })

    # --- scorecard ---
    print("\n===== SCORECARD =====")
    print(f"Routing accuracy : {metrics.routing_accuracy(records):.0%}")
    print(f"Answer score     : {metrics.answer_score(records):.0%}")
    print(f"Failure rate     : {metrics.failure_rate(records):.0%}")
    print("Calibration:")
    for b in metrics.calibration(records):
        print(f"  {b['bucket']:14} n={b['n']:2}  actual_acc={b['actual_accuracy']}")
    print(f"LLM stats        : {llm.stats()}")

    # --- save for before/after comparison ---
    settings.EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = settings.EVAL_RESULTS_DIR / f"run_{ts}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=records[0].keys())
        w.writeheader()
        w.writerows(records)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    run()
