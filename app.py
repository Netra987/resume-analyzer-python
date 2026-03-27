"""Enhanced Resume Analyzer — PDF/DOCX upload, skill gap report, visual dashboard."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from resume_analyzer.io_utils import load_from_bytes
from resume_analyzer.preprocess import preprocess
from resume_analyzer.extract import extract_all, extract_skills
from resume_analyzer.match import match_resume_to_job
from resume_analyzer.suggest import make_report

# ── spaCy (optional — graceful fallback if not installed) ──────────────────────
def _try_load_spacy():
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except Exception:
        return None


@st.cache_resource
def load_spacy_model():
    return _try_load_spacy()


def spacy_normalize(nlp, text: str) -> str:
    if nlp is None:
        return text
    doc = nlp(text)
    return " ".join(
        t.lemma_.lower()
        for t in doc
        if not (t.is_space or t.is_punct or t.is_stop)
    )


# ── Analysis pipeline ──────────────────────────────────────────────────────────
def analyze(resume_bytes: bytes, resume_filename: str, job_text: str, top_k: int = 20):
    skills_path = Path(__file__).parent / "resume_analyzer" / "data" / "skills_lexicon.txt"

    nlp = load_spacy_model()

    resume_doc = load_from_bytes(resume_bytes, resume_filename)

    resume_pp = preprocess(resume_doc.text)
    job_pp = preprocess(job_text)

    resume_norm = spacy_normalize(nlp, resume_pp.cleaned)
    job_norm = spacy_normalize(nlp, job_pp.cleaned)

    extracted = extract_all(
        raw_text=resume_doc.text,
        cleaned_text=resume_pp.cleaned,
        skills_lexicon_path=skills_path,
    )
    job_skills = extract_skills(job_pp.cleaned, skills_lexicon_path=skills_path)

    match = match_resume_to_job(
        resume_text_norm=resume_norm,
        job_text_norm=job_norm,
        top_k=top_k,
    )

    report = make_report(
        match_percent=match.match_percent,
        top_resume_terms=match.top_resume_terms,
        resume_skills=extracted.skills,
        job_skills=job_skills,
        education=extracted.education,
        experience_keywords=extracted.experience_keywords,
    )

    return report, extracted, match, job_skills


# ── Score colour helper ────────────────────────────────────────────────────────
def score_color(pct: float) -> str:
    if pct >= 70:
        return "#2ecc71"   # green
    elif pct >= 45:
        return "#f39c12"   # orange
    return "#e74c3c"       # red


def score_label(pct: float) -> str:
    if pct >= 70:
        return "Strong Match 🟢"
    elif pct >= 45:
        return "Moderate Match 🟡"
    return "Low Match 🔴"


# ── Main app ───────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Resume Analyzer",
        page_icon="📄",
        layout="wide",
    )

    # Custom CSS for a cleaner look
    st.markdown("""
        <style>
        .metric-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border-left: 5px solid #1F4E79;
        }
        .skill-tag {
            display: inline-block;
            background: #d4edda;
            color: #155724;
            border-radius: 12px;
            padding: 3px 10px;
            margin: 3px;
            font-size: 13px;
        }
        .skill-missing {
            background: #f8d7da;
            color: #721c24;
        }
        .skill-bonus {
            background: #d1ecf1;
            color: #0c5460;
        }
        .section-header {
            font-size: 17px;
            font-weight: 700;
            color: #1F4E79;
            margin-top: 8px;
            margin-bottom: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📄 Resume Analyzer")
    st.caption("Upload your resume and a job description — get an instant match score, skill gap report, and improvement tips.")

    st.markdown("---")

    # ── Input columns ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📁 Upload Resume")
        uploaded_resume = st.file_uploader(
            "Supported formats: PDF, DOCX, TXT",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )
        if uploaded_resume:
            st.success(f"✅ Loaded: **{uploaded_resume.name}**")

    with col_right:
        st.markdown("### 📋 Job Description")
        job_mode = st.radio(
            "Input method",
            ["Paste text", "Upload .txt file"],
            horizontal=True,
            label_visibility="collapsed",
        )
        job_text: str | None = None
        if job_mode == "Paste text":
            job_text = st.text_area(
                "Paste job description",
                height=160,
                placeholder="Paste the full job description here…",
                label_visibility="collapsed",
            )
        else:
            jf = st.file_uploader("Upload job description (.txt)", type=["txt"], key="job_file")
            if jf:
                job_text = jf.read().decode("utf-8", errors="ignore")
                st.success(f"✅ Loaded: **{jf.name}**")

    # Options row
    with st.expander("⚙️ Options", expanded=False):
        top_k = st.slider("Top TF-IDF keywords to display", 5, 40, 20, 1)

    st.markdown("---")
    run_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

    # ── Results ────────────────────────────────────────────────────────────────
    if run_btn:
        if uploaded_resume is None:
            st.error("⚠️ Please upload a resume file.")
            return
        if not job_text or not job_text.strip():
            st.error("⚠️ Please provide a job description.")
            return

        with st.spinner("Running NLP pipeline…"):
            report, extracted, match, job_skills = analyze(
                resume_bytes=uploaded_resume.getvalue(),
                resume_filename=uploaded_resume.name,
                job_text=job_text,
                top_k=top_k,
            )

        # ── Score banner ───────────────────────────────────────────────────────
        color = score_color(report.match_percent)
        label = score_label(report.match_percent)
        st.markdown(f"""
            <div style="background:{color}22; border:2px solid {color};
                        border-radius:12px; padding:18px 24px; margin:16px 0; text-align:center;">
                <span style="font-size:36px; font-weight:800; color:{color};">
                    {report.match_percent:.1f}%
                </span>
                <span style="font-size:20px; color:{color}; margin-left:12px;">
                    {label}
                </span>
            </div>
        """, unsafe_allow_html=True)

        # ── Three-column overview ──────────────────────────────────────────────
        oc1, oc2, oc3 = st.columns(3)
        oc1.metric("Overall Match", f"{report.match_percent:.1f}%")
        oc2.metric("Skill Coverage", f"{report.skill_coverage_percent:.1f}%",
                   help="% of job-required skills found in your resume")
        oc3.metric("Skills Matched", f"{len(report.matched_skills)} / {len(report.matched_skills) + len(report.missing_skills)}")

        st.markdown("---")

        # ── Skill Gap Report (main feature) ───────────────────────────────────
        st.markdown("## 🔍 Skill Gap Report")

        sg1, sg2, sg3 = st.columns(3)

        with sg1:
            st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
            if report.matched_skills:
                tags = "".join(f'<span class="skill-tag">{s}</span>' for s in report.matched_skills)
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("None detected from lexicon.")

        with sg2:
            st.markdown('<div class="section-header">❌ Missing Skills</div>', unsafe_allow_html=True)
            if report.missing_skills:
                tags = "".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in report.missing_skills)
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("No required skills missing — great coverage!")

        with sg3:
            st.markdown('<div class="section-header">💡 Bonus Skills</div>', unsafe_allow_html=True)
            if report.bonus_skills:
                tags = "".join(f'<span class="skill-tag skill-bonus">{s}</span>' for s in report.bonus_skills[:12])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("No extra skills beyond job requirements.")

        # ── Skill coverage bar ─────────────────────────────────────────────────
        if report.matched_skills or report.missing_skills:
            st.markdown("#### Skill Coverage")
            total = len(report.matched_skills) + len(report.missing_skills)
            st.progress(int(report.skill_coverage_percent), text=f"{report.skill_coverage_percent:.0f}% of required skills covered")

        st.markdown("---")

        # ── Strengths & Suggestions ────────────────────────────────────────────
        sc1, sc2 = st.columns(2)

        with sc1:
            st.markdown("## 💪 Strengths")
            if report.strengths:
                for s in report.strengths:
                    st.markdown(f"- {s}")
            else:
                st.caption("No specific strengths detected.")

        with sc2:
            st.markdown("## 🛠️ Improvement Suggestions")
            for s in report.improvement_suggestions:
                st.markdown(f"- {s}")

        st.markdown("---")

        # ── Extracted info ─────────────────────────────────────────────────────
        with st.expander("📋 Extracted Resume Info"):
            ei1, ei2 = st.columns(2)
            with ei1:
                st.write("**Education**")
                if extracted.education:
                    for e in extracted.education:
                        st.markdown(f"- {e}")
                else:
                    st.caption("No clear education lines found.")
                st.write("**Action Verbs Detected**")
                if extracted.experience_keywords:
                    st.write(", ".join(extracted.experience_keywords))
                else:
                    st.caption("None detected.")
            with ei2:
                if extracted.name:
                    st.write(f"**Name:** {extracted.name}")
                if extracted.email:
                    st.write(f"**Email:** {extracted.email}")
                if extracted.phone:
                    st.write(f"**Phone:** {extracted.phone}")

        # ── TF-IDF keyword tables ──────────────────────────────────────────────
        with st.expander("📊 TF-IDF Keyword Analysis"):
            kc1, kc2 = st.columns(2)
            with kc1:
                st.write("**Top Resume Keywords**")
                if match.top_resume_terms:
                    st.dataframe(
                        {"Term": [t for t, _ in match.top_resume_terms],
                         "Score": [round(s, 4) for _, s in match.top_resume_terms]},
                        hide_index=True, use_container_width=True,
                    )
            with kc2:
                st.write("**Top Job Description Keywords**")
                if match.top_job_terms:
                    st.dataframe(
                        {"Term": [t for t, _ in match.top_job_terms],
                         "Score": [round(s, 4) for _, s in match.top_job_terms]},
                        hide_index=True, use_container_width=True,
                    )
            if match.common_terms:
                st.write("**Common Top Keywords**")
                st.write(", ".join(match.common_terms))


if __name__ == "__main__":
    main()
