"""
Sales data tool. Reads a CSV (mock CRM). WHY CSV: zero setup, zero RAM cost,
runs on a 3GB machine. Swap for Google Sheets API later with the same return shape.
"""
import csv
from config import settings


def get_pipeline() -> dict:
    """Load deals and compute simple aggregates the LLM can report on."""
    path = settings.DATA_DIR / "mock_sales.csv"
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        r["value_usd"] = int(r["value_usd"])

    open_deals = [r for r in rows if r["stage"] != "Closed Won"]
    won = [r for r in rows if r["stage"] == "Closed Won"]
    # WHY pre-compute totals: keeps the LLM from doing math (LLMs are unreliable
    # at arithmetic). The tool does numbers; the LLM does language.
    return {
        "total_pipeline_open_usd": sum(r["value_usd"] for r in open_deals),
        "total_won_usd": sum(r["value_usd"] for r in won),
        "num_open_deals": len(open_deals),
        "deals": rows,
        "biggest_deal": max(rows, key=lambda r: r["value_usd"]),
    }
