@echo off
echo =====================================
echo A-MEM Debug Connection Tool
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

echo Current directory: %CD%
echo Python path: %PYTHONPATH%
echo.

echo Setting up environment...
set PYTHONPATH=%CD%;%PYTHONPATH%
set PYTHONUNBUFFERED=1
set CHROMADB_CACHE_DIR=%CD%\.cache
echo.

echo Checking for simple_server.py...
if exist simple_server.py (
  echo GOOD: simple_server.py found in current directory
) else (
  echo ERROR: simple_server.py not found in current directory
)
echo.

echo STEP 1: Starting standard server with full functionality...
echo Server command: python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level debug
start "A-MEM Server" cmd /c "echo PYTHONPATH=%PYTHONPATH% && echo Starting server... && python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level debug"

echo Waiting for server to start (longer timeout)...
timeout /t 15 /nobreak > nul

echo Testing server connection...
python -c "import requests; response = requests.get('http://localhost:%SERVER_PORT%/health'); print(f'Server status: {response.status_code}, {response.text}')" 2>server_test.log
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Server health check failed. See server_test.log for details.
  type server_test.log
) else (
  echo Server check completed.
)
echo.

echo STEP 2: Starting MCP connector wrapper...
echo This wrapper connects to the running server rather than starting its own.
echo.
echo Press Ctrl+C to stop the wrapper when finished.
echo.

echo Connector command: python connector_mcp_wrapper.py
echo You can check connector_mcp.log for detailed logs.
echo.

set PORT=%WRAPPER_PORT%
set SERVER_PORT=%SERVER_PORT%
python connector_mcp_wrapper.py

echo.
echo Wrapper stopped. Remember to close the server window as well.
pause
