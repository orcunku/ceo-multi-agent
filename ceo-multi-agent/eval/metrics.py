"""
Metrics — the statistical core. Each function answers ONE question about the
system so you can improve them independently.
"""


def routing_accuracy(records: list[dict]) -> float:
    """
    Did the orchestrator pick the right agent?
    WHY separate from answer quality: a wrong route guarantees a wrong answer,
    so you fix routing FIRST. This isolates that failure mode.
    """
    correct = sum(r["routed"] == r["expected_agent"] for r in records)
    return correct / len(records)


def answer_score(records: list[dict]) -> float:
    """
    Did the answer contain the expected facts? (keyword check)
    WHY keyword-match for v1: free, deterministic, no extra LLM cost. Upgrade to
    LLM-as-judge later for nuance. Start cheap, get a baseline, then refine.
    """
    passed = sum(r["contains_ok"] for r in records)
    return passed / len(records)


def failure_rate(records: list[dict]) -> float:
    """% of runs that errored or returned empty. WHY: reliability is its own axis."""
    failed = sum(bool(r["error"]) or not r["answer"] for r in records)
    return failed / len(records)


def calibration(records: list[dict]) -> list[dict]:
    """
    Bucket answers by confidence, then check how often each bucket is actually
    correct. WHY: reveals over/under-confidence. If '0.9' answers are only 60%
    right, the system's confidence is misleading — a real, reportable finding.
    """
    buckets = {"low(<0.5)": [], "mid(0.5-0.8)": [], "high(>=0.8)": []}
    for r in records:
        c = r["confidence"]
        key = "low(<0.5)" if c < 0.5 else "mid(0.5-0.8)" if c < 0.8 else "high(>=0.8)"
        buckets[key].append(r["contains_ok"])
    out = []
    for k, vals in buckets.items():
        if vals:
            out.append({"bucket": k, "n": len(vals),
                        "actual_accuracy": round(sum(vals) / len(vals), 2)})
    return out
