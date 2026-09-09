# Data dictionary

## Ledger fields

| Field | Meaning |
|---|---|
| `transaction_id` | Stable cross-ledger transaction key |
| `ledger_name` | `source` or `settlement` |
| `account_id` | Synthetic account identifier |
| `transaction_date` | Posting date |
| `amount` | USD transaction amount, precision 18,2 in PostgreSQL |
| `transaction_type` | ACH, wire, card, or check |

## Exception rules

`missing_source` and `missing_settlement` indicate a one-sided key. `amount_mismatch` means the absolute difference exceeds $0.01. `date_mismatch` means posting dates differ by more than one day. Amount checks take precedence over date checks when both fields differ.

The generated benchmark contains 125 missing settlements, 75 amount mismatches, 50 date mismatches, and 25 settlement-only transactions. A fixed seed makes the expected result reproducible.

## Document records

Every passage includes the document ID, physical PDF page, within-page index, extracted section title, content hash, text, and 384-dimensional embedding. Physical PDF pages are used so a reviewer can reproduce citations directly.
