@echo off
echo =====================================
echo A-MEM Complete Setup (Server + Connector)
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
set PORT=%WRAPPER_PORT%
set DISABLE_CHROMADB=true
set DISABLE_LLM=true

echo Step 2: Environment variables set:
echo SERVER_PORT=%SERVER_PORT%
echo WRAPPER_PORT=%WRAPPER_PORT%
echo PYTHONPATH=%PYTHONPATH%
echo DISABLE_CHROMADB=%DISABLE_CHROMADB%
echo DISABLE_LLM=%DISABLE_LLM%
echo.

echo Step 3: Starting A-MEM server...
start "A-MEM Server" cmd /c "set DISABLE_CHROMADB=true && set DISABLE_LLM=true && python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info"

echo Waiting 10 seconds for server to start...
timeout /t 10 /nobreak

echo Step 4: Checking if server started properly...
curl -s http://localhost:%SERVER_PORT%/health > nul
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Server failed to start properly!
  echo Please check the server window for errors.
  pause
  exit /b 1
)

echo Server started successfully!
echo.

echo Step 5: Starting MCP connector...
echo This connector will enable Claude to use the memory system.
echo.
echo Press Ctrl+C to stop the connector when finished.
echo Remember to close the server window as well when you're done.
echo.

python connector_mcp_wrapper.py

echo.
echo Connector stopped.
pause
