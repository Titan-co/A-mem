@echo off
echo A-MEM MCP Server for Claude Desktop
echo =====================================

if exist .venv\\Scripts\\activate.bat (
  call .venv\\Scripts\\activate.bat
)

set PORT=8765

echo Choose an option:
echo 1. Start the MCP server for Claude Desktop
echo 2. Test the MCP integration locally first
echo 3. Run the simple API server only (for debugging)
echo 4. Exit

set /p option=\"Enter option (1-4): \"

if \"%option%\"==\"1\" (
  echo Starting MCP server for Claude Desktop...
  python improved_mcp_wrapper.py
  exit /b
)

if \"%option%\"==\"2\" (
  echo Starting API server in the background...
  start /b cmd /c python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug
  
  echo Waiting for server to start...
  timeout /t 5 /nobreak > nul
  
  echo Running MCP integration test...
  python test_mcp_integration.py
  
  echo Press any key to stop the server...
  pause > nul
  
  exit /b
)

if \"%option%\"==\"3\" (
  echo Starting simple API server...
  echo Access at http://localhost:%PORT%/
  echo Swagger docs at http://localhost:%PORT%/docs
  python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug
  exit /b
)

echo Exiting...