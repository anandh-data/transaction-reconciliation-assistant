# Testing and measured results

The retrieval benchmark contains ten manually labeled questions covering CIP, funds transfers, suspicious activity, CTRs, independent testing, structuring, monetary instruments, and record retention. Labels reference physical PDF pages. Hit@5 is successful when any expected page appears in the first five results; reciprocal rank rewards earlier relevant results.

The verified run achieved 10/10 Hit@5 and 0.85 mean reciprocal rank over 1,128 passages. Reconciliation returned all 275 injected exceptions in their expected classes and 24,750 matches. The committed CSV contains every exception for inspection.

Unit tests cover deterministic generation, exception counts, acronym expansion, refusal behavior, and evaluation calculations. The CI workflow runs those tests on each push and pull request.
