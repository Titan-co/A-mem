@echo off
echo =====================================
echo A-MEM Complete MCP Setup
echo =====================================
echo.

rem Initialize cache directories
echo Step 1: Initializing cache directories...
python initialize_cache.py
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Cache initialization had some issues.
  pause
)
echo.

rem Set environment variables
set SERVER_PORT=8903
set WRAPPER_PORT=8767
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set MCP_KEEP_ALIVE=true

echo Step 2: Updating environmental variables...
echo PORT=%WRAPPER_PORT%
echo SERVER_PORT=%SERVER_PORT%
echo MCP_KEEP_ALIVE=%MCP_KEEP_ALIVE%
echo PYTHONUNBUFFERED=%PYTHONUNBUFFERED%
echo PYTHONPATH=%PYTHONPATH%
echo.

echo Step 3: Checking if A-MEM server is already running...
curl -s http://localhost:%SERVER_PORT%/health 
if %ERRORLEVEL% NEQ 0 (
  echo Server not running. Starting it now...
  start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info"
  
  echo Waiting for server to start...
  
  set /a max_retries=20
  set /a count=0
  
  :retry_server_check
  timeout /t 1 >nul
  set /a count+=1
  curl -s http://localhost:%SERVER_PORT%/health
  if %ERRORLEVEL% NEQ 0 (
    if %count% LSS %max_retries% (
      echo Attempt %count%/%max_retries%...
      goto retry_server_check
    ) else (
      echo ERROR: Server failed to start after %max_retries% attempts.
      echo Check the server window for error messages.
      pause
      exit /b 1
    )
  )
  
  echo A-MEM server started successfully!
) else (
  echo A-MEM server is already running.
)
echo.

echo Step 4: Starting the MCP connector wrapper...
echo The wrapper will handle communications between Claude and the A-MEM server.
echo.
echo Press Ctrl+C to stop the wrapper when finished.
echo.

rem Set environment variables for the wrapper
set PORT=%WRAPPER_PORT%
set SERVER_PORT=%SERVER_PORT%

rem Start the wrapper
python connector_mcp_wrapper.py

echo.
echo Wrapper stopped. Remember to close the server window if you wish to shut down.
pause
