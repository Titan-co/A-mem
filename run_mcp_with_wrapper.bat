@echo off
echo =====================================
echo A-MEM Memory System with MCP Wrapper
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Cache initialization had some issues.
  pause
)
echo.

rem Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting the MCP server with wrapper...
echo This setup uses a specialized wrapper to connect to Claude.
echo.

echo STEP 1: Starting server in a new window...
start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT%"

echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo STEP 2: Starting MCP wrapper...
echo The wrapper will handle communication between Claude and the server.
echo.
echo Press Ctrl+C to stop the wrapper when finished.
echo.

python simple_mcp_wrapper.py

echo.
echo Wrapper stopped. Remember to close the server window as well.
pause
