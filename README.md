# CareerCompass AI — Starter Project

This Streamlit prototype is based on the uploaded **AI-Based Career Counselor and Resume Analyzer** hackathon PDF.

## Windows setup (VS Code / PowerShell)
1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Extract this ZIP and open the `ai_career_counselor_starter` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```powershell
   py -3.12 -m venv .venv
   ```
   If that fails, try `python -m venv .venv`.
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
6. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
7. Create your environment file:
   ```powershell
   Copy-Item .env.example .env
   ```
8. Get your own Gemini API key at https://aistudio.google.com/app/apikey. Open `.env` and replace `PASTE_YOUR_API_KEY_HERE`. Keep the key private; never commit `.env` to GitHub.
9. Run:
   ```powershell
   python -m streamlit run app.py
   ```
10. Open the URL printed in the terminal, normally `http://localhost:8501`.

## Troubleshooting
- If `py` is not recognized, try `python -m venv .venv`.
- Use `python -m pip`, not `pip`, if pip is not on PATH.
- Gemini 401/403: check key and API access.
- Model not found/404: check currently available model IDs in Google AI Studio / official Gemini API docs and update `GEMINI_MODEL` in `.env`.
- Port conflict: stop the old server with Ctrl+C, or run `python -m streamlit run app.py --server.port 8502`.
- Blank extracted resume text usually means the PDF is scanned/image-only; OCR is not included.

## Demo flow
Set target role and skills → ask for career guidance → upload a resume with personal details removed and paste a job description → build a learning plan → generate/review a mock interview answer → improve LinkedIn profile.

## Honest limitations
This is a prototype. It does not include custom-trained ML models, live job portal APIs, live salary data feeds, voice recording/TTS, scanned-PDF OCR, a validated personality test, authentication, or a database. Do not claim these are implemented. Verify AI output and job-market details before acting on them.
