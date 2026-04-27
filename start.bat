@echo off
:: ============================================================
::  DocuMind RAG Chatbot — Windows Quick Start
:: ============================================================

echo.
echo ==========================================
echo   DocuMind RAG Chatbot - Starting Up
echo ==========================================
echo.

:: Check if .env exists in backend folder
if not exist "backend\.env" (
    echo [WARNING] No .env file found in backend folder.
    if exist ".env.example" (
        copy ".env.example" "backend\.env" >nul
        echo [INFO] Created backend\.env from .env.example
        echo.
        echo [ACTION REQUIRED] Edit backend\.env and add your GROQ_API_KEY
        echo Get your FREE key at: https://console.groq.com
        echo.
        pause
    )
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found.

:: Create venv if not exists
if not exist "backend\venv" (
    echo [INFO] Creating virtual environment...
    python -m venv backend\venv
    echo [OK] Virtual environment created.
)

:: Activate and install
echo [INFO] Installing dependencies...
call backend\venv\Scripts\activate.bat
pip install -q -r backend\requirements.txt
echo [OK] Dependencies installed.

:: Start server
echo.
echo [START] Backend starting at http://localhost:8000
echo [INFO]  Open your browser to: http://localhost:8000
echo.

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
