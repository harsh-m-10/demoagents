import os
import json
from datetime import datetime
from . import get_llm_response

GENERATED_OFFERS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "generated_offers")
os.makedirs(GENERATED_OFFERS_DIR, exist_ok=True)


def _check_budget(offered_ctc: float, budget_max: float) -> dict:
    """Hard guardrail: reject if offered CTC exceeds budget ceiling."""
    if budget_max > 0 and offered_ctc > budget_max:
        return {
            "within_budget": False,
            "message": (
                f"REJECTED: Offered CTC ₹{offered_ctc:,.0f} exceeds budget ceiling "
                f"₹{budget_max:,.0f} by ₹{offered_ctc - budget_max:,.0f}. "
                f"Reduce offer or escalate to hiring manager for approval."
            ),
        }
    return {"within_budget": True, "message": "Within budget."}


def generate_offer(
    candidate_name: str,
    role_title: str,
    offered_ctc: float,
    budget_max: float,
    joining_date: str = "",
    location: str = "Remote",
    additional_perks: str = "",
) -> dict:
    """Generate a professional offer letter with budget guardrails.

    Returns dict with:
        budget_check  – result of guardrail check
        offer_markdown – formatted offer letter (None if over budget)
        offer_html     – HTML version
        saved_path     – file where the offer was saved
    """
    # --- Budget guardrail (hard logic, no LLM) ---
    budget_result = _check_budget(offered_ctc, budget_max)
    if not budget_result["within_budget"]:
        return {
            "budget_check": budget_result,
            "offer_markdown": None,
            "offer_html": None,
            "saved_path": None,
        }

    if not joining_date:
        joining_date = "To be confirmed"

    prompt = f"""You are an HR professional. Generate a formal Offer Letter in **Markdown** format.

### Details
- **Candidate Name:** {candidate_name}
- **Role:** {role_title}
- **Annual CTC:** ₹{offered_ctc:,.0f}
- **Joining Date:** {joining_date}
- **Location:** {location}
- **Additional Perks:** {additional_perks if additional_perks else 'Standard benefits package'}

### Requirements
Include these sections:
1. Opening congratulations
2. Position and reporting details
3. Compensation breakdown (basic salary ~40% of CTC, HRA ~20%, special allowance ~20%, PF + insurance ~20%)
4. Benefits and perks
5. Joining date and location
6. Terms and conditions (probation period: 6 months, notice period: 2 months)
7. Acceptance deadline (14 days from offer date)
8. Warm closing

Use today's date as the offer date. Make it professional but warm.
"""
    offer_md = get_llm_response(prompt)

    # Generate HTML version
    html_prompt = f"""Convert this offer letter to clean HTML with professional styling (inline CSS).
Use a clean serif font, proper spacing, and a subtle border. Include a company header.

{offer_md}

Return ONLY the HTML, no markdown fences.
"""
    offer_html = get_llm_response(html_prompt)

    # --- Save to disk ---
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = candidate_name.replace(" ", "_").lower()
    filename = f"offer_{safe_name}_{ts}.json"
    save_path = os.path.join(GENERATED_OFFERS_DIR, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "candidate_name": candidate_name,
                "role_title": role_title,
                "offered_ctc": offered_ctc,
                "budget_max": budget_max,
                "joining_date": joining_date,
                "location": location,
                "offer_markdown": offer_md,
                "generated_at": datetime.now().isoformat(),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return {
        "budget_check": budget_result,
        "offer_markdown": offer_md,
        "offer_html": offer_html,
        "saved_path": save_path,
    }


def negotiate(
    candidate_name: str,
    role_title: str,
    original_ctc: float,
    counter_ctc: float,
    budget_max: float,
    negotiation_context: str = "",
) -> dict:
    """Handle a salary negotiation round.

    The candidate has countered with counter_ctc. The agent:
    1. Checks if counter is within budget ceiling → auto-accept
    2. If slightly over (within 10% of max) → suggest a middle ground
    3. If way over → reject and explain

    Returns dict with:
        decision     – ACCEPT / COUNTER / REJECT / ESCALATE
        response     – natural language response to candidate
        final_ctc    – the CTC in the response (if applicable)
    """
    # Pure logic first
    if counter_ctc <= budget_max:
        decision = "ACCEPT"
        final_ctc = counter_ctc
    elif counter_ctc <= budget_max * 1.05:
        # Within 5% — escalate to hiring manager
        decision = "ESCALATE"
        final_ctc = counter_ctc
    elif counter_ctc <= budget_max * 1.10:
        # Within 10% — counter with budget max
        decision = "COUNTER"
        final_ctc = budget_max
    else:
        decision = "REJECT"
        final_ctc = original_ctc

    prompt = f"""You are an HR negotiation specialist. A candidate has countered a salary offer.

### Context
- **Candidate:** {candidate_name}
- **Role:** {role_title}
- **Original Offer:** ₹{original_ctc:,.0f} CTC
- **Candidate Counter:** ₹{counter_ctc:,.0f} CTC
- **Budget Ceiling:** ₹{budget_max:,.0f} CTC
- **Decision:** {decision}
- **Final CTC (if applicable):** ₹{final_ctc:,.0f}
{f'- **Additional Context:** {negotiation_context}' if negotiation_context else ''}

### Task
Write a professional, warm response email to the candidate based on the decision:
- **ACCEPT**: Congratulate them and confirm the accepted CTC.
- **COUNTER**: Politely explain you can meet them at ₹{budget_max:,.0f} and highlight non-monetary benefits.
- **REJECT**: Politely decline, restate the original offer, and give a deadline.
- **ESCALATE**: Acknowledge their request, explain it needs manager approval, and give a timeline (2 business days).

Write the email only, no subject line.
"""
    response_text = get_llm_response(prompt)

    return {
        "decision": decision,
        "response": response_text,
        "original_ctc": original_ctc,
        "counter_ctc": counter_ctc,
        "final_ctc": final_ctc,
        "budget_max": budget_max,
    }
