 # utils/scorer.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.resume_parser import parse_resume
from utils.jd_parser import parse_jd


def calculate_match_score(resume_text, jd_text):
    """
    Uses TF-IDF + Cosine Similarity to compare
    resume and job description.
    Returns a match score between 0 and 100.
    """

    # Put both texts in a list (TF-IDF needs a list)
    documents = [resume_text, jd_text]

    # Step 1: Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Step 2: Calculate cosine similarity between the two vectors
    score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    # Step 3: Convert to percentage (multiply by 100)
    match_percentage = round(float(score[0][0]) * 100, 2)

    return match_percentage


def get_full_report(resume_pdf_path, jd_text_or_path, jd_is_file=False):
    """
    Full report combining:
    - Match Score
    - JD Keywords
    - Resume Keywords
    - Missing skills (gap analysis)
    """

    # Parse resume
    resume_text = parse_resume(resume_pdf_path)

    # Parse JD
    jd_result = parse_jd(jd_text_or_path, is_file=jd_is_file)
    jd_text = jd_result["clean_text"]
    jd_keywords = jd_result["keywords"]

    # Parse resume keywords too
    from utils.jd_parser import extract_keywords
    resume_keywords = extract_keywords(resume_text)

    # Calculate match score
    score = calculate_match_score(resume_text, jd_text)

    # Find missing skills (in JD but not in resume)
    missing_skills = [skill for skill in jd_keywords
                      if skill not in resume_keywords]

    # Find matching skills (in both)
    matching_skills = [skill for skill in jd_keywords
                       if skill in resume_keywords]

    return {
        "match_score": score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "jd_keywords": jd_keywords,
        "resume_keywords": resume_keywords
    }


# ---- TEST IT ----
if __name__ == "__main__":
    resume_path = "data/resume.pdf"
    jd_path = "data/sample_jd.txt"

    print("⏳ Analyzing your resume against job description...")
    report = get_full_report(resume_path, jd_path, jd_is_file=True)

    print("\n" + "="*50)
    print("📊 RESUME MATCH REPORT")
    print("="*50)

    score = report["match_score"]
    print(f"\n🎯 Match Score: {score}%")

    # Score feedback
    if score >= 75:
        print("🟢 Excellent match! You're a strong candidate.")
    elif score >= 50:
        print("🟡 Good match. A few improvements needed.")
    elif score >= 30:
        print("🟠 Average match. Work on missing skills.")
    else:
        print("🔴 Low match. Tailor your resume more.")

    print(f"\n✅ Matching Skills ({len(report['matching_skills'])}):")
    for skill in report["matching_skills"]:
        print(f"   → {skill}")

    print(f"\n❌ Missing Skills ({len(report['missing_skills'])}):")
    for skill in report["missing_skills"]:
        print(f"   → {skill}")
