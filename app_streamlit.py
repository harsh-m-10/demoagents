import os
import glob
import json
import streamlit as st
from agents import jd_creator_agent, resume_screener_agent, offer_agent

st.set_page_config(page_title="HR Hiring Pipeline", layout="wide")
st.title("🧑‍💼 HR Hiring Pipeline (Mistral AI)")

# ---- Sidebar navigation ----
page = st.sidebar.selectbox(
    "Pipeline Stage",
    ["📋 JD Creator", "📄 Resume Screener", "💼 Offer Generator", "🔗 Full Pipeline"]
)

# ================================================================
# 📋 JD CREATOR
# ================================================================
if page == "📋 JD Creator":
    st.header("📋 Job Description Creator")
    st.caption("Generate a professional JD with inclusive language bias check.")

    col1, col2 = st.columns(2)
    with col1:
        role_title = st.text_input("Role Title", value="Senior Python Developer")
        must_haves = st.text_area("Must-Have Skills (comma-separated)", value="Python, Django, REST APIs, PostgreSQL")
        nice_to_haves = st.text_area("Nice-to-Have Skills (comma-separated)", value="Docker, AWS, React")
    with col2:
        location = st.text_input("Location", value="Bengaluru, India")
        work_mode = st.selectbox("Work Mode", ["Remote", "Hybrid", "On-site"])
        budget_min = st.number_input("Budget Min (₹ CTC/year)", value=1200000, step=100000)
        budget_max = st.number_input("Budget Max (₹ CTC/year)", value=2000000, step=100000)
    team_context = st.text_input("Team Context (optional)", value="Backend team of 6, building a fintech SaaS product")

    if st.button("🚀 Generate JD", type="primary"):
        with st.spinner("Generating Job Description..."):
            result = jd_creator_agent.create_jd(
                role_title=role_title,
                must_haves=[s.strip() for s in must_haves.split(",") if s.strip()],
                nice_to_haves=[s.strip() for s in nice_to_haves.split(",") if s.strip()],
                location=location,
                work_mode=work_mode,
                budget_min=budget_min,
                budget_max=budget_max,
                team_context=team_context,
            )

        # Store in session for pipeline chaining
        st.session_state["last_jd"] = result

        st.subheader("Generated Job Description")
        st.markdown(result["jd_markdown"])

        # Bias report
        if result["bias_report"]:
            st.subheader("⚠️ Bias Check Findings")
            for finding in result["bias_report"]:
                st.warning(f"**{finding['term']}** → {finding['suggestion']}")
        else:
            st.success("✅ No biased language detected!")

        st.info(f"💾 Saved to: `{result['saved_path']}`")


# ================================================================
# 📄 RESUME SCREENER
# ================================================================
elif page == "📄 Resume Screener":
    st.header("📄 Resume Screener & Shortlister")
    st.caption("Parse resumes from `data/resumes/` and rank candidates against a JD.")

    # JD input — either from session or manual
    jd_source = st.radio("JD Source", ["Paste/type JD", "Use last generated JD"], horizontal=True)
    if jd_source == "Use last generated JD" and "last_jd" in st.session_state:
        jd_text = st.session_state["last_jd"]["jd_markdown"]
        st.text_area("Job Description (from JD Creator)", value=jd_text, height=200, disabled=True)
    else:
        jd_text = st.text_area(
            "Paste the Job Description",
            height=200,
            value="Senior Python Developer with 4+ years experience in Python, Django, REST APIs, PostgreSQL. Nice to have: Docker, AWS, React. Location: Bengaluru. CTC: ₹12-20 LPA."
        )

    resume_dir = os.path.join(os.path.dirname(__file__), "data", "resumes")
    resume_count = len(glob.glob(os.path.join(resume_dir, "*.txt")))
    st.info(f"📁 Found **{resume_count}** resume(s) in `data/resumes/`")

    top_k = st.slider("Top-K candidates to shortlist", 1, 10, 3)

    if st.button("🔍 Screen Resumes", type="primary"):
        with st.spinner(f"Screening {resume_count} resumes... (this may take a minute)"):
            result = resume_screener_agent.screen_resumes(jd_text, top_k=top_k)

        if "error" in result and result["error"]:
            st.error(result["error"])
        else:
            st.session_state["screening_result"] = result
            st.success(f"✅ Screened {result['total_screened']} resumes. Shortlisted top {len(result['shortlist'])}.")

            st.subheader("🏆 Shortlisted Candidates")
            for i, candidate in enumerate(result["shortlist"], 1):
                r = candidate["resume"]
                s = candidate["score"]
                with st.expander(f"#{i} — {r.get('name', 'Unknown')} | Score: {s.get('score', 'N/A')}/100 | {s.get('recommendation', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Profile**")
                        st.write(f"📧 {r.get('email', 'N/A')}")
                        st.write(f"📱 {r.get('phone', 'N/A')}")
                        st.write(f"🎓 {r.get('education', 'N/A')}")
                        st.write(f"💼 {r.get('current_role', 'N/A')}")
                        st.write(f"📅 {r.get('years_of_experience', 0)} years experience")
                        st.write(f"🛠️ Skills: {', '.join(r.get('skills', []))}")
                    with col2:
                        st.markdown("**Evaluation**")
                        st.write(f"✅ Matched: {', '.join(s.get('matched_skills', []))}")
                        st.write(f"❌ Missing: {', '.join(s.get('missing_skills', []))}")
                        st.markdown("**Strengths:**")
                        for strength in s.get("strengths", []):
                            st.write(f"  • {strength}")
                        st.markdown("**Concerns:**")
                        for concern in s.get("concerns", []):
                            st.write(f"  • {concern}")


# ================================================================
# 💼 OFFER GENERATOR
# ================================================================
elif page == "💼 Offer Generator":
    st.header("💼 Offer Letter Generator")
    st.caption("Generate offer letters with budget guardrails and negotiation support.")

    tab1, tab2 = st.tabs(["📝 Generate Offer", "🤝 Negotiate"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            candidate_name = st.text_input("Candidate Name", value="Priya Sharma")
            role_title = st.text_input("Role Title", value="Senior Python Developer", key="offer_role")
            offered_ctc = st.number_input("Offered CTC (₹/year)", value=1500000, step=100000)
        with col2:
            budget_max = st.number_input("Budget Ceiling (₹/year)", value=2000000, step=100000, key="offer_budget")
            joining_date = st.text_input("Joining Date", value="2026-07-15")
            location = st.text_input("Location", value="Bengaluru, India", key="offer_loc")
        perks = st.text_input("Additional Perks (optional)", value="Annual learning budget of ₹50,000, flexible hours")

        if st.button("📜 Generate Offer Letter", type="primary"):
            with st.spinner("Generating offer letter..."):
                result = offer_agent.generate_offer(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    offered_ctc=offered_ctc,
                    budget_max=budget_max,
                    joining_date=joining_date,
                    location=location,
                    additional_perks=perks,
                )

            st.session_state["last_offer"] = result

            if not result["budget_check"]["within_budget"]:
                st.error(f"🚫 {result['budget_check']['message']}")
            else:
                st.success("✅ Within budget — offer generated!")
                st.subheader("Offer Letter")
                st.markdown(result["offer_markdown"])
                if result.get("offer_html"):
                    with st.expander("View HTML Version"):
                        st.markdown(result["offer_html"], unsafe_allow_html=True)
                st.info(f"💾 Saved to: `{result['saved_path']}`")

    with tab2:
        st.markdown("#### Salary Negotiation Round")
        st.caption("Candidate countered? Enter details below.")
        col1, col2 = st.columns(2)
        with col1:
            neg_candidate = st.text_input("Candidate Name", value="Priya Sharma", key="neg_name")
            neg_role = st.text_input("Role", value="Senior Python Developer", key="neg_role")
            neg_original = st.number_input("Original Offer (₹)", value=1500000, step=100000, key="neg_orig")
        with col2:
            neg_counter = st.number_input("Candidate Counter (₹)", value=1800000, step=100000, key="neg_counter")
            neg_budget = st.number_input("Budget Ceiling (₹)", value=2000000, step=100000, key="neg_budget")
            neg_context = st.text_input("Context (optional)", value="Candidate has competing offer from a large MNC", key="neg_ctx")

        if st.button("🤝 Negotiate", type="primary"):
            with st.spinner("Processing negotiation..."):
                neg_result = offer_agent.negotiate(
                    candidate_name=neg_candidate,
                    role_title=neg_role,
                    original_ctc=neg_original,
                    counter_ctc=neg_counter,
                    budget_max=neg_budget,
                    negotiation_context=neg_context,
                )

            # Decision badge
            decision_colors = {
                "ACCEPT": "🟢",
                "COUNTER": "🟡",
                "REJECT": "🔴",
                "ESCALATE": "🟠",
            }
            badge = decision_colors.get(neg_result["decision"], "⚪")
            st.subheader(f"{badge} Decision: {neg_result['decision']}")
            st.write(f"**Final CTC:** ₹{neg_result['final_ctc']:,.0f}")
            st.markdown("---")
            st.markdown("**Response to Candidate:**")
            st.markdown(neg_result["response"])


# ================================================================
# 🔗 FULL PIPELINE
# ================================================================
elif page == "🔗 Full Pipeline":
    st.header("🔗 End-to-End Hiring Pipeline")
    st.caption("Run all 3 agents in sequence: JD → Screen → Offer")

    st.markdown("""
    ### How the Pipeline Works
    ```
    Step 1: JD Creator       → Generates job description + bias check
                ↓
    Step 2: Resume Screener  → Parses & ranks candidates against JD
                ↓
    Step 3: Offer Generator  → Creates offer for top candidate (with budget guardrails)
    ```
    """)

    st.subheader("Pipeline Configuration")
    role = st.text_input("Role Title", value="Senior Python Developer", key="pipe_role")
    skills = st.text_input("Must-Have Skills", value="Python, Django, REST APIs, PostgreSQL", key="pipe_skills")
    budget = st.number_input("Budget Max (₹ CTC/year)", value=2000000, step=100000, key="pipe_budget")

    if st.button("▶️ Run Full Pipeline", type="primary"):
        # Step 1: JD
        st.subheader("Step 1: Generating JD...")
        with st.spinner("Creating job description..."):
            jd_result = jd_creator_agent.create_jd(
                role_title=role,
                must_haves=[s.strip() for s in skills.split(",")],
                budget_min=budget * 0.6,
                budget_max=budget,
            )
        with st.expander("📋 Generated JD", expanded=False):
            st.markdown(jd_result["jd_markdown"])
        if jd_result["bias_report"]:
            st.warning(f"⚠️ {len(jd_result['bias_report'])} bias issue(s) found")
        else:
            st.success("✅ JD generated — no bias issues")

        # Step 2: Screen
        st.subheader("Step 2: Screening Resumes...")
        with st.spinner("Parsing and scoring resumes..."):
            screen_result = resume_screener_agent.screen_resumes(jd_result["jd_markdown"], top_k=3)

        if screen_result["shortlist"]:
            top = screen_result["shortlist"][0]
            st.success(f"✅ Screened {screen_result['total_screened']} resumes. Top candidate: **{top['resume'].get('name', 'Unknown')}** (Score: {top['score'].get('score', 'N/A')}/100)")
            with st.expander("📄 Full Shortlist", expanded=False):
                for i, c in enumerate(screen_result["shortlist"], 1):
                    st.write(f"{i}. **{c['resume'].get('name')}** — Score: {c['score'].get('score')}/100 — {c['score'].get('recommendation')}")

            # Step 3: Offer for top candidate
            st.subheader("Step 3: Generating Offer for Top Candidate...")
            top_name = top["resume"].get("name", "Candidate")
            offer_ctc = budget * 0.75  # Offer at 75% of max budget
            with st.spinner(f"Creating offer for {top_name}..."):
                offer_result = offer_agent.generate_offer(
                    candidate_name=top_name,
                    role_title=role,
                    offered_ctc=offer_ctc,
                    budget_max=budget,
                )
            if offer_result["budget_check"]["within_budget"]:
                st.success(f"✅ Offer generated for {top_name} at ₹{offer_ctc:,.0f} CTC")
                with st.expander("📜 Offer Letter", expanded=False):
                    st.markdown(offer_result["offer_markdown"])
            else:
                st.error(offer_result["budget_check"]["message"])

            st.balloons()
            st.success("🎉 Pipeline complete!")
        else:
            st.error("No resumes found to screen.")
