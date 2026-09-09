from recon_assistant.retrieval import SearchResult, expand_domain_terms, grounded_response


def test_domain_abbreviations_are_expanded():
    assert "Customer Identification Program" in expand_domain_terms("Review CIP testing")
    assert "Currency Transaction Report" in expand_domain_terms("When is a CTR filed?")


def test_response_refuses_without_sufficient_evidence():
    weak = [SearchResult("c1", 10, "Section", "Unrelated text", 0.1)]
    response = grounded_response("question", weak, 0.25)
    assert response["grounded"] is False
    assert response["citations"] == []


def test_response_preserves_page_and_chunk_citations():
    result = SearchResult("c1", 61, "CIP", "Select a risk-based sample.", 0.8)
    response = grounded_response("question", [result], 0.25)
    assert response["grounded"] is True
    assert response["citations"][0]["page"] == 61
    assert response["citations"][0]["chunk_id"] == "c1"
