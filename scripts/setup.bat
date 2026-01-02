@echo off
REM Quick Start Script for Offline AI Chatbot (Windows)

echo ============================================================
echo OFFLINE AI CHATBOT - QUICK START
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "envi\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv envi
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call envi\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Next steps:
echo 1. Install Ollama from https://ollama.ai
echo 2. Run: ollama pull gemma:2b
echo 3. Add documents to data\documents\
echo 4. Run: python ingest.py
echo 5. Start Ollama: ollama serve
echo 6. Run chatbot: python app.py
echo 7. Open http://localhost:5000
echo.
echo For system check, run: python test_setup.py
echo ============================================================
pause
