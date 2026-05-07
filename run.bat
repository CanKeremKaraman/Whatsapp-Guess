@echo off
echo ===================================================
echo     WhatsApp Guess Game - Backend Launcher
echo ===================================================
echo.

:: Check if the virtual environment exists and activate it
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo [WARNING] No .venv folder found. Running globally...
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
