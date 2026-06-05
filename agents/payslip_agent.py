import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup Jinja2 environment – templates folder is sibling to this file
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('payslip.html')

PAYROLL_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "payroll.csv")

def generate_payslip(employee_id: str) -> str:
    """Return an HTML string representing a payslip for *employee_id*.
    Reads `payroll.csv`, extracts the row for the employee, computes net pay,
    and renders the `payslip.html` Jinja2 template.
    """
    df = pd.read_csv(PAYROLL_CSV)
    row = df.loc[df['emp_id'] == employee_id]
    if row.empty:
        return f"<p style='color:red;'>No payroll record found for employee ID {employee_id}</p>"
    row = row.iloc[0]
    net = row['salary'] - row['deduction']
    context = {
        'emp_id': row['emp_id'],
        'salary': row['salary'],
        'deduction': row['deduction'],
        'net': net,
        'month': row['month']
    }
    return template.render(**context)
