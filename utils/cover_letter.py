# utils/cover_letter.py

import os
from groq import Groq
from dotenv import load_dotenv
from utils.resume_parser import parse_resume
from utils.jd_parser import parse_jd

# Load API key from .env file
load_dotenv()


def generate_cover_letter(resume_text, jd_text, job_title="the position"):
    """
    Sends resume + JD to Groq API and gets back
    a tailored professional cover letter.
    """

    # Initialize Groq client
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    # Build the prompt
    prompt = f"""
You are a professional career coach and expert cover letter writer.

Based on the resume and job description below, write a professional, 
tailored cover letter for {job_title}.

Guidelines:
- Keep it to 3-4 paragraphs
- Match the tone to the job description
- Highlight the most relevant skills from the resume
- Be specific, not generic
- End with a confident closing statement
- Do NOT include placeholder text like [Your Name] or [Date]
- Write as if you ARE the candidate

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Write the cover letter now:
"""

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # Free model on Groq
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    # Extract the text response
    cover_letter = response.choices[0].message.content
    return cover_letter


def save_cover_letter(cover_letter, output_path="data/cover_letter.txt"):
    """
    Saves the generated cover letter to a text file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cover_letter)
    print(f"✅ Cover letter saved to {output_path}")


# ---- TEST IT ----
if __name__ == "__main__":
    resume_path = "data/resume.pdf"
    jd_path = "data/sample_jd.txt"

    print("⏳ Reading resume and JD...")
    resume_text = parse_resume(resume_path)
    jd_result = parse_jd(jd_path, is_file=True)
    jd_text = jd_result["clean_text"]

    print("🤖 Sending to Groq API (Free!)...")
    print("⏳ Generating your cover letter (takes 3-5 seconds)...")

    cover_letter = generate_cover_letter(
        resume_text,
        jd_text,
        job_title="Full Stack Developer"
    )

    print("\n" + "="*55)
    print("📝 GENERATED COVER LETTER")
    print("="*55)
    print(cover_letter)

    # Save it
    save_cover_letter(cover_letter)