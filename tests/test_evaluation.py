from pathlib import Path

from recon_assistant.evaluation import evaluate_cases
from recon_assistant.retrieval import SearchResult


def test_evaluation_metrics(tmp_path: Path):
    cases = [{"question_id": "Q1", "question": "q", "expected_pages": [2]}]
    results = [SearchResult("a", 1, "", "", 0.8), SearchResult("b", 2, "", "", 0.7)]
    payload = evaluate_cases(cases, lambda _: results, tmp_path / "evaluation.json")
    assert payload["hit_rate_at_5"] == 1.0
    assert payload["mean_reciprocal_rank"] == 0.5
