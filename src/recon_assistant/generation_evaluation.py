from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    return 0.0 if denominator == 0 else float(np.dot(left, right) / denominator)


def evaluate_generation(supported_cases, unsupported_questions, retrieve, generate, embedder, destination: Path) -> dict:
    supported_rows = []
    for case in supported_cases:
        response = generate(case["question"], retrieve(case["question"]))
        cited_pages = [item["page"] for item in response["citations"]]
        citation_correct = any(page in case["expected_pages"] for page in cited_pages)
        context = response.pop("context", "")
        similarity = 0.0
        if response["grounded"] and context:
            vectors = embedder.documents([response["answer"], context], batch_size=2, show_progress=False)
            similarity = cosine(vectors[0], vectors[1])
        supported_rows.append({
            **response,
            "expected_pages": case["expected_pages"],
            "citation_correct": citation_correct,
            "answer_context_similarity": round(similarity, 4),
            "key_facts_present": all(
                term.lower() in response["answer"].lower() for term in case["required_terms"]
            ),
        })

    unsupported_rows = []
    for question in unsupported_questions:
        response = generate(question, retrieve(question))
        response.pop("context", None)
        unsupported_rows.append({**response, "correct_abstention": not response["grounded"]})

    payload = {
        "supported_questions": len(supported_rows),
        "unsupported_questions": len(unsupported_rows),
        "citation_accuracy": sum(row["citation_correct"] for row in supported_rows) / len(supported_rows),
        "key_fact_accuracy": sum(row["key_facts_present"] for row in supported_rows) / len(supported_rows),
        "mean_answer_context_similarity": sum(row["answer_context_similarity"] for row in supported_rows) / len(supported_rows),
        "correct_abstention_rate": sum(row["correct_abstention"] for row in unsupported_rows) / len(unsupported_rows),
        "supported_results": supported_rows,
        "unsupported_results": unsupported_rows,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
