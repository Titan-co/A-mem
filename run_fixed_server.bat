@echo off
echo =====================================
echo A-MEM MCP Server - Fixed Version
echo =====================================
echo.

rem Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

rem Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port from .env: %PORT%
echo.

rem Set environment variable for the server
setlocal enabledelayedexpansion
set "CHROMADB_CACHE_DIR=%CD%\.cache"
set "SENTENCE_TRANSFORMERS_HOME=%CD%\.cache\sentence_transformers"
set "TRANSFORMERS_CACHE=%CD%\.cache\transformers"
echo Set cache directories to local paths to avoid permission issues.
echo.

echo Choose an option:
echo 1. Start the MCP server for Claude Desktop
echo 2. Test the integration without ChromaDB (safer)
echo 3. Run the simple API server only (for debugging)
echo 4. Exit

set /p option="Enter option (1-4): "

if "%option%"=="1" (
  echo.
  echo Starting MCP server for Claude Desktop...
  echo Press Ctrl+C to stop the server when done.
  echo.
  python improved_mcp_wrapper.py
  goto end
)

if "%option%"=="2" (
  echo.
  echo Starting API server with fallback mode...
  
  rem Create a local .env override for testing
  echo DISABLE_CHROMADB=true > .env.test
  
  start /b cmd /c "set DISABLE_CHROMADB=true && python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug"
  
  echo Waiting for server to start... (10 seconds)
  timeout /t 10 /nobreak > nul
  
  echo Running integration test...
  python test_mcp_integration.py
  
  echo.
  echo Press any key to stop the server...
  pause > nul
  
  echo Stopping server process...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%PORT%') do (
    taskkill /F /PID %%a 2>nul
  )
  
  rem Clean up test .env
  del .env.test
  goto end
)

if "%option%"=="3" (
  echo.
  echo Starting simple API server...
  echo.
  echo Access at http://localhost:%PORT%/
  echo Swagger docs at http://localhost:%PORT%/docs
  echo Press Ctrl+C to stop the server when done.
  echo.
  python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug
  goto end
)

echo Exiting...

:end
echo.
echo Server stopped.
pause
