"""Skill gap analysis and improvement suggestion engine."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillGapReport:
    match_percent: float
    matched_skills: list[str]
    missing_skills: list[str]
    bonus_skills: list[str]          # skills in resume not in job (good extras)
    strengths: list[str]
    improvement_suggestions: list[str]
    skill_coverage_percent: float    # what % of required skills are covered


def make_report(
    match_percent: float,
    top_resume_terms: list[tuple[str, float]],
    resume_skills: list[str],
    job_skills: list[str],
    education: list[str],
    experience_keywords: list[str],
) -> SkillGapReport:
    resume_skill_set = set(s.lower() for s in resume_skills)
    job_skill_set = set(s.lower() for s in job_skills)

    matched_skills = sorted(resume_skill_set & job_skill_set)
    missing_skills = sorted(job_skill_set - resume_skill_set)
    bonus_skills = sorted(resume_skill_set - job_skill_set)

    skill_coverage = (
        round(len(matched_skills) / len(job_skill_set) * 100, 1)
        if job_skill_set else 0.0
    )

    strengths = _build_strengths(
        match_percent=match_percent,
        matched_skills=matched_skills,
        experience_keywords=experience_keywords,
        education=education,
        bonus_skills=bonus_skills,
    )

    suggestions = _build_suggestions(
        match_percent=match_percent,
        missing_skills=missing_skills,
        experience_keywords=experience_keywords,
        education=education,
        skill_coverage=skill_coverage,
    )

    return SkillGapReport(
        match_percent=match_percent,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        bonus_skills=bonus_skills,
        strengths=strengths,
        improvement_suggestions=suggestions,
        skill_coverage_percent=skill_coverage,
    )


def _build_strengths(
    match_percent: float,
    matched_skills: list[str],
    experience_keywords: list[str],
    education: list[str],
    bonus_skills: list[str],
) -> list[str]:
    strengths = []

    if match_percent >= 70:
        strengths.append(f"Strong overall match ({match_percent:.1f}%) with the job description.")
    elif match_percent >= 45:
        strengths.append(f"Moderate match ({match_percent:.1f}%) — good foundation to build on.")

    if matched_skills:
        preview = ", ".join(matched_skills[:5])
        more = f" (+{len(matched_skills)-5} more)" if len(matched_skills) > 5 else ""
        strengths.append(f"Covers {len(matched_skills)} required skill(s): {preview}{more}.")

    if len(experience_keywords) >= 5:
        strengths.append("Resume uses strong action verbs (e.g. built, developed, implemented).")

    if education:
        strengths.append("Education section is present and detectable.")

    if bonus_skills:
        preview = ", ".join(bonus_skills[:4])
        strengths.append(f"Additional skills beyond job requirements: {preview}.")

    return strengths


def _build_suggestions(
    match_percent: float,
    missing_skills: list[str],
    experience_keywords: list[str],
    education: list[str],
    skill_coverage: float,
) -> list[str]:
    suggestions = []

    if match_percent < 45:
        suggestions.append(
            "Overall match is low — tailor your resume language to closely mirror the job description."
        )

    if missing_skills:
        preview = ", ".join(missing_skills[:6])
        more = f" (+{len(missing_skills)-6} more)" if len(missing_skills) > 6 else ""
        suggestions.append(
            f"Add or highlight {len(missing_skills)} missing skill(s) if you have them: {preview}{more}."
        )

    if skill_coverage < 50 and missing_skills:
        suggestions.append(
            "Less than half the required skills were found — consider adding a dedicated Skills section."
        )

    if len(experience_keywords) < 3:
        suggestions.append(
            "Use more action verbs (e.g. developed, built, optimized, deployed) in your bullet points."
        )

    if not education:
        suggestions.append(
            "Education section was not clearly detected — ensure degree names and institutions are visible."
        )

    if match_percent < 70:
        suggestions.append(
            "Use keywords from the job description more naturally in your project and summary sections."
        )

    if not suggestions:
        suggestions.append("Resume looks well-optimized for this role. Minor tailoring may still help.")

    return suggestions
