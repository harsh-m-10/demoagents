import os
import pandas as pd

EMP_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "employees.csv")
LEAVE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "leaves.csv")
PAYROLL_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "payroll.csv")

def total_employees() -> int:
    df = pd.read_csv(EMP_CSV)
    return len(df)

def total_leave_balance() -> int:
    df = pd.read_csv(LEAVE_CSV)
    df['remaining'] = df['balance'] - df['used']
    return int(df['remaining'].sum())

def total_payroll_expense() -> float:
    df = pd.read_csv(PAYROLL_CSV)
    df['net'] = df['salary'] - df['deduction']
    return float(df['net'].sum())
