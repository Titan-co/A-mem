@echo off
echo ===========================================
echo A-MEM MCP Server - Non-interactive Test
echo ===========================================
echo.

rem Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

rem Run diagnostics first
echo Running diagnostics...
python diagnose_server.py
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

rem Get port from .env file or use default
set PORT=8901
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%

rem Set environment variable for ChromaDB to bypass issues
set DISABLE_CHROMADB=false
set PYTHONPATH=%CD%

echo Running server connection test...
python test_server_connection.py

rem Check if the server test was successful
if %ERRORLEVEL% NEQ 0 (
  echo Server connection test failed with code %ERRORLEVEL%
  echo Aborting integration test.
  exit /b %ERRORLEVEL%
)

echo Server connection successful, proceeding with integration test...

echo Running simplified integration test...
python test_integration_simple.py

echo.
echo Test completed. Stopping server...

rem Find and kill the server process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%PORT%') do (
  echo Terminating process %%a
  taskkill /F /PID %%a 2>nul
)

echo.
echo Test run complete. Check results above.
echo Server logs saved to server_log.txt

timeout /t 5
