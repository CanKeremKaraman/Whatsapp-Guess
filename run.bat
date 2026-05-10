@echo off
echo ===================================================
echo     WhatsApp Guess Game - Backend Launcher
echo ===================================================
echo.

:: Ensure virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo [WARNING] No .venv folder found. Running globally...
)

:: Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo [INFO] Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo [INFO] Starting FastAPI server...
echo [INFO] Open your browser and go to: http://localhost:8000
echo.

:: Launch the Frontend in the default browser
echo [INFO] Launching Frontend...
start "" "Web\index.html"

:: Launch the FastAPI server
uvicorn GuessBackend:app --reload --host 0.0.0.0 --port 8000

:: Pause if the server crashes so the user can see the error
pause
