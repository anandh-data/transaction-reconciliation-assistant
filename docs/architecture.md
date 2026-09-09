# Architecture and design decisions

The system has two deliberately separate paths. The reconciliation path uses a full outer join and configured amount/date tolerances; it does not depend on probabilistic output. The retrieval path ingests the manual by physical PDF page, creates overlapping passages, embeds each passage locally, and stores the vectors alongside searchable text.

Search combines the top 25 cosine-similarity matches with the top 25 PostgreSQL full-text matches. Reciprocal-rank fusion weights semantic rank two-to-one over lexical rank. A small domain dictionary expands CIP, CTR, SAR, BSA, and AML before lexical search. Results preserve document, physical page, chunk, checksum, and similarity score.

PostgreSQL with pgvector was selected instead of a separate vector database because transactions, exceptions, passages, evaluations, and audit events can share one governed datastore and one backup/access-control model.

The response composer is extractive. It returns the strongest retrieved passages rather than calling an external generative model. That makes every statement traceable, avoids API credentials and cost, and prevents an LLM from changing a reconciliation result.
