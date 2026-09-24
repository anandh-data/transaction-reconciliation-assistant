from pathlib import Path

import pytest
from psycopg2.extensions import parse_dsn

from recon_assistant.config import load_settings


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("field,value", [
    ("password", "two words"),
    ("password", "quote'and\\slash"),
    ("password", "value host=other"),
    ("password", ""),
    ("dbname", "test database"),
    ("user", "test'user"),
])
def test_database_settings_preserve_special_characters(monkeypatch, field, value):
    values = {
        "host": "localhost",
        "port": "55433",
        "dbname": "test_database",
        "user": "test_user",
        "password": "dummy_password",
    }
    values[field] = value
    for key, value in values.items():
        env_key = "DB" if key == "dbname" else key.upper()
        monkeypatch.setenv(f"POSTGRES_{env_key}", value)

    settings = load_settings(ROOT)

    assert parse_dsn(settings.dsn) == values


def test_database_settings_keep_existing_defaults(monkeypatch):
    for key in ("HOST", "PORT", "DB", "USER", "PASSWORD"):
        monkeypatch.delenv(f"POSTGRES_{key}", raising=False)

    assert parse_dsn(load_settings(ROOT).dsn) == {
        "host": "127.0.0.1",
        "port": "55433",
        "dbname": "reconciliation",
        "user": "reconciliation",
        "password": "change_me",
    }
