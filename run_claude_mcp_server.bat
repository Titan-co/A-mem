@echo off
echo =====================================
echo A-MEM MCP Server for Claude Desktop
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

:: Get port from .env file or use default
set API_PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set API_PORT=%%b
)
echo Using port from .env: %API_PORT%

:: Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
  echo Activating virtual environment...
  call .venv\Scripts\activate.bat
) else (
  echo No virtual environment found, using system Python
)

:: Check if .env file exists
if not exist .env (
  echo Creating default .env file...
  (
    echo # A-MEM Configuration
    echo.
    echo # API Key for OpenAI - YOU NEED TO UPDATE THIS WITH YOUR KEY
    echo OPENAI_API_KEY=your_openai_api_key_here
    echo.
    echo # Custom API URL (if needed)
    echo OPENAI_API_URL=https://your-custom-api-endpoint.com/v1
    echo.
    echo # Model settings
    echo MODEL_NAME=all-MiniLM-L6-v2
    echo LLM_BACKEND=openai
    echo LLM_MODEL=gpt-4-turbo-preview
    echo.
    echo # Server settings
    echo HOST=0.0.0.0
    echo PORT=8765
    echo DEBUG=True
    echo.
    echo # Memory settings
    echo EVO_THRESHOLD=5
    echo.
    echo # CORS settings
    echo CORS_ORIGINS=*
    echo CORS_METHODS=*
    echo CORS_HEADERS=*
  ) > .env
  echo.
  echo ⚠️ Created default .env file
  echo Please open and update with your OpenAI API key!
  echo.
  pause
  start notepad .env
)

:: Check if user wants to test locally first
echo Choose an option:
echo 1. Start the MCP server for Claude Desktop
echo 2. Test the MCP integration locally first
echo 3. Run the simple API server only (for debugging)
echo 4. Exit
set /p option="Enter option (1-4): "

if "%option%"=="1" (
  echo.
  echo Starting MCP server for Claude Desktop...
  echo Press Ctrl+C to stop the server when done.
  echo.
  python improved_mcp_wrapper.py
) else if "%option%"=="2" (
  echo.
  echo Starting API server in the background...
  start /b cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %API_PORT% --log-level debug"
  
  echo Waiting for server to start... (10 seconds)
  ping 127.0.0.1 -n 11 > nul
  
  echo Running MCP integration test...
  echo.
  python test_mcp_integration.py
  
  echo.
  echo Press any key to stop the server...
  pause > nul
  
  echo Stopping server...
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%API_PORT%') do (
    taskkill /F /PID %%a > nul 2>&1
  )
) else if "%option%"=="3" (
  echo.
  echo Starting simple API server...
  echo Access at http://localhost:%API_PORT%/
  echo Swagger docs at http://localhost:%API_PORT%/docs
  echo Press Ctrl+C to stop the server when done.
  echo.
  python -m uvicorn simple_server:app --host 0.0.0.0 --port %API_PORT% --log-level debug
) else (
  echo Exiting...
  exit /b
)
