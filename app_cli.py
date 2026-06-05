import argparse
import json
from agents import jd_creator_agent, resume_screener_agent, offer_agent

parser = argparse.ArgumentParser(description="HR Hiring Pipeline CLI (Mistral AI)")
subparsers = parser.add_subparsers(dest="mode", required=True)

# JD Creator
jd_p = subparsers.add_parser("jd", help="Generate a Job Description")
jd_p.add_argument("role", type=str, help="Role title")
jd_p.add_argument("--skills", type=str, default="Python,Django", help="Comma-separated must-have skills")
jd_p.add_argument("--budget-max", type=float, default=2000000, help="Max CTC budget")

# Resume Screener
rs_p = subparsers.add_parser("screen", help="Screen resumes against a JD")
rs_p.add_argument("jd", type=str, help="Job description text or path to JD JSON")
rs_p.add_argument("--top-k", type=int, default=3, help="Number of top candidates")

# Offer Generator
of_p = subparsers.add_parser("offer", help="Generate an offer letter")
of_p.add_argument("name", type=str, help="Candidate name")
of_p.add_argument("role", type=str, help="Role title")
of_p.add_argument("ctc", type=float, help="Offered CTC")
of_p.add_argument("--budget-max", type=float, default=2000000, help="Budget ceiling")

# Negotiation
ng_p = subparsers.add_parser("negotiate", help="Handle salary negotiation")
ng_p.add_argument("name", type=str, help="Candidate name")
ng_p.add_argument("role", type=str, help="Role title")
ng_p.add_argument("original", type=float, help="Original offer CTC")
ng_p.add_argument("counter", type=float, help="Candidate counter CTC")
ng_p.add_argument("--budget-max", type=float, default=2000000, help="Budget ceiling")

args = parser.parse_args()

if args.mode == "jd":
    result = jd_creator_agent.create_jd(
        role_title=args.role,
        must_haves=[s.strip() for s in args.skills.split(",")],
        budget_max=args.budget_max,
    )
    print(result["jd_markdown"])
    if result["bias_report"]:
        print("\nWARNING - BIAS CHECK FINDINGS:")
        for f in result["bias_report"]:
            print(f"  - {f['suggestion']}")
    print(f"\nSaved: {result['saved_path']}")

elif args.mode == "screen":
    # If JD arg is a file path, read it
    jd_text = args.jd
    if jd_text.endswith(".json") and __import__("os").path.isfile(jd_text):
        with open(jd_text) as f:
            jd_text = json.load(f).get("jd_markdown", jd_text)

    result = resume_screener_agent.screen_resumes(jd_text, top_k=args.top_k)
    print(f"Screened {result['total_screened']} resumes.\n")
    for i, c in enumerate(result["shortlist"], 1):
        r, s = c["resume"], c["score"]
        print(f"#{i} {r.get('name', '?')} | Score: {s.get('score', '?')}/100 | {s.get('recommendation', '?')}")
        print(f"   Skills: {', '.join(r.get('skills', []))}")
        print(f"   Matched: {', '.join(s.get('matched_skills', []))}")
        print(f"   Missing: {', '.join(s.get('missing_skills', []))}")
        print()

elif args.mode == "offer":
    result = offer_agent.generate_offer(
        candidate_name=args.name,
        role_title=args.role,
        offered_ctc=args.ctc,
        budget_max=args.budget_max,
    )
    if not result["budget_check"]["within_budget"]:
        print(f"ERROR: {result['budget_check']['message']}")
    else:
        print(result["offer_markdown"])
        print(f"\nSaved: {result['saved_path']}")

elif args.mode == "negotiate":
    result = offer_agent.negotiate(
        candidate_name=args.name,
        role_title=args.role,
        original_ctc=args.original,
        counter_ctc=args.counter,
        budget_max=args.budget_max,
    )
    print(f"Decision: {result['decision']}")
    print(f"Final CTC: ₹{result['final_ctc']:,.0f}")
    print(f"\n{result['response']}")
