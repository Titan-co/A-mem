@echo off
echo =====================================
echo A-MEM Two-Port Solution
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

rem Set different ports for server and wrapper
set SERVER_PORT=8903
set WRAPPER_PORT=8767

echo Using server port: %SERVER_PORT%
echo Using wrapper port: %WRAPPER_PORT%
echo.

echo Starting the A-MEM server with connector wrapper...
echo This setup uses different ports to avoid conflicts.
echo.

echo STEP 1: Starting standard server with full functionality...
start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info"

echo Waiting for server to start...
timeout /t 10 /nobreak > nul

echo STEP 2: Starting MCP connector wrapper...
echo This wrapper connects to the running server rather than starting its own.
echo.
echo Press Ctrl+C to stop the wrapper when finished.
echo.

set PORT=%WRAPPER_PORT%
set SERVER_PORT=%SERVER_PORT%
python connector_mcp_wrapper.py

echo.
echo Wrapper stopped. Remember to close the server window as well.
pause
