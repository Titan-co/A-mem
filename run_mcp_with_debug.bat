@echo off
echo =====================================
echo A-MEM MCP Wrapper with Debug Mode
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

rem Set environment variables
set SERVER_PORT=8903
set WRAPPER_PORT=8767
set MCP_KEEP_ALIVE=true
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%;%PYTHONPATH%
set PORT=%WRAPPER_PORT%

echo Using server port: %SERVER_PORT%
echo Using wrapper port: %WRAPPER_PORT%
echo.

echo STEP 1: Checking if server is running...
curl -s http://localhost:%SERVER_PORT%/health
if %ERRORLEVEL% NEQ 0 (
  echo Server not running!
  echo Starting server in a new window...
  
  start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level debug"
  echo Waiting for server to start...
  timeout /t 10 /nobreak > nul
  
  curl -s http://localhost:%SERVER_PORT%/health
  if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Server still not responding. Check server window for errors.
    pause
  ) else (
    echo Server started successfully.
  )
) else (
  echo Server already running.
)
echo.

echo STEP 2: Running connector wrapper with console debug output...
echo Press Ctrl+C to stop the wrapper when finished.
echo.

python -u connector_mcp_wrapper.py

echo.
echo Wrapper stopped. Remember to close the server window if you started it.
pause
