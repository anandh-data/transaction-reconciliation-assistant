from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from psycopg2.extensions import make_dsn


@dataclass(frozen=True)
class Settings:
    root: Path
    seed: int
    transaction_count: int
    source_file: Path
    source_url: str
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    dimensions: int
    top_k: int
    minimum_score: float
    generation_model: str
    max_input_tokens: int
    max_output_tokens: int
    evidence_gate_score: float
    amount_tolerance: float
    date_tolerance_days: int
    dsn: str


def load_settings(root: Path) -> Settings:
    raw = yaml.safe_load((root / "config/pipeline.yml").read_text())
    dsn = make_dsn(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=os.getenv("POSTGRES_PORT", "55433"),
        dbname=os.getenv("POSTGRES_DB", "reconciliation"),
        user=os.getenv("POSTGRES_USER", "reconciliation"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me"),
    )
    return Settings(
        root=root,
        seed=int(raw["run"]["seed"]),
        transaction_count=int(raw["run"]["transaction_count"]),
        source_file=root / raw["documents"]["source_file"],
        source_url=raw["documents"]["source_url"],
        chunk_size=int(raw["documents"]["chunk_size"]),
        chunk_overlap=int(raw["documents"]["chunk_overlap"]),
        embedding_model=raw["retrieval"]["embedding_model"],
        dimensions=int(raw["retrieval"]["dimensions"]),
        top_k=int(raw["retrieval"]["top_k"]),
        minimum_score=float(raw["retrieval"]["minimum_score"]),
        generation_model=raw["generation"]["model"],
        max_input_tokens=int(raw["generation"]["max_input_tokens"]),
        max_output_tokens=int(raw["generation"]["max_output_tokens"]),
        evidence_gate_score=float(raw["generation"]["evidence_gate_score"]),
        amount_tolerance=float(raw["reconciliation"]["amount_tolerance"]),
        date_tolerance_days=int(raw["reconciliation"]["date_tolerance_days"]),
        dsn=dsn,
    )
