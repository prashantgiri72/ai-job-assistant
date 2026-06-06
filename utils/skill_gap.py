 # utils/skill_gap.py

# ---- Learning resources for each skill ----
SKILL_RESOURCES = {
    "python": "https://www.learnpython.org",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "deep learning": "https://www.coursera.org/specializations/deep-learning",
    "nlp": "https://www.coursera.org/learn/classification-vector-spaces-in-nlp",
    "tensorflow": "https://www.tensorflow.org/tutorials",
    "pytorch": "https://pytorch.org/tutorials",
    "sql": "https://www.w3schools.com/sql",
    "docker": "https://docs.docker.com/get-started",
    "aws": "https://aws.amazon.com/training",
    "git": "https://learngitbranching.js.org",
    "react": "https://react.dev/learn",
    "next.js": "https://nextjs.org/learn",
    "node.js": "https://nodejs.org/en/learn",
    "mongodb": "https://learn.mongodb.com",
    "kubernetes": "https://kubernetes.io/docs/tutorials",
    "flask": "https://flask.palletsprojects.com/en/3.0.x/tutorial",
    "fastapi": "https://fastapi.tiangolo.com/tutorial",
    "pandas": "https://pandas.pydata.org/docs/getting_started",
    "numpy": "https://numpy.org/learn",
    "communication": "https://www.coursera.org/learn/wharton-communication-skills",
    "teamwork": "https://www.coursera.org/learn/teamwork-skills",
    "statistics": "https://www.khanacademy.org/math/statistics-probability",
    "computer vision": "https://www.coursera.org/learn/computer-vision-basics",
    "data analysis": "https://www.kaggle.com/learn/data-analysis",
    "data science": "https://www.kaggle.com/learn",
}

# ---- Resume improvement tips per skill ----
SKILL_TIPS = {
    "python": "Add Python projects to your resume with GitHub links.",
    "machine learning": "Mention any ML models you built, even in college projects.",
    "deep learning": "Add any neural network projects or Kaggle competitions.",
    "nlp": "Mention text processing or chatbot projects if any.",
    "tensorflow": "Build a simple image classifier and add it to GitHub.",
    "pytorch": "Complete one PyTorch tutorial project and add to GitHub.",
    "sql": "Mention database projects or queries you've written.",
    "docker": "Add 'Dockerized applications' to your project descriptions.",
    "aws": "Get AWS Free Tier and deploy one project — mention it.",
    "git": "Make sure your GitHub profile is active with contributions.",
    "react": "Add React projects with live demo links to your resume.",
    "next.js": "Mention Next.js projects with deployment on Vercel.",
    "node.js": "Highlight REST APIs you've built with Node.js.",
    "mongodb": "Mention CRUD applications using MongoDB.",
    "teamwork": "Add team projects or open source contributions.",
    "communication": "Mention presentations, talks, or technical blogs.",
    "rest": "Explicitly write 'REST API development' in your skills section.",
    "statistics": "Add statistics coursework or data analysis projects.",
    "data analysis": "Add any data analysis projects with visualizations.",
}

DEFAULT_RESOURCE = "https://www.google.com/search?q=learn+"
DEFAULT_TIP = "Add this skill to your resume with a relevant project or certification."


def get_skill_gap_report(missing_skills, matching_skills, match_score):
    """
    Takes missing skills and generates:
    - Learning resources for each missing skill
    - Resume tips for each missing skill
    - Overall resume improvement suggestions
    """

    gap_report = {
        "match_score": match_score,
        "total_missing": len(missing_skills),
        "total_matching": len(matching_skills),
        "gaps": []
    }

    for skill in missing_skills:
        resource = SKILL_RESOURCES.get(skill, DEFAULT_RESOURCE + skill.replace(" ", "+"))
        tip = SKILL_TIPS.get(skill, DEFAULT_TIP)

        gap_report["gaps"].append({
            "skill": skill,
            "learn_at": resource,
            "resume_tip": tip
        })

    return gap_report


def print_gap_report(report):
    """
    Prints the gap report in a clean readable format
    """
    print("\n" + "="*55)
    print("🔍 SKILL GAP ANALYSIS REPORT")
    print("="*55)
    print(f"🎯 Match Score     : {report['match_score']}%")
    print(f"✅ Matching Skills : {report['total_matching']}")
    print(f"❌ Missing Skills  : {report['total_missing']}")

    if report['total_missing'] == 0:
        print("\n🎉 Perfect! No skill gaps found. You're a great fit!")
        return

    print("\n📚 SKILL GAPS + WHAT TO DO:\n")
    for i, gap in enumerate(report["gaps"], 1):
        print(f"{i}. ❌ Missing Skill : {gap['skill'].upper()}")
        print(f"   💡 Resume Tip    : {gap['resume_tip']}")
        print(f"   🔗 Learn Here    : {gap['learn_at']}")
        print()


# ---- TEST IT ----
if __name__ == "__main__":
    from utils.scorer import get_full_report

    resume_path = "data/resume.pdf"
    jd_path = "data/sample_jd.txt"

    # Get full report from Day 4
    report = get_full_report(resume_path, jd_path, jd_is_file=True)

    # Generate gap report
    gap_report = get_skill_gap_report(
        report["missing_skills"],
        report["matching_skills"],
        report["match_score"]
    )

    # Print it
    print_gap_report(gap_report)
