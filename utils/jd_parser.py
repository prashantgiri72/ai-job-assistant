 
# utils/jd_parser.py

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required nltk data (only runs once)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# ---- Common tech skills list (our custom dictionary) ----
SKILL_KEYWORDS = ["react", "next.js", "node.js", "express.js", "react.js",
"tailwind", "html", "css", "vercel", "jwt",
"nextauth", "cloudinary", "postman", "clerk",
"full stack", "frontend", "backend", "web development",
"teamwork", "rest api",
    "python", "java", "javascript", "c++", "sql", "r",
    "machine learning", "deep learning", "nlp", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "pandas", "numpy", "matplotlib", "seaborn",
    "flask", "fastapi", "django", "streamlit",
    "docker", "kubernetes", "git", "github", "linux",
    "aws", "azure", "gcp", "cloud",
    "data analysis", "data science", "statistics",
    "neural network", "random forest", "svm", "regression",
    "classification", "clustering", "feature engineering",
    "api", "rest", "mongodb", "postgresql", "mysql",
    "communication", "teamwork", "problem solving"
]


def read_jd_from_file(file_path):
    """
    Reads job description from a .txt file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def clean_text(text):
    """
    Cleans raw text:
    - Lowercase
    - Remove special characters
    - Remove extra spaces
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def extract_keywords(text):
    """
    Extracts important skill keywords from text
    by matching against our SKILL_KEYWORDS list
    """
    cleaned = clean_text(text)
    found_skills = []

    for skill in SKILL_KEYWORDS:
        if skill in cleaned:
            found_skills.append(skill)

    return found_skills


def parse_jd(text_or_path, is_file=False):
    """
    Main function — call this to parse any JD.
    - text_or_path: either raw JD text OR a file path
    - is_file: set True if passing a file path
    Returns: dict with clean_text and keywords
    """
    if is_file:
        raw_text = read_jd_from_file(text_or_path)
    else:
        raw_text = text_or_path

    cleaned = clean_text(raw_text)
    keywords = extract_keywords(raw_text)

    return {
        "clean_text": cleaned,
        "keywords": keywords
    }


# ---- TEST IT ----
if __name__ == "__main__":
    # Test using our sample_jd.txt from Day 1
    result = parse_jd("data/sample_jd.txt", is_file=True)

    print("✅ JD parsed successfully!")
    print(f"\n📄 Clean Text Preview:")
    print(result["clean_text"][:300])
    print(f"\n🔑 Keywords Found ({len(result['keywords'])} total):")
    for kw in result["keywords"]:
        print(f"   → {kw}")
    print("\n--- Testing with raw text ---")
    raw_jd = """
    We need a Data Scientist with Python, TensorFlow, 
    and strong SQL skills. Experience with AWS and Docker is a plus.
    Good communication and teamwork required.
    """
    result2 = parse_jd(raw_jd, is_file=False)
    print(f"🔑 Keywords from raw text: {result2['keywords']}")    