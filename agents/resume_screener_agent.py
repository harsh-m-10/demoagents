import os
import json
import glob
from . import get_llm_response

RESUMES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "resumes")


def _parse_single_resume(resume_text: str, filename: str) -> dict:
    """Use Mistral to extract structured fields from a resume."""
    prompt = f"""You are an expert HR resume parser. Extract structured information from this resume.

### Resume Text
{resume_text}

### Output
Return ONLY a valid JSON object (no markdown fences, no extra text) with these keys:
- "name": candidate full name (string)
- "email": email address or "Not found" (string)
- "phone": phone number or "Not found" (string)
- "skills": list of technical and soft skills (array of strings)
- "years_of_experience": estimated total years (number, 0 if unclear)
- "education": highest degree and institution (string)
- "current_role": most recent job title (string or "Not found")
- "summary": 1-2 sentence professional summary (string)
"""
    raw = get_llm_response(prompt)

    # Try to parse JSON from the response
    try:
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        parsed = {
            "name": "Parse error",
            "email": "N/A",
            "phone": "N/A",
            "skills": [],
            "years_of_experience": 0,
            "education": "N/A",
            "current_role": "N/A",
            "summary": raw[:200],
        }

    parsed["source_file"] = filename
    return parsed


def _score_resume_against_jd(resume_data: dict, jd_text: str) -> dict:
    """Use Mistral to score a parsed resume against a JD."""
    prompt = f"""You are an expert HR recruiter evaluating a candidate against a Job Description.

### Job Description
{jd_text}

### Candidate Profile
- Name: {resume_data.get('name', 'Unknown')}
- Skills: {', '.join(resume_data.get('skills', []))}
- Experience: {resume_data.get('years_of_experience', 0)} years
- Education: {resume_data.get('education', 'N/A')}
- Current Role: {resume_data.get('current_role', 'N/A')}
- Summary: {resume_data.get('summary', 'N/A')}

### Task
Score this candidate on a scale of 0 to 100 for fit against the JD.
Return ONLY a valid JSON object (no markdown fences) with:
- "score": integer 0-100
- "matched_skills": list of skills that match the JD requirements
- "missing_skills": list of required skills the candidate lacks
- "strengths": 2-3 bullet points on candidate strengths
- "concerns": 1-2 bullet points on gaps or concerns
- "recommendation": one of "STRONG_FIT", "GOOD_FIT", "PARTIAL_FIT", "WEAK_FIT"
"""
    raw = get_llm_response(prompt)

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        scored = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        scored = {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "strengths": ["Could not parse scoring response"],
            "concerns": ["Scoring failed — review manually"],
            "recommendation": "WEAK_FIT",
        }

    return scored


def screen_resumes(jd_text: str, top_k: int = 5) -> dict:
    """Parse all resumes in data/resumes/, score against JD, return ranked shortlist.

    Args:
        jd_text: The Job Description text to match against.
        top_k: Number of top candidates to return.

    Returns:
        dict with keys:
            candidates  – list of {resume_data, score_data} sorted by score descending
            total_screened – number of resumes processed
            shortlist – top_k candidates
    """
    if not os.path.isdir(RESUMES_DIR):
        return {"error": f"Resume directory not found: {RESUMES_DIR}", "candidates": [], "total_screened": 0, "shortlist": []}

    resume_files = glob.glob(os.path.join(RESUMES_DIR, "*.txt"))
    if not resume_files:
        return {"error": "No .txt resume files found in data/resumes/", "candidates": [], "total_screened": 0, "shortlist": []}

    candidates = []
    for fpath in resume_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        # Step 1: Parse resume
        resume_data = _parse_single_resume(text, fname)

        # Step 2: Score against JD
        score_data = _score_resume_against_jd(resume_data, jd_text)

        candidates.append({
            "resume": resume_data,
            "score": score_data,
        })

    # Sort by score descending
    candidates.sort(key=lambda c: c["score"].get("score", 0), reverse=True)

    return {
        "candidates": candidates,
        "total_screened": len(candidates),
        "shortlist": candidates[:top_k],
    }
