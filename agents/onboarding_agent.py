import os
import pandas as pd
from . import get_llm_response

EMP_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "employees.csv")

def answer(question: str) -> str:
    """Answer an onboarding-related question using the employees CSV as context."""
    df = pd.read_csv(EMP_CSV)
    csv_context = df.to_markdown(index=False)

    prompt = (
        f"You are an HR onboarding assistant. Use ONLY the employee data below to answer the question.\n\n"
        f"### Employee Data\n{csv_context}\n\n"
        f"### Question\n{question}\n\n"
        f"### Answer"
    )
    return get_llm_response(prompt)
