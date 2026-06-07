import subprocess
import sys
import os

# Download spacy model only if not already present
def load_spacy_model():
    try:
        import en_core_web_sm
        return en_core_web_sm.load()
    except ImportError:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], capture_output=True)
        import en_core_web_sm
        return en_core_web_sm.load()

import streamlit as st
import tempfile
import os
from utils.resume_parser import parse_resume
from utils.jd_parser import parse_jd
from utils.scorer import get_full_report
from utils.skill_gap import get_skill_gap_report
from utils.keyword_extractor import get_ats_report
from utils.cover_letter import generate_cover_letter

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="AI Job Assistant",
    page_icon="🎯",
    layout="wide"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(90deg, #f093fb, #f5576c, #fda085);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 20px 0;
    }

    .sub-title {
        text-align: center;
        font-size: 1.2em;
        color: #a0aec0;
        margin-bottom: 30px;
    }

    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }

    /* Score circle */
    .score-box {
        text-align: center;
        padding: 30px;
        border-radius: 50%;
        width: 150px;
        height: 150px;
        margin: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5em;
        font-weight: 900;
    }

    /* Skill badges */
    .skill-match {
        display: inline-block;
        background: linear-gradient(90deg, #11998e, #38ef7d);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }

    .skill-missing {
        display: inline-block;
        background: linear-gradient(90deg, #f5576c, #f093fb);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }

    .skill-keyword {
        display: inline-block;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }

    /* Section headers */
    .section-header {
        font-size: 1.6em;
        font-weight: 700;
        margin: 20px 0 10px 0;
        padding-left: 10px;
        border-left: 4px solid #f5576c;
        color: white;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .metric-value {
        font-size: 2.5em;
        font-weight: 900;
        background: linear-gradient(90deg, #f093fb, #f5576c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.9em;
        color: #a0aec0;
        margin-top: 5px;
    }

    /* Progress bar */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 20px;
        margin: 10px 0;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #f093fb, #f5576c, #fda085);
        transition: width 0.5s ease;
    }

    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #f093fb, #f5576c) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        transition: transform 0.2s !important;
    }

    .stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4) !important;
    }

    /* File uploader */
    .stFileUploader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 2px dashed rgba(255,255,255,0.2) !important;
    }

    /* Text area */
    .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Text input */
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    .tip-box {
        background: rgba(253, 160, 133, 0.15);
        border-left: 4px solid #fda085;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
for key in ["analysis_done", "full_report", "gap_report", "ats_report",
            "resume_text", "jd_text_saved", "job_title_saved", "cover_letter"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# ---- HEADER ----
st.markdown('<div class="main-title">🎯 AI Job Application Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload your resume · Paste a JD · Get instant AI-powered insights</div>', unsafe_allow_html=True)

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("## 📋 How to Use")
    st.markdown("""
    1. 📄 Upload your **Resume PDF**
    2. 📋 Paste the **Job Description**
    3. 💼 Enter the **Job Title**
    4. 🚀 Click **Analyze!**
    5. 📝 Generate **Cover Letter**
    """)
    st.divider()
    st.markdown("### 🛠️ Powered By")
    st.markdown("🤖 Groq LLaMA 3.3")
    st.markdown("📊 TF-IDF + Cosine Similarity")
    st.markdown("🔍 spaCy + NLTK")
    st.markdown("⚡ Streamlit")
    st.divider()
    st.markdown("Built with ❤️ by **Prashant Giri**")

# ---- INPUT SECTION ----
st.markdown('<div class="section-header">📥 Input Your Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

with col2:
    st.markdown("#### 📋 Job Description")
    jd_text = st.text_area(
        "Paste the full JD here",
        height=200,
        placeholder="Copy and paste from LinkedIn, Naukri, Indeed..."
    )

job_title = st.text_input(
    "💼 Job Title",
    placeholder="e.g. Full Stack Developer, ML Engineer, Data Scientist..."
)

st.markdown("<br>", unsafe_allow_html=True)
analyze_button = st.button("🚀 Analyze My Resume!", use_container_width=True)
st.divider()

# ---- ANALYZE ----
if analyze_button:
    if not uploaded_file:
        st.error("⚠️ Please upload your resume PDF!")
        st.stop()
    if not jd_text.strip():
        st.error("⚠️ Please paste a job description!")
        st.stop()
    if not job_title.strip():
        job_title = "the position"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("🤖 AI is analyzing your resume..."):
        full_report = get_full_report(tmp_path, jd_text, jd_is_file=False)
        gap_report = get_skill_gap_report(
            full_report["missing_skills"],
            full_report["matching_skills"],
            full_report["match_score"]
        )
        ats_report = get_ats_report(tmp_path, jd_text, jd_is_file=False)
        resume_text = parse_resume(tmp_path)

    os.unlink(tmp_path)

    st.session_state.analysis_done = True
    st.session_state.full_report = full_report
    st.session_state.gap_report = gap_report
    st.session_state.ats_report = ats_report
    st.session_state.resume_text = resume_text
    st.session_state.jd_text_saved = jd_text
    st.session_state.job_title_saved = job_title
    st.session_state.cover_letter = None

# ---- RESULTS ----
if st.session_state.analysis_done:

    full_report = st.session_state.full_report
    gap_report = st.session_state.gap_report
    ats_report = st.session_state.ats_report
    score = full_report["match_score"]
    ats_score = ats_report["ats_score"]

    # ---- SCORE SECTION ----
    st.markdown('<div class="section-header">📊 Match Analysis</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{score}%</div>
            <div class="metric-label">🎯 Resume Match Score</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(full_report["matching_skills"])}</div>
            <div class="metric-label">✅ Matching Skills</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(full_report["missing_skills"])}</div>
            <div class="metric-label">❌ Missing Skills</div>
        </div>""", unsafe_allow_html=True)

    # Progress bar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="color:#a0aec0; margin-bottom:6px;">Resume Match Progress</div>
    <div class="progress-container">
        <div class="progress-bar" style="width:{score}%"></div>
    </div>
    """, unsafe_allow_html=True)

    if score >= 75:
        st.success("🟢 Excellent match! You're a strong candidate for this role!")
    elif score >= 50:
        st.warning("🟡 Good match! A few improvements can make you stand out.")
    elif score >= 30:
        st.warning("🟠 Average match. Work on the missing skills below.")
    else:
        st.error("🔴 Low match. Tailor your resume more to this job description.")

    st.divider()

    # ---- SKILLS SECTION ----
    st.markdown('<div class="section-header">🔍 Skill Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ Skills You Have")
        if full_report["matching_skills"]:
            badges = " ".join([f'<span class="skill-match">✅ {s}</span>'
                               for s in full_report["matching_skills"]])
            st.markdown(f'<div class="card">{badges}</div>', unsafe_allow_html=True)
        else:
            st.info("No matching skills found.")

    with col2:
        st.markdown("#### ❌ Skills to Add")
        if full_report["missing_skills"]:
            badges = " ".join([f'<span class="skill-missing">❌ {s}</span>'
                               for s in full_report["missing_skills"]])
            st.markdown(f'<div class="card">{badges}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 No skill gaps found!")

    st.divider()

    # ---- SKILL GAP RESOURCES ----
    if gap_report["gaps"]:
        st.markdown('<div class="section-header">📚 Learning Resources</div>', unsafe_allow_html=True)
        for gap in gap_report["gaps"]:
            with st.expander(f"❌ {gap['skill'].upper()} — Click to see how to learn it"):
                st.markdown(f'<div class="tip-box">💡 {gap["resume_tip"]}</div>',
                            unsafe_allow_html=True)
                st.markdown(f"🔗 [Learn {gap['skill']} here]({gap['learn_at']})")
        st.divider()

    # ---- ATS SECTION ----
    st.markdown('<div class="section-header">🤖 ATS Keyword Analysis</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="color:#a0aec0; margin-bottom:6px;">ATS Pass Score: {ats_score}%</div>
    <div class="progress-container">
        <div class="progress-bar" style="width:{ats_score}%"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ Keywords Found")
        if ats_report["present_in_resume"]:
            badges = " ".join([f'<span class="skill-keyword">✅ {k}</span>'
                               for k in ats_report["present_in_resume"]])
            st.markdown(f'<div class="card">{badges}</div>', unsafe_allow_html=True)
        else:
            st.info("No keywords found.")

    with col2:
        st.markdown("#### ❌ Keywords to Add")
        if ats_report["missing_from_resume"]:
            badges = " ".join([f'<span class="skill-missing">❌ {k}</span>'
                               for k in ats_report["missing_from_resume"]])
            st.markdown(f'<div class="card">{badges}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 Your resume is ATS optimized!")

    st.divider()

    # ---- COVER LETTER ----
    st.markdown('<div class="section-header">📝 AI Cover Letter Generator</div>',
                unsafe_allow_html=True)

    if st.button("✨ Generate My Cover Letter", use_container_width=True):
        with st.spinner("🤖 AI is crafting your perfect cover letter..."):
            cover_letter = generate_cover_letter(
                st.session_state.resume_text,
                st.session_state.jd_text_saved,
                st.session_state.job_title_saved
            )
        st.session_state.cover_letter = cover_letter

    if st.session_state.cover_letter:
        st.success("✅ Your cover letter is ready!")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.text_area("", value=st.session_state.cover_letter, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Cover Letter",
            data=st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True
        )