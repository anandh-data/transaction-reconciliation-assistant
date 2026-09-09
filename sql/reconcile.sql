truncate table recon.reconciliation_result;
insert into recon.reconciliation_result(
  transaction_id,status,source_amount,settlement_amount,amount_difference,date_difference_days,reason
)
select
  coalesce(s.transaction_id,t.transaction_id),
  case
    when s.transaction_id is null then 'missing_source'
    when t.transaction_id is null then 'missing_settlement'
    when abs(s.amount-t.amount) > %(amount_tolerance)s then 'amount_mismatch'
    when abs(s.transaction_date-t.transaction_date) > %(date_tolerance_days)s then 'date_mismatch'
    else 'matched'
  end,
  s.amount,t.amount,
  case when s.amount is null or t.amount is null then null else t.amount-s.amount end,
  case when s.transaction_date is null or t.transaction_date is null then null else t.transaction_date-s.transaction_date end,
  case
    when s.transaction_id is null then 'transaction absent from source ledger'
    when t.transaction_id is null then 'transaction absent from settlement ledger'
    when abs(s.amount-t.amount) > %(amount_tolerance)s then 'amount exceeds configured tolerance'
    when abs(s.transaction_date-t.transaction_date) > %(date_tolerance_days)s then 'posting date exceeds configured tolerance'
    else null
  end
from (select * from recon.ledger_transaction where ledger_name='source') s
full outer join (select * from recon.ledger_transaction where ledger_name='settlement') t using(transaction_id);
