import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from recon_assistant.evaluation import evaluate_cases
from recon_assistant.retrieval import SearchResult


def test_evaluation_metrics(tmp_path: Path):
    cases = [{"question_id": "Q1", "question": "q", "expected_pages": [2]}]
    results = [SearchResult("a", 1, "", "", 0.8), SearchResult("b", 2, "", "", 0.7)]
    payload = evaluate_cases(cases, lambda _: results, tmp_path / "evaluation.json")
    assert payload["hit_rate_at_5"] == 1.0
    assert payload["mean_reciprocal_rank"] == 0.5


def test_hit_at_5_excludes_relevant_results_after_fifth_place(tmp_path: Path):
    cases = [
        {"question_id": "Q1", "question": "fifth", "expected_pages": [5]},
        {"question_id": "Q2", "question": "sixth", "expected_pages": [6]},
        {"question_id": "Q3", "question": "missing", "expected_pages": [99]},
    ]
    results = [SearchResult(str(page), page, "", "", 0.8) for page in range(1, 7)]
    destination = tmp_path / "evaluation.json"
    payload = evaluate_cases(cases, lambda _: results, destination)

    assert [row["hit_at_5"] for row in payload["results"]] == [True, False, False]
    assert payload["hit_rate_at_5"] == 1 / 3
    # Reciprocal rank still considers all returned results, not just the first five.
    assert payload["results"][1]["reciprocal_rank"] == 1 / 6
    assert payload["results"][1]["retrieved_pages"] == [1, 2, 3, 4, 5, 6]
    assert json.loads(destination.read_text()) == payload


def test_hit_at_5_with_no_retrieved_results(tmp_path: Path):
    cases = [{"question_id": "Q1", "question": "q", "expected_pages": [2]}]
    payload = evaluate_cases(cases, lambda _: [], tmp_path / "evaluation.json")
    assert payload["hit_rate_at_5"] == 0
    assert payload["mean_reciprocal_rank"] == 0


@pytest.mark.parametrize("existing_report", [False, True])
def test_empty_evaluation_rejects_input_without_changing_report(tmp_path, existing_report):
    destination = tmp_path / "evaluation.json"
    original = '{"previous": "result"}\n'
    if existing_report:
        destination.write_text(original)
    retrieve = Mock()

    with pytest.raises(ValueError, match="at least one evaluation case"):
        evaluate_cases([], retrieve, destination)

    retrieve.assert_not_called()
    if existing_report:
        assert destination.read_text() == original
    else:
        assert not destination.exists()
