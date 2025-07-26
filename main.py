from app.src.orchestration.code_generation import orchestrated_codegen
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

prompt = """
# FastAPI + React: Morning News Email Newsletter

Build a full-stack web app using **FastAPI** (backend) and **React.js** (frontend) for a **morning news email newsletter**. Users register their email on the frontend and receive daily news emails each morning. The whole project goes inside d:/projects/news

## Tech Stack

- **Frontend**: React.js + TailwindCSS
- **Backend**: FastAPI
- **Database**: SQLite or PostgreSQL
- **Email Service**: SMTP or SendGrid
- **News Source**: NewsAPI.org or mocked data

## Features

### Frontend

- Simple responsive page with a call to action
- Email subscription form (`email` field + submit)
- Inline email validation
- Displays success or error messages

### Backend

- `POST /subscribe`: stores validated email, prevents duplicates
- `GET /subscribers`: lists all emails (admin/debug only)
- Daily task (cron/job):
  - Fetch top headlines from NewsAPI
  - Format and send email to all subscribers

### Email

- Styled HTML email with 3–5 headlines (title + link)
- Daily delivery at 07:00 (can be triggered manually)
- Handles invalid or failed emails gracefully

## Suggested Structure

morning_news/
├── backend/
│ ├── main.py, models.py, scheduler.py, etc.
├── frontend/
│ ├── src/App.jsx, components/, index.js
└── README.md


## Deployment

- Use CORS in FastAPI to support frontend calls
- Store secrets in `.env`
- Dev: Frontend (3000), Backend (8000)
- Hosting: Vercel (frontend), Render or Fly.io (backend)

## Optional Extras

- CAPTCHA/honeypot
- Double opt-in confirmation
- Category preferences
- Admin dashboard with stats
"""

# Get required parameters from environment
llm_api_key = os.getenv("CEREBRAS_API_KEY")
model_name = "qwen-3-235b-a22b"

if not llm_api_key:
    raise ValueError("CEREBRAS_API_KEY environment variable is required")

orchestrated_codegen(prompt, llm_api_key, model_name)