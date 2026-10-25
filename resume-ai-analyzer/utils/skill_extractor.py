import re

SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#",
    "SQL", "HTML", "CSS", "React", "Node.js", "Flask", "Django",
    "FastAPI", "REST API", "Git", "GitHub", "Docker", "AWS",
    "Azure", "Google Cloud", "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "NLP", "Natural Language Processing",
    "Data Analysis", "Data Visualization", "Pandas", "NumPy",
    "Scikit-learn", "TensorFlow", "PyTorch", "Excel", "Power BI",
    "Tableau", "MongoDB", "PostgreSQL", "MySQL", "Firebase",
    "Communication", "Leadership", "Problem Solving",
    "Project Management", "Teamwork", "Agile"
]


def extract_skills(text: str) -> list[str]:
    """Identify recognized skills in the given text."""
    found = []
    normalized = text.lower()

    for skill in SKILLS:
        skill_lower = skill.lower()
        if not skill_lower.endswith("s"):
            pattern = r"(?<!\w)" + re.escape(skill_lower) + r"s?(?!\w)"
        else:
            pattern = r"(?<!\w)" + re.escape(skill_lower) + r"(?!\w)"

        if re.search(pattern, normalized):
            found.append(skill)

    return found
