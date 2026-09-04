# AI Study Companion

A beginner-friendly Full Stack Python project using Flask, SQLite, HTML, CSS and JavaScript.

## Features
- Register / Login / Logout
- Dashboard
- AI Summary
- AI MCQ Generator
- Quiz with score
- AI Translate
- Read Aloud
- AI Explain Any Topic
- Study Timer
- Achievements

## Run

1. Create a virtual environment:
   python -m venv venv

2. Activate it on Windows:
   venv\Scripts\activate

3. Install packages:
   pip install -r requirements.txt

4. Optional AI setup:
   Copy `.env.example` to `.env` and set OPENAI_API_KEY.
   If no API key is configured, Summary/Explain/Translate/MCQ use beginner-friendly fallback logic.

5. Start:
   python app.py

6. Open:
   http://127.0.0.1:5000

## Important
For a real deployment, use a strong SECRET_KEY and store passwords securely with hashing.
