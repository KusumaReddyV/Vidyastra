# Vidyastra Incremental Extension

This project extends the existing Resume Analyzer without removing any existing route:

- Existing analyzer route remains at `/`
- Existing analyzer APIs remain unchanged (`/analyze`, `/api/analyze-text`, `/sample-jd`)
- New Vidyastra landing page added at `/vidyastra`

## Added Folder Structure

```
app/
  auth/
  dashboard/
  resume/
  quiz/
  recommendation/
  chatbot/
  ml_models/
  datasets/
  static/
    css/vidyastra/
    js/vidyastra/
  templates/
    auth/
    vidyastra/
```

## MongoDB Collections

Collections initialized via `app/db.py`:

1. users
2. student_profiles
3. resumes
4. quiz_results
5. weak_subjects
6. study_plans
7. recommendations
8. learning_progress
9. chatbot_history
10. internships
11. career_roadmaps

## Implemented Modules

- Flask-Login auth flow: signup/login/logout
- Student profile CRUD form
- Weak subject detection logic
- Adaptive quiz generator/submission APIs
- Recommendation APIs (learning, internships, roadmap)
- AI mentor chatbot endpoint
- Enhanced resume analysis API (ATS + gaps + suggestions)
- Dashboard with Chart.js and chatbot widget

## Step-by-Step Run

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start MongoDB service on `mongodb://localhost:27017`
3. Optional env vars:
   - `MONGO_URI`
   - `MONGO_DB_NAME`
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
4. Run app:
   - `flask --app wsgi run`
5. Visit:
   - Resume Analyzer: `/`
   - Vidyastra Landing: `/vidyastra`
   - Auth: `/auth/signup`
   - Dashboard: `/vidyastra/dashboard`
