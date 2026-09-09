from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    page_number: int
    chunk_index: int
    section_title: str
    content: str
    content_sha256: str


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"(?<=\w)-\n(?=\w)", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def section_title(text: str) -> str:
    candidates = [part.strip() for part in re.split(r"[.!?]", text[:350]) if part.strip()]
    return (candidates[0] if candidates else "Untitled section")[:180]


def extract_chunks(path: Path, chunk_size: int, overlap: int) -> tuple[int, list[Chunk]]:
    reader = fitz.open(path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, separators=["\n\n", ". ", " "])
    chunks: list[Chunk] = []
    for page_number, page in enumerate(reader, start=1):
        text = clean_text(page.get_text("text") or "")
        if not text:
            continue
        for index, content in enumerate(splitter.split_text(text)):
            digest = hashlib.sha256(content.encode()).hexdigest()
            chunks.append(Chunk(f"p{page_number:04d}-c{index:03d}-{digest[:10]}", page_number, index, section_title(content), content, digest))
    return len(reader), chunks
