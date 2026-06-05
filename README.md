# HR Multi-Agent Hiring Pipeline (Mistral AI)

## Overview
A **functional, end-to-end HR hiring pipeline** powered by **Mistral AI** with 3 intelligent agents that chain together: **JD Creation → Resume Screening → Offer Generation**.

This is not a simple chatbot — each agent performs real tasks with structured input/output, business logic, and file persistence.

| Agent | What It Actually Does |
|-------|----------------------|
| **JD Creator** | Takes role details + budget → generates structured JD + runs inclusive language **bias check** |
| **Resume Screener** | Parses resume files → extracts structured data → **scores & ranks** candidates against JD |
| **Offer Generator** | Creates offer letters with **hard budget guardrails** + handles salary **negotiation** rounds |

### Key Features
- ✅ **Structured I/O** — Agents accept and return structured data (dicts/JSON), not just free text
- ✅ **Bias Detection** — JD Creator flags gendered/exclusionary language and suggests alternatives
- ✅ **Resume Parsing** — Extracts name, email, skills, experience from free-form resume text
- ✅ **Scoring & Ranking** — Candidates scored 0-100 with match/gap analysis and recommendation
- ✅ **Budget Guardrails** — Hard logic (no LLM) prevents offers exceeding budget ceiling
- ✅ **Negotiation Loop** — Multi-turn: candidate counters → agent checks ceiling → ACCEPT/COUNTER/REJECT/ESCALATE
- ✅ **Agent Chaining** — Full pipeline: JD output feeds Resume Screener feeds Offer Generator
- ✅ **File Persistence** — Generated JDs and offers saved as JSON to disk

---

## Architecture

```
User Input  ──►  Streamlit UI / CLI
                      │
                      ▼
              ┌─── Pipeline Router ───┐
              │          │            │
              ▼          ▼            ▼
         JD Creator   Resume      Offer
          Agent       Screener    Generator
              │        Agent       Agent
              │          │            │
              ▼          ▼            ▼
         Mistral AI   Mistral AI   Budget Check
         (generate)   (parse+score) (hard logic)
              │          │          + Mistral AI
              ▼          ▼            │
         data/        data/          ▼
         generated_   resumes/     data/
         jds/         (input)      generated_
         (output)                  offers/
                                   (output)
```

### Agent Chaining (Full Pipeline Mode)
```
JD Creator ──► Resume Screener ──► Offer Generator
   │                │                    │
   │ JD text        │ Ranked list        │ Offer letter
   │ + budget       │ + scores           │ + budget check
   ▼                ▼                    ▼
 Bias check      Top candidate       Negotiation
                 selected            (if needed)
```

---

## Repository Structure
```
HR_MultiAgent_Project_Plan/
│   .gitignore
│   .env                    # Mistral API key – DO NOT COMMIT
│   .env.example            # Template
│   README.md
│   requirements.txt
│
├── agents/
│   ├── __init__.py                 # Mistral API client (direct REST via httpx)
│   ├── jd_creator_agent.py         # JD generation + bias check
│   ├── resume_screener_agent.py    # Resume parsing + scoring + ranking
│   └── offer_agent.py              # Offer generation + budget guardrails + negotiation
│
├── data/
│   ├── resumes/                    # Input: resume .txt files (5 samples included)
│   │   ├── priya_sharma.txt
│   │   ├── sneha_reddy.txt
│   │   ├── ananya_krishnan.txt
│   │   ├── rahul_patel.txt
│   │   └── vikram_deshmukh.txt
│   ├── generated_jds/              # Output: generated JD JSON files
│   └── generated_offers/           # Output: generated offer JSON files
│
├── app_streamlit.py                # Streamlit UI (4 pages)
├── app_cli.py                      # CLI interface (4 subcommands)
├── test_sanity.py                  # Sanity tests for all agents
└── debug_llm.py                    # Quick API key test script
```

---

## Prerequisites
- **Python 3.10+**
- A **Mistral API key** — get one free at [console.mistral.ai](https://console.mistral.ai/)

---

## Setup & Installation

### Step 1 — Navigate to the project
```powershell
cd C:\Users\harsh\Downloads\HR_MultiAgent_Project_Plan
```

### Step 2 — Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4 — Set your Mistral API key
Create a `.env` file in the project root:
```
MISTRAL_API_KEY=your_mistral_api_key_here
```
> ⚠️ Do **not** commit `.env` to any public repository. It is already in `.gitignore`.

### Step 5 — Verify setup
```powershell
python debug_llm.py        # Quick API test
python test_sanity.py       # Full agent tests
```

---

## Running the Demo

### Option 1 — Streamlit UI (recommended)
```powershell
.\venv\Scripts\activate
streamlit run app_streamlit.py
```
Opens at `http://localhost:8501`.

#### UI Pages
| Page | Description |
|------|-------------|
| **📋 JD Creator** | Fill in role details → generate JD with bias check |
| **📄 Resume Screener** | Paste JD → screen resumes → view ranked candidates with scores |
| **💼 Offer Generator** | Generate offer letters + handle negotiation rounds |
| **🔗 Full Pipeline** | Run all 3 agents in sequence with one click |

### Option 2 — CLI
```powershell
.\venv\Scripts\activate

# Generate a Job Description
python app_cli.py jd "Senior Python Developer" --skills "Python,Django,REST APIs" --budget-max 2000000

# Screen resumes against a JD
python app_cli.py screen "Senior Python Developer with 4+ years in Python, Django, REST APIs" --top-k 3

# Generate an offer letter
python app_cli.py offer "Priya Sharma" "Senior Python Developer" 1500000 --budget-max 2000000

# Handle salary negotiation
python app_cli.py negotiate "Priya Sharma" "Senior Python Developer" 1500000 1800000 --budget-max 2000000
```

---

## How Each Agent Works

### 1. JD Creator (`agents/jd_creator_agent.py`)
- **Input:** Role title, must-have/nice-to-have skills, location, work mode, budget range, team context
- **Process:** Sends structured prompt to Mistral → generates markdown JD → runs bias scan
- **Bias Check:** Scans for 15+ known biased terms (rockstar, ninja, manpower, etc.) and suggests inclusive alternatives
- **Output:** `{jd_markdown, jd_data, bias_report, saved_path, budget}`
- **Persistence:** Saves JD + metadata as JSON to `data/generated_jds/`

### 2. Resume Screener (`agents/resume_screener_agent.py`)
- **Input:** JD text + resume `.txt` files in `data/resumes/`
- **Step 1 — Parse:** For each resume, Mistral extracts structured fields (name, email, skills, experience, education)
- **Step 2 — Score:** Each parsed resume is scored 0-100 against the JD with matched/missing skills and recommendation
- **Output:** `{candidates (sorted), total_screened, shortlist (top-k)}`

### 3. Offer Generator (`agents/offer_agent.py`)
- **Input:** Candidate name, role, CTC, budget ceiling, joining date, location
- **Budget Guardrail:** Pure logic check — if `offered_ctc > budget_max`, immediately rejects (no LLM call)
- **Offer Letter:** Mistral generates professional markdown + HTML offer letter with compensation breakdown
- **Negotiation:** Multi-turn logic:
  - Counter ≤ budget → **ACCEPT**
  - Counter within 5% over budget → **ESCALATE** to hiring manager
  - Counter within 10% over → **COUNTER** at budget max
  - Counter >10% over → **REJECT**, restate original offer
- **Persistence:** Saves offer + metadata as JSON to `data/generated_offers/`

---

## Adding Your Own Resumes
Drop `.txt` files into `data/resumes/`. The Resume Screener will automatically pick them up.
Each file should contain a standard resume in plain text format.

---

## Tech Stack
| Component | Technology |
|-----------|-----------|
| LLM | Mistral AI (`mistral-small-latest` via REST API) |
| HTTP Client | httpx (direct API calls, no SDK needed) |
| Data | CSV files + Pandas + JSON |
| UI | Streamlit |
| CLI | argparse |
| Config | python-dotenv |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `MISTRAL_API_KEY not set` | Create `.env` with your key (see Step 4) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in your activated venv |
| Rate limit errors | Mistral free tier has per-minute limits. Wait and retry. |
| Resume parsing fails | Ensure resumes are `.txt` files in `data/resumes/` |
| Budget rejection | This is intentional — reduce the offered CTC or increase the budget ceiling |

---

## License
MIT License — feel free to modify, redistribute, or use commercially.

---

**Built with ❤️ using Mistral AI for the HR Multi-Agent Hiring Pipeline demo.**
