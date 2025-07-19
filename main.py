prompt = r"""
You are a senior full-stack engineer.  
Build a Python FastAPI + ReactJS project that delivers daily Hacker News headlines via email.  
The project should be scaffolded at the following path:

/home/projects/news

----------------------
Project Overview
----------------------

Backend (Python + FastAPI)
--------------------------
- Language: Python 3.10+
- Framework: FastAPI
- Responsibilities:
  - Accept user email registrations (via POST endpoint)
  - Store registered emails in a local SQLite database
  - Every morning at 8:00 AM, fetch the top 10 stories from Hacker News API
  - Send those headlines via email (use smtplib or a mail library like email or yagmail)
  - Provide a /health route for uptime monitoring

Frontend (React.js)
-------------------
- Language: JavaScript (or TypeScript)
- Framework: ReactJS (Vite or CRA)
- Responsibilities:
  - Show a form to register with an email
  - POST the email to the backend's registration endpoint
  - Display confirmation of successful subscription
  - Host frontend under a separate folder (e.g., frontend/ inside the project root)

--------------------------
Directory Structure
--------------------------

/home/projects/news
├── backend
│   ├── main.py               # FastAPI app
│   ├── scheduler.py          # Daily task runner
│   ├── email_utils.py        # Email sending functions
│   ├── hn_fetcher.py         # Hacker News fetching logic
│   └── db.sqlite             # Email storage
├── frontend
│   ├── ...                   # React app
└── README.md

-------------------------------
Additional Requirements
-------------------------------
- Use APScheduler or schedule for timed jobs
- Use uvicorn to serve the backend
- Use CORS middleware for frontend-backend integration
- Backend should listen on port 8000
- Frontend should run on port 3000

---------------------
Deliverables
---------------------
- A runnable project in /home/projects/news
- Both servers (backend + frontend) should work out of the box
- Example email output format:
  
  Subject: Top Hacker News Headlines for Today

  1. Title 1 - URL
  2. Title 2 - URL
  ...
"""
