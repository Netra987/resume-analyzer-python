"""TF-IDF + cosine similarity matching between resume and job description."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MatchResult:
    match_percent: float
    top_resume_terms: list[tuple[str, float]] = field(default_factory=list)
    top_job_terms: list[tuple[str, float]] = field(default_factory=list)
    common_terms: list[str] = field(default_factory=list)


def match_resume_to_job(
    resume_text_norm: str,
    job_text_norm: str,
    top_k: int = 20,
) -> MatchResult:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    corpus = [resume_text_norm, job_text_norm]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_features=5000,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    match_percent = float(round(similarity * 100, 2))

    resume_vec = np.asarray(tfidf_matrix[0].todense()).flatten()
    job_vec = np.asarray(tfidf_matrix[1].todense()).flatten()

    def top_terms(vec, k):
        indices = vec.argsort()[::-1][:k]
        return [(feature_names[i], float(round(vec[i], 4))) for i in indices if vec[i] > 0]

    top_resume = top_terms(resume_vec, top_k)
    top_job = top_terms(job_vec, top_k)

    # Terms that appear in both top lists
    resume_term_set = {t for t, _ in top_resume}
    job_term_set = {t for t, _ in top_job}
    common = sorted(resume_term_set & job_term_set)

    return MatchResult(
        match_percent=match_percent,
        top_resume_terms=top_resume,
        top_job_terms=top_job,
        common_terms=common,
    )
