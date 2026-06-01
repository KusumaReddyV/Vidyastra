# Vidyastra

**Vidyastra** is a full-stack learning and career platform for students and early-career developers. It combines resume intelligence, adaptive quizzes, personalized recommendations, a rule-based mentor, study planning, and analytics — all running **locally without external LLM APIs**.

---

## Overview

Upload a resume, set career goals, and Vidyastra helps you:

- Analyze ATS fit and skill gaps against job descriptions
- Practice with adaptive quizzes (Python, DSA, DBMS, OS, Flask, SQL, and more)
- Get resume-aware recommendations and career roadmaps
- Plan weekly study blocks from weak subjects and available hours
- Chat with a mentor that uses structured knowledge and your profile

---

## Key features

| Area | Description |
|------|-------------|
| **Resume Analyzer** | NLP-based parsing, ATS scoring, keyword gaps, improvement tips |
| **Resume History** | Track versions and progress over time |
| **Dashboard** | Insights, weak subjects, recommendations preview, activity timeline |
| **Adaptive Quizzes** | Local question bank with difficulty adaptation from scores |
| **Learning Paths** | Static roadmaps (frontend, backend, full stack, ML, etc.) |
| **Study Planner** | 7-day template plans from weak topics + study hours |
| **Mentor** | Keyword-matched guidance from `data/mentor_knowledge.json` + resume context |
| **Recommendations** | Skill gaps, learning paths, internships, career roadmap |
| **Analytics** | Quiz performance, focus areas, strongest/weakest skills |

---

## Architecture

```
Browser (HTML/CSS/JS)
        │
        ▼
Flask (blueprints: auth, dashboard, quiz, recommendation, chatbot, resume)
        │
        ├── MongoDB (users, profiles, quizzes, resumes, chat history)
        ├── spaCy + scikit-learn (resume NLP / scoring)
        └── app/services/ (rule-based engines)
                ├── data_loader.py      → /data/*.json
                ├── resume_intelligence.py
                ├── mentor_service.py
                ├── recommendation_service.py
                └── study_planner_service.py
```

No Gemini, OpenAI, or Ollama required.

---

## Tech stack

- **Backend:** Python 3.11+, Flask, Flask-Login
- **Database:** MongoDB
- **NLP:** spaCy, scikit-learn, PyMuPDF
- **Frontend:** Bootstrap 5, vanilla JavaScript, Chart.js
- **Data:** JSON knowledge bases under `/data`

---

## Screenshots

_Add screenshots of landing, dashboard, resume analyzer, quizzes, and mentor here._

---

## Setup

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- pip

### Install

```bash
git clone <your-repo-url>
cd Vidyastra

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Environment

Copy `.env.example` to `.env` and set:

```env
SESSION_SECRET=your-secure-secret
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=vidyastra
```

### Run

```bash
python wsgi.py
```

Open **http://localhost:5000**

### Tests

```bash
pytest
```

---

## Folder structure

```
Vidyastra/
├── app/
│   ├── auth/           # Signup, login, password reset
│   ├── dashboard/      # Main app pages + study plan API
│   ├── quiz/           # Quiz generate/submit API
│   ├── recommendation/ # Learning, roadmap, internships API
│   ├── chatbot/        # Mentor API
│   ├── resume/         # Resume history
│   ├── services/       # Rule-based engines
│   ├── ml_models/      # Thin wrappers (quiz, analytics, weak subjects)
│   ├── static/         # CSS & JS
│   └── templates/      # HTML
├── data/               # Editable JSON knowledge bases
├── tests/
├── wsgi.py
└── requirements.txt
```

---

## Extending data files

All rule-based content lives in `/data`. Edit JSON and restart the app (cached loaders refresh on process restart).

| File | Purpose |
|------|---------|
| `question_bank.json` | Quiz questions by topic and difficulty |
| `mentor_knowledge.json` | Mentor Q&A entries (`keywords`, `question_patterns`, `answer`) |
| `learning_paths.json` | Course phases and certifications per track |
| `career_paths.json` | Role roadmaps (SDE, full stack, backend, data scientist) |
| `skill_gap_rules.json` | Required skills per role + inference rules (e.g. Flask → Docker) |

**Example mentor entry:**

```json
{
  "id": "flask-1",
  "topics": ["flask"],
  "keywords": ["flask", "blueprint"],
  "question_patterns": ["how to use flask"],
  "answer": "Use application factory, blueprints, and config classes..."
}
```

**Example skill gap rule:**

```json
{
  "has_any": ["flask"],
  "lacks_any": ["docker", "aws"],
  "recommend": ["Docker", "AWS"],
  "reason": "Add deployment skills to complement your Flask projects"
}
```

---

## Future scope

- Spaced-repetition quiz scheduling
- Email reminders for study plans
- Team / college admin dashboards
- Exportable PDF career reports
- Optional plug-in LLM provider (not required for core product)

---

## License

See repository license. Built for portfolio and production-style demos.
