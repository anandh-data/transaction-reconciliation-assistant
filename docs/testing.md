# Testing and measured results

The retrieval benchmark contains ten manually labeled questions covering CIP, funds transfers, suspicious activity, CTRs, independent testing, structuring, monetary instruments, and record retention. Labels reference physical PDF pages. Hit@5 is successful when any expected page appears in the first five results; reciprocal rank rewards earlier relevant results across all returned passages. The Hit@5 cutoff remains five even when retrieval is configured to return more passages.

The verified retrieval run achieved 10/10 Hit@5 and 0.85 mean reciprocal rank over 1,128 passages. Across the same ten supported questions, generated answers achieved 100% expected-page citation accuracy, contained all manually specified key facts, and recorded 0.74 mean embedding similarity to their retrieved context. The evidence gate correctly refused all five unrelated questions. These are small, transparent portfolio test sets—not claims about general model performance.

Reconciliation returned all 275 injected exceptions in their expected classes and 24,750 matches. The committed CSV contains every exception for inspection.

Unit tests cover deterministic generation, exception counts, acronym expansion, refusal behavior, and evaluation calculations. The CI workflow runs those tests on each push and pull request.

Evaluation requires at least one labeled question. An empty case list raises `ValueError` before retrieval or report writing; an existing report is left unchanged.
