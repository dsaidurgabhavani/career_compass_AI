import os, io
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from google import genai

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="CareerCompass AI", page_icon="🧭", layout="wide")

def extract_resume(f):
    if not f: return ""
    try:
        name = f.name.lower()
        if name.endswith(".pdf"):
            return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(f.getvalue())).pages).strip()
        if name.endswith(".docx"):
            return "\n".join(p.text for p in Document(io.BytesIO(f.getvalue())).paragraphs).strip()
        if name.endswith(".txt"):
            return f.getvalue().decode("utf-8", errors="replace").strip()
        return "Unsupported file type."
    except Exception as e:
        return f"Could not read file: {e}"

def ask_ai(prompt, language):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_API_KEY_HERE":
        return None, "Gemini API key is missing. Add it to the .env file and restart the app."
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=("You are CareerCompass AI, a practical career assistant. Be specific and honest. "
                      "Do not invent job openings, salaries, credentials, skills, or achievements. "
                      "Label uncertain or changing facts and tell the user what to verify. "
                      "Never make hiring decisions. Answer in " + language + ".\n\n" + prompt)
        )
        return response.text or "The model returned an empty response.", None
    except Exception as e:
        return None, f"Gemini request failed: {e}"

def run_ai(prompt, language):
    with st.spinner("Generating suggestions..."):
        result, error = ask_ai(prompt, language)
    if error:
        st.error(error)
        st.caption("Check the API key, model name, internet connection, and API access.")
    else:
        st.markdown(result)

st.title("🧭 CareerCompass AI")
st.caption("AI Career Counselor • Resume Analyzer • Learning Roadmap • Mock Interview")
st.warning("Prototype only. Verify AI suggestions. Do not upload sensitive identity details. This app sends prompts/resume text to your configured AI provider.")
with st.sidebar:
    st.header("Your profile")
    language = st.selectbox("Response language", ["English", "Telugu", "Hindi", "Kannada", "Tamil"])
    stage = st.selectbox("Current stage", ["BTech / college student", "Diploma student", "Recent graduate", "Working professional", "Career switcher", "Other"])
    role = st.text_input("Target role", placeholder="e.g., Data Analyst")
    experience = st.selectbox("Experience", ["Fresher", "Less than 1 year", "1–3 years", "3+ years"])
    skills = st.text_area("Skills, interests and strengths", placeholder="e.g., Python, Excel, communication")
    location = st.text_input("Preferred location", placeholder="e.g., Bengaluru / Remote")
profile = f"Stage: {stage}\nTarget role: {role or 'Not specified'}\nExperience: {experience}\nSkills/interests: {skills or 'Not specified'}\nLocation: {location or 'Not specified'}"
tabs = st.tabs(["Career Counselor", "Resume Analyzer", "Learning Roadmap", "Mock Interview", "Job & Salary Planner", "LinkedIn & Networking"])

with tabs[0]:
    st.subheader("Career guidance chatbot")
    q = st.text_area("Ask a career question", placeholder="Which entry-level roles fit my current skills?")
    if st.button("Get career guidance", type="primary", key="career"):
        if q.strip():
            run_ai(f"{profile}\nQuestion: {q}\nRank suitable career paths with reasons, strengths, skill gaps, next 3 actions, and project ideas. State assumptions.", language)
        else: st.warning("Enter a question first.")

with tabs[1]:
    st.subheader("Resume analyzer and ATS improvement")
    f = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    resume = extract_resume(f)
    if resume:
        st.text_area("Extracted text — review it before analysis", resume, height=200)
    jd = st.text_area("Paste target job description (optional)")
    if st.button("Analyze resume", type="primary", key="resume"):
        if not resume or resume.startswith("Could not") or resume.startswith("Unsupported"):
            st.warning("Upload a readable resume first.")
        elif len(resume) < 40:
            st.warning("Very little text was extracted. Try a text-based PDF or DOCX.")
        else:
            run_ai(f"Target role: {role or 'infer from job description'}\nJob description:\n{jd or 'Not supplied'}\nResume text:\n{resume[:18000]}\nAnalyze: summary, ATS readability checklist (not a guaranteed score), strengths, evidence-based skill gaps, grammar/formatting, suggested bullet improvements, relevant keywords only if truthful, and top 3 edits. Never invent achievements, numbers, education or skills.", language)
    st.caption("Scanned PDFs need OCR, which is not included. Remove personal details if they are not needed.")

with tabs[2]:
    st.subheader("Personalized learning roadmap")
    current = st.text_area("Skills you already have", placeholder="Excel, SQL basics, Python...")
    goal = st.text_area("Skills to learn", placeholder="SQL, Power BI, statistics...")
    weeks = st.slider("Plan duration in weeks", 2, 24, 8)
    if st.button("Build learning plan", type="primary", key="roadmap"):
        run_ai(f"{profile}\nCurrent skills: {current or skills or 'Not specified'}\nTarget skills: {goal or 'infer from target role'}\nDuration: {weeks} weeks. Create a week-by-week plan with goals, practice, a portfolio project, checkpoints, and final readiness checklist. Suggest reputable platforms but do not invent course links/prices; tell user to verify availability.", language)

with tabs[3]:
    st.subheader("Mock interview practice")
    ir = st.text_input("Interview role", value=role, key="ir")
    itype = st.selectbox("Interview type", ["HR / behavioral", "Technical", "Mixed"])
    level = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    answer = st.text_area("Paste/type your answer to review")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Generate question", key="genq"):
            run_ai(f"Target role: {ir or 'entry-level role'}; type: {itype}; difficulty: {level}. Give ONE interview question, what it assesses, and a simple answer structure.", language)
    with c2:
        if st.button("Review my answer", type="primary", key="review"):
            if answer.strip():
                run_ai(f"Role: {ir or role or 'entry-level role'}; type: {itype}; difficulty: {level}. Candidate answer: {answer}. Score clarity, relevance, structure, evidence and communication out of 5 each. Give specific improvements and an example that does not invent personal experience. Do not infer real emotion/personality from text.", language)
            else: st.warning("Enter an answer first.")
    st.info("This starter supports typed practice only; live microphone, speech analysis and text-to-speech are not implemented.")

with tabs[4]:
    st.subheader("Job matching and salary planning")
    job = st.text_input("Job title", value=role, key="job")
    jd2 = st.text_area("Paste job description to compare (optional)", key="jd2")
    if st.button("Analyze job match", type="primary", key="jobbtn"):
        run_ai(f"{profile}\nRole: {job or 'Not specified'}\nJob description: {jd2 or 'Not provided'}. Give match assessment with evidence, gaps, keywords, portfolio proof, interview topics, salary research factors, and reliable places to verify current openings/pay. Do not fabricate live vacancies or present salary as live verified data.", language)
    st.caption("Live LinkedIn/Indeed/Glassdoor APIs are not connected. Paste a real job description for comparison.")

with tabs[5]:
    st.subheader("LinkedIn profile and networking")
    about = st.text_area("Current LinkedIn About section (optional)")
    goal_net = st.text_area("Networking goal", placeholder="Connect with data analysts / find mentors...")
    if st.button("Improve profile and networking", type="primary", key="network"):
        run_ai(f"{profile}\nCurrent About: {about or 'Not supplied'}\nNetworking goal: {goal_net or 'Not specified'}. Create About section based only on facts supplied, headline options, connection request under 300 characters, 2-week networking plan, mentor questions, and profile checklist. Never invent achievements.", language)

with st.expander("Requirements coverage and limitations"):
    st.markdown("""
- Included: career chatbot, PDF/DOCX/TXT resume parsing, resume review, learning roadmap, typed mock interview, job-match planning, LinkedIn/networking suggestions, response-language selector.
- Not included yet: live job portal integrations, live salary feeds, voice input/output, scanned-PDF OCR, validated personality test, custom-trained models, authentication/database, mobile app packaging.
- The LLM is not a custom-trained model. Test the app on sample cases and document limitations honestly.
- This demo does not save resumes in a database, but resume text is sent to the configured AI provider for analysis.
- Do not use AI suggestions as the sole basis for hiring or career decisions.
""")
