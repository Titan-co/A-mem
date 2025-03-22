@echo off
echo =====================================
echo A-MEM MCP Server - Fix and Run
echo =====================================
echo.

rem Ensure cache directories exist
if not exist .cache (
  echo Creating cache directories...
  mkdir .cache
  mkdir .cache\chromadb_data
  mkdir .cache\sentence_transformers
  mkdir .cache\transformers
  mkdir .cache\onnx_models
  echo Cache directories created.
)

rem Get port from .env file or use default
set PORT=8903
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)

echo Using port: %PORT%
echo.

echo What would you like to do?
echo 1. Run simple server in full fallback mode (most reliable)
echo 2. Run MCP wrapper for Claude
echo 3. Run diagnostic test only
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
  echo.
  echo Running simple server in fallback mode...
  
  rem Set environment variables for fallback
  set "DISABLE_CHROMADB=true"
  set "DISABLE_LLM=true"
  
  rem Start the server
  python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug
  goto end
)

if "%choice%"=="2" (
  echo.
  echo Running MCP wrapper for Claude...
  
  rem Start the server with the MCP wrapper
  python improved_mcp_wrapper.py
  goto end
)

if "%choice%"=="3" (
  echo.
  echo Running diagnostic test...
  
  rem Start a temporary server in the background
  echo Starting temporary server...
  set "DISABLE_CHROMADB=true"
  set "DISABLE_LLM=true"
  start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug 2>server_log.txt"
  
  echo Waiting for server to start...
  timeout /t 10 /nobreak > nul
  
  echo Running test...
  python debug_test.py http://localhost:%PORT%
  
  echo Stopping server...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%PORT%') do (
    taskkill /F /PID %%a 2>nul
  )
  
  echo Test complete.
  goto end
)

echo Exiting...

:end
echo.
echo Done!
pause
