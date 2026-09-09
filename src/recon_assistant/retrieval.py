from __future__ import annotations

from dataclasses import dataclass

import psycopg2
from pgvector.psycopg2 import register_vector


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    page_number: int
    section_title: str
    content: str
    score: float


DOMAIN_EXPANSIONS = {
    "CIP": "Customer Identification Program",
    "CTR": "Currency Transaction Report",
    "SAR": "Suspicious Activity Report",
    "BSA": "Bank Secrecy Act",
    "AML": "Anti Money Laundering",
}


def expand_domain_terms(query: str) -> str:
    expanded = query
    tokens = set(query.replace("?", "").replace("/", " ").split())
    for abbreviation, phrase in DOMAIN_EXPANSIONS.items():
        if abbreviation in tokens:
            expanded = f"{expanded} {phrase}"
    return expanded


def search(dsn: str, embedding: list[float], query: str, limit: int = 5) -> list[SearchResult]:
    lexical_query = expand_domain_terms(query)
    with psycopg2.connect(dsn) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """with vector_matches as (
                       select chunk_id, row_number() over (order by embedding <=> %s::vector) vector_rank
                       from recon.document_chunk order by embedding <=> %s::vector limit 25
                   ), text_matches as (
                       select chunk_id, row_number() over (
                           order by ts_rank_cd(content_tsv, websearch_to_tsquery('english', %s)) desc
                       ) text_rank
                       from recon.document_chunk
                       where content_tsv @@ websearch_to_tsquery('english', %s)
                       order by ts_rank_cd(content_tsv, websearch_to_tsquery('english', %s)) desc limit 25
                   ), candidates as (
                       select chunk_id from vector_matches union select chunk_id from text_matches
                   )
                   select d.chunk_id,d.page_number,d.section_title,d.content,
                          1-(d.embedding <=> %s::vector) score
                   from candidates c
                   join recon.document_chunk d using(chunk_id)
                   left join vector_matches v using(chunk_id)
                   left join text_matches t using(chunk_id)
                   order by coalesce(2.0/(60+v.vector_rank),0) + coalesce(1.0/(60+t.text_rank),0) desc
                   limit %s""",
                (embedding, embedding, lexical_query, lexical_query, lexical_query, embedding, limit),
            )
            return [SearchResult(*row) for row in cursor.fetchall()]


def grounded_response(question: str, results: list[SearchResult], minimum_score: float) -> dict:
    accepted = [item for item in results if item.score >= minimum_score]
    if not accepted:
        return {"question": question, "answer": "The indexed manual does not provide enough evidence to answer this question.", "citations": [], "grounded": False}
    citations = [{"page": item.page_number, "chunk_id": item.chunk_id, "score": round(item.score, 4), "section": item.section_title} for item in accepted]
    answer = " ".join(item.content[:360].strip() for item in accepted[:2])
    return {"question": question, "answer": answer, "citations": citations, "grounded": True}
