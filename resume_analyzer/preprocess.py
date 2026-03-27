"""Text preprocessing: cleaning, normalization, tokenization."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PreprocessedText:
    original: str
    cleaned: str
    tokens: list[str]


def preprocess(text: str) -> PreprocessedText:
    cleaned = _clean(text)
    tokens = _tokenize(cleaned)
    return PreprocessedText(original=text, cleaned=cleaned, tokens=tokens)


def _clean(text: str) -> str:
    # Normalize whitespace and line breaks
    text = re.sub(r"\r\n|\r", "\n", text)
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    # Remove phone numbers
    text = re.sub(r"[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]", " ", text)
    # Remove special characters except hyphens inside words
    text = re.sub(r"[^\w\s\-]", " ", text)
    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _tokenize(text: str) -> list[str]:
    return [t for t in text.split() if len(t) > 1]
