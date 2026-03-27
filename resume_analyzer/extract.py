"""Extraction: skills, education, experience keywords using spaCy + lexicon."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedInfo:
    skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience_keywords: list[str] = field(default_factory=list)
    name: str = ""
    email: str = ""
    phone: str = ""


# Degree keywords for education detection
_DEGREE_PATTERNS = re.compile(
    r"(b\.?tech|m\.?tech|b\.?e|m\.?e|b\.?sc|m\.?sc|b\.?com|mba|phd|ph\.d"
    r"|bachelor|master|doctorate|diploma|hsc|ssc|12th|10th|cgpa|gpa|percentage)",
    re.IGNORECASE,
)

_EXPERIENCE_KEYWORDS = [
    "developed", "built", "designed", "implemented", "created", "led",
    "managed", "analyzed", "optimized", "deployed", "automated", "collaborated",
    "researched", "maintained", "integrated", "architected", "delivered",
    "improved", "reduced", "increased", "achieved",
]


def load_skills_lexicon(path: Path) -> set[str]:
    if not path.exists():
        return set()
    skills = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            skills.add(line)
    return skills


def extract_skills(text: str, skills_lexicon_path: Path) -> list[str]:
    lexicon = load_skills_lexicon(skills_lexicon_path)
    if not lexicon:
        return []
    text_lower = text.lower()
    found = []
    # Sort by length desc so multi-word skills match before substrings
    for skill in sorted(lexicon, key=len, reverse=True):
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(text: str) -> list[str]:
    lines = text.splitlines()
    edu_lines = []
    for line in lines:
        if _DEGREE_PATTERNS.search(line):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 5:
                edu_lines.append(cleaned)
    return edu_lines[:6]  # cap at 6 lines


def extract_experience_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in _EXPERIENCE_KEYWORDS if kw in text_lower]


def extract_contact(raw_text: str) -> tuple[str, str, str]:
    email_match = re.search(r"[\w.\-]+@[\w.\-]+\.\w+", raw_text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]", raw_text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # Very naive name extraction: first non-empty line that looks like a name
    name = ""
    for line in raw_text.splitlines():
        line = line.strip()
        if line and re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+){0,3}$", line):
            name = line
            break

    return name, email, phone


def extract_all(raw_text: str, cleaned_text: str, skills_lexicon_path: Path) -> ExtractedInfo:
    skills = extract_skills(cleaned_text, skills_lexicon_path)
    education = extract_education(raw_text)
    experience_keywords = extract_experience_keywords(cleaned_text)
    name, email, phone = extract_contact(raw_text)
    return ExtractedInfo(
        skills=skills,
        education=education,
        experience_keywords=experience_keywords,
        name=name,
        email=email,
        phone=phone,
    )
