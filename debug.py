 
# debug.py
from utils.resume_parser import parse_resume
from utils.jd_parser import extract_keywords

resume_text = parse_resume("data/resume.pdf")

print("📄 Your Resume Text (first 600 chars):")
print(resume_text[:600])

print("\n🔑 Skills found in your resume:")
skills = extract_keywords(resume_text)
for s in skills:
    print(f"   → {s}")