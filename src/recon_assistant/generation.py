from __future__ import annotations

import re

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .retrieval import SearchResult


ABSTENTION = "The manual does not provide enough evidence to answer this question."


class LocalAnswerGenerator:
    def __init__(self, model_name: str, max_input_tokens: int = 512, max_output_tokens: int = 120):
        self.model_name = model_name
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def answer(
        self, question: str, results: list[SearchResult], minimum_score: float, evidence_gate_score: float
    ) -> dict:
        accepted = [result for result in results if result.score >= minimum_score]
        if not accepted or max(result.score for result in accepted) < evidence_gate_score:
            return self._abstain(question)

        context = "\n".join(
            f"[Page {item.page_number}; {item.chunk_id}] {item.content}" for item in accepted[:2]
        )
        prompt = (
            "Answer the question using only the manual excerpts below. "
            "Do not add facts that are absent from the excerpts. Answer in your own words, avoid long quotations, "
            "and include every item needed to answer the question. Use no more than two sentences. "
            "If the excerpts do not answer the question, output NOT_ENOUGH_EVIDENCE.\n\n"
            f"Question: {question}\n\nManual excerpts:\n{context}\n\nAnswer:"
        )
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=self.max_input_tokens
        )
        output = self.model.generate(
            **inputs,
            max_new_tokens=self.max_output_tokens,
            do_sample=False,
            num_beams=4,
            no_repeat_ngram_size=3,
        )
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True).strip()
        if not answer or "NOT_ENOUGH_EVIDENCE" in answer.upper():
            return self._abstain(question)
        citations = [
            {
                "page": item.page_number,
                "chunk_id": item.chunk_id,
                "score": round(item.score, 4),
                "section": item.section_title,
            }
            for item in accepted[:2]
        ]
        answer = re.sub(r"\[Page\s+\d+;[^\]]+\].*", "", answer).strip()
        if answer and answer[-1] not in ".?!":
            last_stop = max(answer.rfind("."), answer.rfind("?"), answer.rfind("!"))
            if last_stop > 0:
                answer = answer[: last_stop + 1]
        return {
            "question": question,
            "answer": re.sub(r"\s+", " ", answer),
            "citations": citations,
            "grounded": True,
            "model": self.model_name,
            "context": context,
        }

    @staticmethod
    def _abstain(question: str) -> dict:
        return {"question": question, "answer": ABSTENTION, "citations": [], "grounded": False}
