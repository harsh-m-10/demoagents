import sys
from agents import onboarding_agent, leave_agent, payroll_agent

def _run_test(name, func, *args):
    try:
        result = func(*args)
        if isinstance(result, str) and result.strip():
            print(f"[PASS] {name}: {result[:80]}...")
            return True
        else:
            print(f"[FAIL] {name}: Empty or non‑string response")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

if __name__ == "__main__":
    all_ok = True
    all_ok &= _run_test("Onboarding", onboarding_agent.answer, "What documents does a new hire need?")
    all_ok &= _run_test("Leave", leave_agent.process_leave, "E001", 2)
    all_ok &= _run_test("Payroll", payroll_agent.query_salary, "E002")
    sys.exit(0 if all_ok else 1)
