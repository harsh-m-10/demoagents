import os
import pandas as pd
from . import get_llm_response

PAYROLL_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "payroll.csv")

def query_salary(employee_id: str) -> str:
    """Return a concise salary summary for the given employee ID."""
    df = pd.read_csv(PAYROLL_CSV)
    csv_context = df.to_markdown(index=False)

    prompt = (
        f"You are a payroll assistant. Use ONLY the payroll data below.\n\n"
        f"### Payroll Data\n{csv_context}\n\n"
        f"### Request\n"
        f"Provide a concise salary summary for employee ID: {employee_id}.\n"
        f"Include: basic salary, deductions, net pay, and the month.\n\n"
        f"### Summary"
    )
    return get_llm_response(prompt)
