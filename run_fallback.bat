@echo off
echo A-MEM Fallback Server
echo =====================
echo.

:: Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%

:: Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

:: Run the fallback server
echo Starting fallback server on port %PORT%...
echo This is a simplified server that doesn't require complex CORS settings.
echo.
echo Press Ctrl+C to stop the server.
echo.
python fallback_server.py

pause
