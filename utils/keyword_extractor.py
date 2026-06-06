 
# utils/keyword_extractor.py

from sklearn.feature_extraction.text import TfidfVectorizer
from utils.jd_parser import clean_text, extract_keywords
from utils.resume_parser import parse_resume
import numpy as np


def get_top_jd_keywords(jd_text, top_n=15):
    """
    Extracts top N most important keywords from JD
    using TF-IDF scores.
    These are the words ATS systems look for.
    """

    # Clean the text first
    cleaned = clean_text(jd_text)

    # Apply TF-IDF on just the JD
    vectorizer = TfidfVectorizer(
        stop_words='english',   # removes common words like "the", "and", "is"
        ngram_range=(1, 2),     # captures single words AND two-word phrases
        max_features=50         # consider top 50 features max
    )

    # fit_transform needs a list
    tfidf_matrix = vectorizer.fit_transform([cleaned])

    # Get feature names (the actual words)
    feature_names = vectorizer.get_feature_names_out()

    # Get TF-IDF scores
    scores = tfidf_matrix.toarray()[0]

    # Combine words with their scores and sort by score
    keyword_scores = list(zip(feature_names, scores))
    keyword_scores = sorted(keyword_scores, key=lambda x: x[1], reverse=True)

    # Return top N keywords
    top_keywords = [word for word, score in keyword_scores[:top_n]]

    return top_keywords


def get_ats_report(resume_pdf_path, jd_text_or_path, jd_is_file=False):
    """
    Compares JD top keywords against resume and tells
    which ATS keywords are present and which are missing.
    """

    # Read JD
    if jd_is_file:
        with open(jd_text_or_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        jd_text = jd_text_or_path

    # Get resume text
    resume_text = parse_resume(resume_pdf_path)

    # Get top JD keywords
    top_keywords = get_top_jd_keywords(jd_text, top_n=15)

    # Check which ones are in resume
    resume_cleaned = clean_text(resume_text)

    present_keywords = []
    missing_keywords = []

    for keyword in top_keywords:
        if keyword in resume_cleaned:
            present_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    # Calculate ATS pass chance
    ats_score = round((len(present_keywords) / len(top_keywords)) * 100, 2)

    return {
        "top_jd_keywords": top_keywords,
        "present_in_resume": present_keywords,
        "missing_from_resume": missing_keywords,
        "ats_score": ats_score
    }


def print_ats_report(report):
    """
    Prints ATS report in clean readable format
    """
    print("\n" + "="*55)
    print("🤖 ATS KEYWORD ANALYSIS REPORT")
    print("="*55)

    print(f"\n📋 Top Keywords ATS Looks For ({len(report['top_jd_keywords'])}):")
    for kw in report["top_jd_keywords"]:
        print(f"   • {kw}")

    print(f"\n✅ Keywords Present in Your Resume ({len(report['present_in_resume'])}):")
    if report["present_in_resume"]:
        for kw in report["present_in_resume"]:
            print(f"   ✅ {kw}")
    else:
        print("   None found!")

    print(f"\n❌ Keywords Missing from Your Resume ({len(report['missing_from_resume'])}):")
    if report["missing_from_resume"]:
        for kw in report["missing_from_resume"]:
            print(f"   ❌ {kw}  ← ADD THIS to your resume!")
    else:
        print("   None! Your resume is ATS optimized 🎉")

    print(f"\n🎯 ATS Pass Score: {report['ats_score']}%")

    if report["ats_score"] >= 70:
        print("🟢 High chance of passing ATS filter!")
    elif report["ats_score"] >= 40:
        print("🟡 Moderate chance — add the missing keywords.")
    else:
        print("🔴 Low chance — your resume needs more JD keywords.")

    print("\n💡 TIP: Naturally add missing keywords to your")
    print("   resume's skills section or project descriptions.")


# ---- TEST IT ----
if __name__ == "__main__":
    resume_path = "data/resume.pdf"
    jd_path = "data/sample_jd.txt"

    print("⏳ Running ATS Keyword Analysis...")

    report = get_ats_report(resume_path, jd_path, jd_is_file=True)
    print_ats_report(report)