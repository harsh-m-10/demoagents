@echo off
rem ------------------------------------------------------------------
rem HR Agents demo – one‑click starter (Windows)
rem ------------------------------------------------------------------
rem Activate or create virtual environment
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

rem Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

rem Run sanity test – exits with error if any agent fails
python test_sanity.py
if errorlevel 1 (
    echo *** SANITY TEST FAILED – see above messages ***
    pause
    exit /b 1
)

rem Launch the Streamlit UI
streamlit run app_streamlit.py

pause
