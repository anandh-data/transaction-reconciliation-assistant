from __future__ import annotations

import json
from pathlib import Path


def evaluate_cases(cases: list[dict], retrieve, destination: Path) -> dict:
    rows = []
    for case in cases:
        results = retrieve(case["question"])
        pages = [result.page_number for result in results]
        ranks = [index + 1 for index, page in enumerate(pages) if page in case["expected_pages"]]
        rows.append({
            "question_id": case["question_id"], "question": case["question"],
            "expected_pages": case["expected_pages"], "retrieved_pages": pages,
            "hit_at_5": bool(ranks), "reciprocal_rank": 0 if not ranks else 1 / min(ranks),
        })
    payload = {
        "questions": len(rows),
        "hit_rate_at_5": sum(row["hit_at_5"] for row in rows) / len(rows),
        "mean_reciprocal_rank": sum(row["reciprocal_rank"] for row in rows) / len(rows),
        "results": rows,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
