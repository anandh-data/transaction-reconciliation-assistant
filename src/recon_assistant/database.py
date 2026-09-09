from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values

from .documents import Chunk


def execute_file(dsn: str, path: Path) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(path.read_text())


def load_document(dsn: str, document: dict, chunks: list[Chunk], embeddings) -> None:
    rows = [(chunk.chunk_id, document["document_id"], chunk.page_number, chunk.chunk_index, chunk.section_title, chunk.content, chunk.content_sha256, vector) for chunk, vector in zip(chunks, embeddings)]
    with psycopg2.connect(dsn) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute("truncate table recon.document_chunk, recon.document cascade")
            cursor.execute("insert into recon.document(document_id,title,source_url,source_sha256,page_count) values(%s,%s,%s,%s,%s)", (document["document_id"], document["title"], document["source_url"], document["source_sha256"], document["page_count"]))
            execute_values(cursor, "insert into recon.document_chunk(chunk_id,document_id,page_number,chunk_index,section_title,content,content_sha256,embedding) values %s", rows, page_size=250)


def load_ledgers(dsn: str, source_path: Path, settlement_path: Path) -> dict[str, int]:
    counts = {}
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("truncate table recon.reconciliation_result, recon.ledger_transaction")
        for ledger, path in [("source", source_path), ("settlement", settlement_path)]:
            frame = pd.read_parquet(path)
            frame.insert(1, "ledger_name", ledger)
            buffer = io.StringIO()
            frame.to_csv(buffer, index=False, header=False, date_format="%Y-%m-%d")
            buffer.seek(0)
            cursor.copy_expert("copy recon.ledger_transaction(transaction_id,ledger_name,account_id,transaction_date,amount,currency,transaction_type) from stdin with(format csv)", buffer)
            counts[ledger] = len(frame)
    return counts


def reconcile(dsn: str, sql_path: Path, amount_tolerance: float, date_tolerance_days: int) -> dict[str, int]:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute(sql_path.read_text(), {"amount_tolerance": amount_tolerance, "date_tolerance_days": date_tolerance_days})
        cursor.execute("select status,count(*) from recon.reconciliation_result group by status order by status")
        return {status: count for status, count in cursor.fetchall()}


def audit(dsn: str, run_id: str, event_type: str, details: dict) -> None:
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("insert into recon.audit_event(run_id,event_type,details) values(%s,%s,%s::jsonb)", (run_id, event_type, json.dumps(details)))


def store_evaluation(dsn: str, evaluation: dict) -> None:
    rows = [
        (row["question_id"], row["question"], row["expected_pages"], row["retrieved_pages"], row["hit_at_5"], row["reciprocal_rank"])
        for row in evaluation["results"]
    ]
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("truncate table recon.retrieval_evaluation")
        execute_values(
            cursor,
            """insert into recon.retrieval_evaluation
               (question_id,question,expected_pages,retrieved_pages,hit_at_5,reciprocal_rank) values %s""",
            rows,
        )


def export_exceptions(dsn: str, destination: Path) -> int:
    with psycopg2.connect(dsn) as connection:
        frame = pd.read_sql_query(
            """select transaction_id,status,source_amount,settlement_amount,amount_difference,
                      date_difference_days,reason
               from recon.reconciliation_result where status <> 'matched'
               order by status,transaction_id""",
            connection,
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    return len(frame)
