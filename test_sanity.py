"""Sanity tests for the HR Hiring Pipeline agents."""
import sys

sys.stdout.reconfigure(encoding='utf-8')


def _run_test(name, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        if isinstance(result, dict) and result:
            print(f"[PASS] {name}: {str(result)[:120]}...")
            return True
        elif isinstance(result, str) and result.strip():
            print(f"[PASS] {name}: {result[:120]}...")
            return True
        else:
            print(f"[FAIL] {name}: Empty or unexpected response type: {type(result)}")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False


if __name__ == "__main__":
    all_ok = True

    # --- Test 1: JD Creator ---
    from agents import jd_creator_agent
    all_ok &= _run_test(
        "JD Creator",
        jd_creator_agent.create_jd,
        role_title="Python Developer",
        must_haves=["Python", "Django", "REST APIs"],
        budget_max=1500000,
    )

    # --- Test 2: Resume Screener ---
    from agents import resume_screener_agent
    all_ok &= _run_test(
        "Resume Screener",
        resume_screener_agent.screen_resumes,
        jd_text="Senior Python Developer with 4+ years in Python, Django, REST APIs, PostgreSQL.",
        top_k=2,
    )

    # --- Test 3: Offer Generator ---
    from agents import offer_agent

    # 3a: Within budget
    all_ok &= _run_test(
        "Offer (within budget)",
        offer_agent.generate_offer,
        candidate_name="Test Candidate",
        role_title="Python Developer",
        offered_ctc=1200000,
        budget_max=1500000,
    )

    # 3b: Over budget (should reject — no LLM call)
    result = offer_agent.generate_offer(
        candidate_name="Test Candidate",
        role_title="Python Developer",
        offered_ctc=2000000,
        budget_max=1500000,
    )
    if not result["budget_check"]["within_budget"]:
        print(f"[PASS] Offer (over budget): Correctly rejected — {result['budget_check']['message'][:80]}...")
    else:
        print("[FAIL] Offer (over budget): Should have been rejected but wasn't!")
        all_ok = False

    # 3c: Negotiation
    all_ok &= _run_test(
        "Negotiation",
        offer_agent.negotiate,
        candidate_name="Test Candidate",
        role_title="Python Developer",
        original_ctc=1200000,
        counter_ctc=1400000,
        budget_max=1500000,
    )

    print("\n" + ("=" * 50))
    print("ALL PASSED [OK]" if all_ok else "SOME TESTS FAILED [FAIL]")
    sys.exit(0 if all_ok else 1)
