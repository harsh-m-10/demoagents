import os
import pandas as pd
import streamlit as st
from agents import onboarding_agent, leave_agent, payroll_agent, dashboard_agent, visualization_agent, payslip_agent

st.set_page_config(page_title="HR Agents Demo", layout="wide")

st.title("🧑‍💼 HR Agents Demo (Mistral AI)")

# ---------------- Sidebar navigation ----------------
page = st.sidebar.selectbox(
    "Select page",
    ["Dashboard", "Employee Lookup", "Leave Request", "Payroll"]
)

# ---------------- Dashboard ----------------
if page == "Dashboard":
    st.header("📊 Company Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", dashboard_agent.total_employees())
    with col2:
        st.metric("Total Leave Balance (days)", dashboard_agent.total_leave_balance())
    with col3:
        st.metric("Total Payroll Expense ($)", f"{dashboard_agent.total_payroll_expense():,.2f}")
    st.subheader("Payroll Net Pay Chart")
    st.plotly_chart(visualization_agent.payroll_bar_chart())
    st.subheader("Leave Balance Chart")
    st.plotly_chart(visualization_agent.leave_balance_chart())

# ---------------- Employee Lookup ----------------
elif page == "Employee Lookup":
    st.header("🔎 Employee Lookup")
    query = st.text_input("Enter employee ID or name (case-insensitive)")
    if query:
        # Load CSV directly for deterministic lookup
        emp_csv = os.path.join(os.path.dirname(__file__), "data", "employees.csv")
        df = pd.read_csv(emp_csv)
        mask = (df['emp_id'].str.contains(query, case=False)) | (df['name'].str.contains(query, case=False))
        results = df[mask]
        if not results.empty:
            st.table(results)
        else:
            st.warning("No matching employee found.")

# ---------------- Leave Request ----------------
elif page == "Leave Request":
    st.header("🏖️ Leave Request")
    emp_id = st.text_input("Employee ID")
    days = st.number_input("Days requested", min_value=1, max_value=30, step=1)
    if st.button("Submit Request") and emp_id:
        result = leave_agent.process_leave(emp_id, int(days))
        st.markdown(result)

# ---------------- Payroll ----------------
elif page == "Payroll":
    st.header("💰 Payroll")
    emp_id = st.text_input("Employee ID for payroll")
    if st.button("Get Salary Summary") and emp_id:
        summary = payroll_agent.query_salary(emp_id)
        st.markdown(summary)
        st.subheader("Payslip")
        payslip_html = payslip_agent.generate_payslip(emp_id)
        st.markdown(payslip_html, unsafe_allow_html=True)
