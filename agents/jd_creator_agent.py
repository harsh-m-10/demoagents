import os
import json
import re
from datetime import datetime
from . import get_llm_response

GENERATED_JDS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "generated_jds")
os.makedirs(GENERATED_JDS_DIR, exist_ok=True)

# Words/phrases commonly flagged in inclusive-language audits for JDs
_BIAS_TERMS = {
    "rockstar": "high-performer",
    "ninja": "expert",
    "guru": "specialist",
    "manpower": "workforce",
    "chairman": "chairperson",
    "manmade": "synthetic",
    "he/his": "they/their",
    "she/her": "they/their",
    "young": "early-career",
    "energetic": "motivated",
    "native speaker": "fluent",
    "culture fit": "values-aligned",
    "aggressive": "ambitious",
    "dominant": "leading",
    "mankind": "humankind",
}


def _run_bias_check(jd_text: str) -> list[dict]:
    """Scan JD text for biased or non-inclusive language.
    Returns a list of {term, location, suggestion} dicts.
    """
    findings = []
    lower_text = jd_text.lower()
    for biased, suggestion in _BIAS_TERMS.items():
        # Find all occurrences
        start = 0
        while True:
            idx = lower_text.find(biased, start)
            if idx == -1:
                break
            findings.append({
                "term": biased,
                "position": idx,
                "suggestion": f"Replace '{biased}' with '{suggestion}'",
            })
            start = idx + len(biased)
    return findings


def create_jd(
    role_title: str,
    must_haves: list[str],
    nice_to_haves: list[str] | None = None,
    location: str = "Remote",
    work_mode: str = "Remote",
    budget_min: float = 0,
    budget_max: float = 0,
    team_context: str = "",
) -> dict:
    """Generate a structured Job Description using Mistral.

    Returns a dict with keys:
        jd_markdown  – formatted JD text
        jd_data      – structured dict (title, responsibilities, requirements, etc.)
        bias_report  – list of bias findings
        saved_path   – path where the JD JSON was saved
        budget       – {min, max} stored for downstream agents
    """
    must_str = ", ".join(must_haves)
    nice_str = ", ".join(nice_to_haves) if nice_to_haves else "None specified"
    budget_str = (
        f"₹{budget_min:,.0f} – ₹{budget_max:,.0f} CTC per annum"
        if budget_max > 0
        else "Not specified"
    )

    prompt = f"""You are an expert HR recruiter. Generate a professional Job Description in **Markdown** format.

### Inputs
- **Role Title:** {role_title}
- **Must-Have Skills:** {must_str}
- **Nice-to-Have Skills:** {nice_str}
- **Location:** {location}
- **Work Mode:** {work_mode}
- **Salary Band:** {budget_str}
- **Team Context:** {team_context if team_context else 'Not provided'}

### Output Requirements
Generate the JD with these sections (use markdown headings):
1. **Job Title**
2. **About the Company** (use a generic tech company description)
3. **Role Summary** (2-3 sentences)
4. **Key Responsibilities** (6-8 bullet points)
5. **Must-Have Requirements** (based on inputs)
6. **Nice-to-Have Requirements** (based on inputs)
7. **Compensation & Benefits** (include salary band if provided)
8. **Location & Work Mode**

Use inclusive, gender-neutral language throughout. Do NOT use terms like "rockstar", "ninja", "guru", "aggressive".
"""

    jd_markdown = get_llm_response(prompt)

    # --- Bias check ---
    bias_report = _run_bias_check(jd_markdown)

    # --- Structured data ---
    jd_data = {
        "role_title": role_title,
        "must_haves": must_haves,
        "nice_to_haves": nice_to_haves or [],
        "location": location,
        "work_mode": work_mode,
        "budget": {"min": budget_min, "max": budget_max},
        "team_context": team_context,
        "generated_at": datetime.now().isoformat(),
    }

    # --- Save to disk ---
    safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", role_title).strip("_").lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jd_{safe_title}_{ts}.json"
    save_path = os.path.join(GENERATED_JDS_DIR, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            {**jd_data, "jd_markdown": jd_markdown, "bias_report": bias_report},
            f,
            indent=2,
            ensure_ascii=False,
        )

    return {
        "jd_markdown": jd_markdown,
        "jd_data": jd_data,
        "bias_report": bias_report,
        "saved_path": save_path,
        "budget": {"min": budget_min, "max": budget_max},
    }
