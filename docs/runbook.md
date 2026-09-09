# Operations runbook

1. Download and checksum the manual with `make download`.
2. Start PostgreSQL/pgvector with `docker compose up -d`.
3. Run `make pipeline`; review `evidence/pipeline-summary.json` for a passed status.
4. Review `evidence/reconciliation-exceptions.csv` and retrieval misses before publishing metrics.
5. Run `make test` after code or configuration changes.

If ingestion fails, confirm the PDF checksum and page count. If the embedding dimension changes, update the schema and rebuild the chunk table. If retrieval quality drops, examine each labeled question rather than changing labels solely to improve a score. Never place real customer or account data in this repository.
