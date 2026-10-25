from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skill_extractor import extract_skills


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Compare resume text against a job description and return matching metrics."""
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    try:
        vectors = TfidfVectorizer(stop_words="english").fit_transform(
            [resume_text, job_description]
        )
        similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
    except Exception:
        similarity = 0.0

    similarity = max(0.0, min(1.0, similarity))

    # Combine text similarity and skill coverage.
    if job_set:
        skill_coverage = len(matched) / len(job_set)
        score = round(100 * (0.4 * similarity + 0.6 * skill_coverage))
    else:
        skill_coverage = 0.0
        score = round(100 * similarity)

    score = max(0, min(100, score))

    suggestions = []

    if missing:
        suggestions.append(
            "Consider developing or demonstrating these job-related skills: "
            + ", ".join(missing[:10]) + "."
        )

    if not job_set:
        suggestions.append(
            "Add specific technical and professional skills to the job description "
            "for a more detailed skill comparison."
        )

    if len(resume_text.split()) < 100:
        suggestions.append(
            "Your resume contains relatively little text. Include relevant projects, "
            "experience, education, and measurable achievements where applicable."
        )

    if not suggestions:
        suggestions.append(
            "Your resume includes all detected job-related skills. Review your "
            "experience and achievements to ensure they clearly demonstrate those skills."
        )

    return {
        "score": score,
        "text_similarity": round(similarity * 100),
        "skill_coverage": round(skill_coverage * 100),
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
        "resume_word_count": len(resume_text.split()),
    }
