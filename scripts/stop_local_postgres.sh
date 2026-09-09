#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/.local/postgres"
if [[ -f "$DATA/PG_VERSION" ]]; then
  /opt/homebrew/opt/postgresql@14/bin/pg_ctl -D "$DATA" stop -m fast
fi
