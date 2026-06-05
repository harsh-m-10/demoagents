# HR Multi-Agent System (Mistral AI)

## Overview
A **complete, end-to-end demo** of three functional HR agents powered by **Mistral AI** with a **Streamlit UI** and **CLI interface**.

| Agent | Core Capability |
|-------|----------------|
| **Employee Lookup (Onboarding)** | Answers onboarding questions using employee data — search by ID or name, get department and email info. |
| **Leave Request Validator** | Checks remaining leave balance, validates a request, and returns a draft approval/rejection email. |
| **Payroll Assistant** | Retrieves salary, deductions, and net pay; renders a printable **payslip** (HTML) and a net-pay bar chart. |

All data lives in three CSV files under `data/`:
```
employees.csv   # emp_id, name, department, email
leaves.csv      # emp_id, balance, used
payroll.csv     # emp_id, salary, deduction, month
```
Replace these with your real HR exports — keep the column names the same.

The UI also includes a **Dashboard** with company-wide totals and two Plotly charts (payroll net-pay & leave balance).

---

## Repository Structure
```
HR_MultiAgent_Project_Plan/
│   .gitignore
│   .env               # your Mistral API key – DO NOT COMMIT
│   .env.example        # template for the key
│   README.md
│   requirements.txt
│   run.bat             # Windows one-click starter
│
├── agents/
│   ├── __init__.py             # Mistral client helper
│   ├── onboarding_agent.py     # employee lookup (Mistral-enhanced)
│   ├── leave_agent.py          # leave validation
│   ├── payroll_agent.py        # payroll summary (Mistral)
│   ├── dashboard_agent.py      # company-wide totals (no LLM)
│   ├── visualization_agent.py  # Plotly figures (no LLM)
│   └── payslip_agent.py        # Jinja2 payslip HTML generator (no LLM)
│
├── data/
│   ├── employees.csv
│   ├── leaves.csv
│   └── payroll.csv
│
├── templates/
│   └── payslip.html            # HTML template for the payslip card
│
├── app_cli.py                  # CLI interface
├── app_streamlit.py            # Main UI – launch with Streamlit
└── test_sanity.py              # Sanity test (verifies agents return valid responses)
```

---

## Prerequisites
- **Python 3.10+** installed
- A **Mistral API key** (get one free at [console.mistral.ai](https://console.mistral.ai/))

---

## Setup & Installation

### Step 1 — Clone / navigate to the project
```powershell
cd C:\Users\harsh\Downloads\HR_MultiAgent_Project_Plan
```

### Step 2 — Create a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4 — Set your Mistral API key
Create a `.env` file in the project root (or copy `.env.example`):
```
MISTRAL_API_KEY=your_mistral_api_key_here
```
> **Important:** Do **not** commit `.env` to any public repository. It is already in `.gitignore`.

### Step 5 — Run the sanity test
```powershell
python test_sanity.py
```
You should see three `[PASS]` lines confirming all agents work.

---

## Running the Demo

### Option 1 — Streamlit UI (recommended)
```powershell
.\venv\Scripts\activate
streamlit run app_streamlit.py
```
A browser window opens at `http://localhost:8501`.

#### UI Sections
| Section | Description |
|---------|-------------|
| **Dashboard** | Total employees, total remaining leave, total payroll expense, and two interactive Plotly charts. |
| **Employee Lookup** | Type a question about employees; the Mistral agent answers using the CSV data. |
| **Leave Request** | Enter employee ID and days requested; the agent validates and returns a draft email. |
| **Payroll** | Enter employee ID; get a salary summary and a formatted payslip HTML card. |

### Option 2 — CLI
```powershell
.\venv\Scripts\activate

# Onboarding question
python app_cli.py onboard "List all employees in Engineering"

# Leave request (employee E001 wants 2 days off)
python app_cli.py leave E001 2

# Payroll summary for E002
python app_cli.py payroll E002
```

### Option 3 — One-click Windows batch
Double-click `run.bat`. It will:
- Create/activate the virtual environment
- Install/upgrade dependencies
- Run the sanity test
- Launch the Streamlit UI

---

## How It Works

### Architecture
```
User Input  ──►  Streamlit / CLI
                      │
                      ▼
              ┌─── Router ───┐
              │               │
    ┌─────────┼───────────────┼─────────┐
    ▼         ▼               ▼         ▼
Onboarding  Leave          Payroll   Dashboard
  Agent     Agent           Agent     Agent
    │         │               │         │
    ▼         ▼               ▼         ▼
 employees  leaves.csv    payroll.csv  All CSVs
   .csv                                  │
    │         │               │         ▼
    └────┬────┘               │      Plotly Charts
         ▼                    ▼
   Mistral LLM          Mistral LLM
   (NL response)         (NL response)
```

1. **CSV data** is loaded by each agent and formatted as a markdown table.
2. The table is injected into a **system prompt** along with the user's question.
3. **Mistral AI** processes the prompt and returns a natural-language response.
4. The response is displayed in the UI or printed to the terminal.

### Tech Stack
| Component | Technology |
|-----------|-----------|
| LLM | Mistral AI (`mistral-small-latest`) |
| Data | CSV files + Pandas |
| UI | Streamlit |
| Charts | Plotly Express |
| Payslip | Jinja2 HTML templates |
| Config | python-dotenv |

---

## Extending the Demo
- **Add more agents** — copy the pattern in `agents/` and expose a new tab in `app_streamlit.py`.
- **Replace CSVs** — drop your own HR exports into `data/`; the agents will pick up the new values automatically.
- **Change model** — edit the `model` parameter in `agents/__init__.py` (e.g., `mistral-large-latest` for better quality).
- **Deploy** — push to GitHub, set up CI, and host the Streamlit app on any cloud provider.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `MISTRAL_API_KEY not set` | Create a `.env` file with your key (see Step 4 above). |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the activated venv. |
| Rate limit errors | The free tier has per-minute limits. Wait a minute and retry. |
| CSV column mismatches | The agents expect column names: `emp_id`, `name`, `department`, `email`, `balance`, `used`, `salary`, `deduction`, `month`. |

---

## License
This demo code is released under the **MIT License** — feel free to modify, redistribute, or use it in commercial projects.

---

**Enjoy exploring functional AI agents for HR!**
