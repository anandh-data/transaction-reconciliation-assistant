from pathlib import Path

import pandas as pd

from recon_assistant.transactions import generate_ledgers


def test_generator_is_deterministic_and_injects_contract(tmp_path: Path):
    result = generate_ledgers(tmp_path, 25_000, 2026)
    source = pd.read_parquet(result.source)
    settlement = pd.read_parquet(result.settlement)
    assert len(source) == 25_000
    assert len(settlement) == 24_900
    assert source.transaction_id.is_unique and settlement.transaction_id.is_unique
    assert result.injected == {
        "missing_settlement": 125,
        "amount_mismatch": 75,
        "date_mismatch": 50,
        "missing_source": 25,
    }


def test_generator_rejects_too_few_rows(tmp_path: Path):
    try:
        generate_ledgers(tmp_path, 999, 2026)
    except ValueError as error:
        assert "1,000" in str(error)
    else:
        raise AssertionError("expected ValueError")
