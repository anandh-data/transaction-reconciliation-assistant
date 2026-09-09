from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from recon_assistant.config import load_settings
from recon_assistant.database import audit, execute_file, export_exceptions, load_document, load_ledgers, reconcile, store_evaluation
from recon_assistant.documents import extract_chunks, file_sha256
from recon_assistant.embeddings import LocalEmbeddings
from recon_assistant.evaluation import evaluate_cases
from recon_assistant.retrieval import grounded_response, search
from recon_assistant.transactions import generate_ledgers


def run() -> dict:
    settings = load_settings(ROOT)
    started = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    execute_file(settings.dsn, ROOT / "db/init.sql")
    pages, chunks = extract_chunks(settings.source_file, settings.chunk_size, settings.chunk_overlap)
    embedder = LocalEmbeddings(settings.embedding_model)
    vectors = embedder.documents([chunk.content for chunk in chunks])
    document = {"document_id":"ffiec-bsa-aml-2010","title":"FFIEC BSA/AML Examination Manual (2010)","source_url":settings.source_url,"source_sha256":file_sha256(settings.source_file),"page_count":pages}
    load_document(settings.dsn, document, chunks, vectors)
    ledgers = generate_ledgers(ROOT / "data/generated", settings.transaction_count, settings.seed)
    ledger_counts = load_ledgers(settings.dsn, ledgers.source, ledgers.settlement)
    reconciliation = reconcile(settings.dsn, ROOT / "sql/reconcile.sql", settings.amount_tolerance, settings.date_tolerance_days)
    cases = json.loads((ROOT / "evaluation/questions.json").read_text())["questions"]
    retrieve = lambda question: search(settings.dsn, embedder.query(question), question, settings.top_k)
    evaluation = evaluate_cases(cases, retrieve, ROOT / "evidence/retrieval-evaluation.json")
    store_evaluation(settings.dsn, evaluation)
    answers = [grounded_response(case["question"], retrieve(case["question"]), settings.minimum_score) for case in cases]
    (ROOT / "evidence/grounded-answers.json").write_text(json.dumps({"answers": answers}, indent=2) + "\n")
    exception_rows = export_exceptions(settings.dsn, ROOT / "evidence/reconciliation-exceptions.csv")
    summary = {
        "run_id": run_id, "status": "passed", "manual_pages": pages, "indexed_passages": len(chunks),
        "embedding_model": settings.embedding_model, "embedding_dimensions": settings.dimensions,
        "transactions": ledger_counts, "injected_exceptions": ledgers.injected,
        "reconciliation_results": reconciliation, "exported_exception_rows": exception_rows,
        "retrieval_questions": evaluation["questions"],
        "hit_rate_at_5": evaluation["hit_rate_at_5"], "mean_reciprocal_rank": evaluation["mean_reciprocal_rank"],
        "started_at": started.isoformat(), "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    audit(settings.dsn, run_id, "pipeline_completed", summary)
    (ROOT / "evidence/pipeline-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run()
