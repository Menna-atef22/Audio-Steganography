@echo off
echo ================================================
echo   Audio Steganography - Multi-Server Startup
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import flask; import flask_cors" 2>nul
if errorlevel 1 (
    echo.
    echo Installing required packages...
    python -m pip install -r requirements.txt
    echo.
)

REM Start the API server in a new window
echo Starting API Server on http://localhost:5000 ...
start "Flask API Server" python api_server.py

REM Wait a moment for the API server to start
timeout /t 2 /nobreak

REM Start the static HTTP server in a new window
echo.
echo Starting Static Web Server on http://localhost:8000 ...
start "Static Web Server" python -m http.server 8000 --directory frontend

REM Keep main window open
echo.
echo ================================================
echo   Servers are starting...
echo ================================================
echo.
echo API Server:      http://localhost:5000
echo Web Interface:   http://localhost:8000
echo.
echo Close the command windows to stop the servers
echo.
pause
