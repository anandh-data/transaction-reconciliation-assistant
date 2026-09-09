from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GeneratedLedgers:
    source: Path
    settlement: Path
    injected: dict[str, int]


def generate_ledgers(destination: Path, rows: int, seed: int) -> GeneratedLedgers:
    if rows < 1000:
        raise ValueError("at least 1,000 transactions are required")
    rng = np.random.default_rng(seed)
    destination.mkdir(parents=True, exist_ok=True)
    identifiers = np.array([f"TXN-{value:08d}" for value in range(1, rows + 1)])
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, rows), unit="D")
    amounts = np.round(rng.lognormal(mean=5.3, sigma=1.1, size=rows), 2)
    base = pd.DataFrame({
        "transaction_id": identifiers,
        "account_id": [f"ACC-{value:06d}" for value in rng.integers(1, 6001, rows)],
        "transaction_date": dates,
        "amount": amounts,
        "currency": "USD",
        "transaction_type": rng.choice(["ACH", "WIRE", "CARD", "CHECK"], rows, p=[0.42, 0.18, 0.30, 0.10]),
    })
    settlement = base.copy()
    missing = rng.choice(settlement.index, 125, replace=False)
    remaining = settlement.index.difference(missing)
    amount_mismatch = rng.choice(remaining, 75, replace=False)
    remaining = remaining.difference(amount_mismatch)
    date_mismatch = rng.choice(remaining, 50, replace=False)
    settlement.loc[amount_mismatch, "amount"] += rng.choice([5.25, 10.50, 25.00], len(amount_mismatch))
    settlement.loc[date_mismatch, "transaction_date"] += pd.to_timedelta(3, unit="D")
    settlement = settlement.drop(missing)
    extras = base.iloc[:25].copy()
    extras["transaction_id"] = [f"SETTLEMENT-ONLY-{value:04d}" for value in range(1, 26)]
    settlement = pd.concat([settlement, extras], ignore_index=True)
    source_path, settlement_path = destination / "source_ledger.parquet", destination / "settlement_ledger.parquet"
    base.to_parquet(source_path, index=False)
    settlement.to_parquet(settlement_path, index=False)
    return GeneratedLedgers(source_path, settlement_path, {"missing_settlement":125,"amount_mismatch":75,"date_mismatch":50,"missing_source":25})
