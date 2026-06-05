import argparse
from agents import onboarding_agent, leave_agent, payroll_agent

parser = argparse.ArgumentParser(description="HR Multi-Agent demo (Mistral AI)")
subparsers = parser.add_subparsers(dest="mode", required=True)

# Onboarding sub‑command
onb = subparsers.add_parser("onboard", help="Ask an onboarding question")
onb.add_argument("question", type=str, help="Question string")

# Leave sub‑command
lev = subparsers.add_parser("leave", help="Submit a leave request")
lev.add_argument("emp_id", type=str, help="Employee ID")
lev.add_argument("days", type=int, help="Days requested")

# Payroll sub‑command
pay = subparsers.add_parser("payroll", help="Get salary summary")
pay.add_argument("emp_id", type=str, help="Employee ID")

args = parser.parse_args()

if args.mode == "onboard":
    print(onboarding_agent.answer(args.question))
elif args.mode == "leave":
    print(leave_agent.process_leave(args.emp_id, args.days))
elif args.mode == "payroll":
    print(payroll_agent.query_salary(args.emp_id))
