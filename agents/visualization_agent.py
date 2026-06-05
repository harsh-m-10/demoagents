import os
import pandas as pd
import plotly.express as px

PAYROLL_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "payroll.csv")
LEAVE_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "leaves.csv")

def payroll_bar_chart():
    """Return a Plotly bar chart of net pay for each employee."""
    df = pd.read_csv(PAYROLL_CSV)
    df['net'] = df['salary'] - df['deduction']
    fig = px.bar(df, x='emp_id', y='net', title='Net Pay by Employee', labels={'net': 'Net Pay', 'emp_id': 'Employee ID'})
    return fig

def leave_balance_chart():
    """Return a Plotly bar chart of remaining leave balance per employee."""
    df = pd.read_csv(LEAVE_CSV)
    df['remaining'] = df['balance'] - df['used']
    fig = px.bar(df, x='emp_id', y='remaining', title='Remaining Leave Balance', labels={'remaining': 'Days Remaining', 'emp_id': 'Employee ID'})
    return fig
