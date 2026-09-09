create extension if not exists vector;
create schema if not exists recon;

create table if not exists recon.document (
  document_id text primary key,
  title text not null,
  source_url text not null,
  source_sha256 text not null,
  page_count integer not null,
  ingested_at timestamptz not null default now()
);

create table if not exists recon.document_chunk (
  chunk_id text primary key,
  document_id text not null references recon.document(document_id),
  page_number integer not null,
  chunk_index integer not null,
  section_title text,
  content text not null,
  content_tsv tsvector generated always as (to_tsvector('english', content)) stored,
  content_sha256 text not null,
  embedding vector(384) not null,
  unique(document_id, page_number, chunk_index)
);
alter table recon.document_chunk add column if not exists content_tsv tsvector
  generated always as (to_tsvector('english', content)) stored;
create index if not exists document_chunk_embedding_hnsw on recon.document_chunk using hnsw (embedding vector_cosine_ops);
create index if not exists document_chunk_content_gin on recon.document_chunk using gin (content_tsv);

create table if not exists recon.ledger_transaction (
  transaction_id text not null,
  ledger_name text not null check (ledger_name in ('source','settlement')),
  account_id text not null,
  transaction_date date not null,
  amount numeric(18,2) not null,
  currency char(3) not null,
  transaction_type text not null,
  primary key(transaction_id, ledger_name)
);

create table if not exists recon.reconciliation_result (
  transaction_id text primary key,
  status text not null,
  source_amount numeric(18,2),
  settlement_amount numeric(18,2),
  amount_difference numeric(18,2),
  date_difference_days integer,
  reason text,
  reconciled_at timestamptz not null default now()
);

create table if not exists recon.retrieval_evaluation (
  evaluation_id bigserial primary key,
  question_id text not null,
  question text not null,
  expected_pages integer[] not null,
  retrieved_pages integer[] not null,
  hit_at_5 boolean not null,
  reciprocal_rank numeric(10,6) not null,
  evaluated_at timestamptz not null default now()
);

create table if not exists recon.audit_event (
  event_id bigserial primary key,
  run_id uuid not null,
  event_type text not null,
  details jsonb not null,
  recorded_at timestamptz not null default now()
);
