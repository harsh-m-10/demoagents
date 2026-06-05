import os
import pandas as pd
from . import get_llm_response

LEAVE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "leaves.csv")

def process_leave(employee_id: str, days_requested: int) -> str:
    """Validate a leave request and return a draft response."""
    df = pd.read_csv(LEAVE_CSV)
    csv_context = df.to_markdown(index=False)

    prompt = (
        f"You are a leave-request validator for an HR system. Use ONLY the leave data below.\n\n"
        f"### Leave Balance Data\n{csv_context}\n\n"
        f"### Request\n"
        f"Employee ID: {employee_id} wants to take {days_requested} days off.\n\n"
        f"Check their remaining leave balance. If sufficient, write a short approval email. "
        f"If insufficient, explain the shortfall clearly.\n\n"
        f"### Response"
    )
    return get_llm_response(prompt)
