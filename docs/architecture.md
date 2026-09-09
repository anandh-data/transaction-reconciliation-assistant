# Architecture and design decisions

The system has two deliberately separate paths. The reconciliation path uses a full outer join and configured amount/date tolerances; it does not depend on probabilistic output. The retrieval path ingests the manual by physical PDF page, creates overlapping passages, embeds each passage locally, and stores the vectors alongside searchable text.

Search combines the top 25 cosine-similarity matches with the top 25 PostgreSQL full-text matches. Reciprocal-rank fusion weights semantic rank two-to-one over lexical rank. A small domain dictionary expands CIP, CTR, SAR, BSA, and AML before lexical search. Results preserve document, physical page, chunk, checksum, and similarity score.

PostgreSQL with pgvector was selected instead of a separate vector database because transactions, exceptions, passages, evaluations, and audit events can share one governed datastore and one backup/access-control model.

FLAN-T5-base generates a short answer from the three strongest passages. The model runs locally, so the workflow requires no API key. Citations come from stored retrieval metadata rather than model output. A separate evidence threshold blocks generation when retrieval is weak; the LLM never changes the deterministic reconciliation result.
