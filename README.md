# 📄 Resume Analyzer

NLP-powered resume vs job description matcher with skill gap analysis.

## Features

- **PDF, DOCX, TXT** resume upload support
- **TF-IDF + cosine similarity** match scoring
- **Skill gap report** — matched, missing, and bonus skills with visual tags
- **Improvement suggestions** based on gap analysis
- **Streamlit web UI** — runs locally in your browser

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/Netra987/resume-analyzer-python.git
cd resume-analyzer-python

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy model (optional but recommended)
python -m spacy download en_core_web_sm

# 4. Run the app
streamlit run app.py
```

## Project Structure

```
resume-analyzer-python/
├── app.py                          # Streamlit UI
├── requirements.txt
├── resume_analyzer/
│   ├── __init__.py
│   ├── io_utils.py                 # PDF / DOCX / TXT loading
│   ├── preprocess.py               # Text cleaning & normalization
│   ├── extract.py                  # Skill, education, entity extraction
│   ├── match.py                    # TF-IDF cosine similarity scoring
│   ├── suggest.py                  # Skill gap report & suggestions
│   └── data/
│       └── skills_lexicon.txt      # Extensible skills list
```

## Extending the Skills Lexicon

Add any skill (one per line) to `resume_analyzer/data/skills_lexicon.txt` to improve detection accuracy.
