#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/.local/postgres"
LOG="$ROOT/.local/postgres.log"
BIN="/opt/homebrew/opt/postgresql@14/bin"
mkdir -p "$ROOT/.local"
if [[ ! -f "$DATA/PG_VERSION" ]]; then
  "$BIN/initdb" -D "$DATA" --auth=trust --username=reconciliation >/dev/null
  printf "port=55433\nlisten_addresses='127.0.0.1'\nunix_socket_directories='/tmp'\n" >> "$DATA/postgresql.conf"
fi
if ! "$BIN/pg_isready" -h 127.0.0.1 -p 55433 >/dev/null 2>&1; then
  "$BIN/pg_ctl" -D "$DATA" -l "$LOG" start >/dev/null
fi
until "$BIN/pg_isready" -h 127.0.0.1 -p 55433 >/dev/null 2>&1; do sleep 0.2; done
"$BIN/createdb" -h 127.0.0.1 -p 55433 -U reconciliation reconciliation 2>/dev/null || true
echo "PostgreSQL with pgvector ready on 127.0.0.1:55433"
