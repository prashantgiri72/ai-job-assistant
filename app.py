# app.py
import subprocess
import sys

try:
    import en_core_web_sm
except ImportError:
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
        "--user"
    ])
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

# ---- SESSION STATE INIT ----
# This keeps data alive between button clicks
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "full_report" not in st.session_state:
    st.session_state.full_report = None
if "gap_report" not in st.session_state:
    st.session_state.gap_report = None
if "ats_report" not in st.session_state:
    st.session_state.ats_report = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "jd_text_saved" not in st.session_state:
    st.session_state.jd_text_saved = None
if "job_title_saved" not in st.session_state:
    st.session_state.job_title_saved = None
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = None

# ---- HEADER ----
st.title("🎯 AI-Powered Job Application Assistant")
st.markdown("Upload your resume and paste a job description to get instant analysis!")
st.divider()

# ---- SIDEBAR ----
st.sidebar.title("📋 How to Use")
st.sidebar.markdown("""
1. Upload your **Resume PDF**
2. Paste the **Job Description**
3. Enter the **Job Title**
4. Click **Analyze!**
""")
st.sidebar.divider()
st.sidebar.markdown("Built with ❤️ using Python + ML + Groq AI")

# ---- INPUT SECTION ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

with col2:
    st.subheader("📋 Paste Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=200,
        placeholder="Copy and paste the job description from LinkedIn, Naukri, etc..."
    )

job_title = st.text_input(
    "💼 Job Title (for cover letter)",
    placeholder="e.g. Full Stack Developer, ML Engineer..."
)

analyze_button = st.button("🚀 Analyze My Resume!", type="primary", use_container_width=True)

st.divider()

# ---- ANALYZE BUTTON CLICKED ----
if analyze_button:

    if not uploaded_file:
        st.error("⚠️ Please upload your resume PDF!")
        st.stop()

    if not jd_text.strip():
        st.error("⚠️ Please paste a job description!")
        st.stop()

    if not job_title.strip():
        job_title = "the position"

    # Save uploaded PDF to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("⏳ Analyzing your resume... Please wait!"):
        # Run all reports
        full_report = get_full_report(tmp_path, jd_text, jd_is_file=False)
        gap_report = get_skill_gap_report(
            full_report["missing_skills"],
            full_report["matching_skills"],
            full_report["match_score"]
        )
        ats_report = get_ats_report(tmp_path, jd_text, jd_is_file=False)
        resume_text = parse_resume(tmp_path)

    os.unlink(tmp_path)

    # ✅ Save everything to session state
    st.session_state.analysis_done = True
    st.session_state.full_report = full_report
    st.session_state.gap_report = gap_report
    st.session_state.ats_report = ats_report
    st.session_state.resume_text = resume_text
    st.session_state.jd_text_saved = jd_text
    st.session_state.job_title_saved = job_title
    st.session_state.cover_letter = None  # reset cover letter on new analysis


# ---- SHOW RESULTS (if analysis done) ----
if st.session_state.analysis_done:

    full_report = st.session_state.full_report
    gap_report = st.session_state.gap_report
    ats_report = st.session_state.ats_report

    # ===============================
    # SECTION 1 — MATCH SCORE
    # ===============================
    st.subheader("📊 Resume Match Score")

    score = full_report["match_score"]
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 Match Score", f"{score}%")
    with col2:
        st.metric("✅ Matching Skills", len(full_report["matching_skills"]))
    with col3:
        st.metric("❌ Missing Skills", len(full_report["missing_skills"]))

    if score >= 75:
        st.success("🟢 Excellent match! You're a strong candidate for this role.")
    elif score >= 50:
        st.warning("🟡 Good match! A few improvements can make you stand out.")
    elif score >= 30:
        st.warning("🟠 Average match. Work on the missing skills below.")
    else:
        st.error("🔴 Low match. Tailor your resume more to this job description.")

    st.divider()

    # ===============================
    # SECTION 2 — SKILL GAP
    # ===============================
    st.subheader("🔍 Skill Gap Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Skills You Have:**")
        if full_report["matching_skills"]:
            for skill in full_report["matching_skills"]:
                st.markdown(f"✅ {skill}")
        else:
            st.markdown("No matching skills found.")

    with col2:
        st.markdown("**❌ Skills You're Missing:**")
        if gap_report["gaps"]:
            for gap in gap_report["gaps"]:
                st.markdown(f"❌ **{gap['skill'].upper()}**")
                st.markdown(f"💡 {gap['resume_tip']}")
                st.markdown(f"🔗 [Learn Here]({gap['learn_at']})")
                st.markdown("---")
        else:
            st.success("🎉 No skill gaps found!")

    st.divider()

    # ===============================
    # SECTION 3 — ATS KEYWORDS
    # ===============================
    st.subheader("🤖 ATS Keyword Analysis")

    ats_score = ats_report["ats_score"]
    st.metric("🎯 ATS Pass Score", f"{ats_score}%")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Keywords Found in Resume:**")
        if ats_report["present_in_resume"]:
            for kw in ats_report["present_in_resume"]:
                st.markdown(f"✅ {kw}")
        else:
            st.markdown("None found.")

    with col2:
        st.markdown("**❌ Keywords to Add to Resume:**")
        if ats_report["missing_from_resume"]:
            for kw in ats_report["missing_from_resume"]:
                st.markdown(f"❌ `{kw}` ← Add this!")
        else:
            st.success("🎉 Your resume is ATS optimized!")

    st.divider()

    # ===============================
    # SECTION 4 — COVER LETTER
    # ===============================
    st.subheader("📝 AI Cover Letter Generator")

    if st.button("✨ Generate Cover Letter", type="secondary", use_container_width=True):
        with st.spinner("🤖 AI is writing your cover letter..."):
            cover_letter = generate_cover_letter(
                st.session_state.resume_text,
                st.session_state.jd_text_saved,
                st.session_state.job_title_saved
            )
        st.session_state.cover_letter = cover_letter

    # Show cover letter if generated
    if st.session_state.cover_letter:
        st.success("✅ Cover letter generated!")
        st.text_area(
            "Your Cover Letter (copy and use!)",
            value=st.session_state.cover_letter,
            height=400
        )
        st.download_button(
            label="⬇️ Download Cover Letter",
            data=st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain"
        )