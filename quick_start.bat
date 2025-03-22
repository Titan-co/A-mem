@echo off
echo =====================================
echo A-MEM Quick Start
echo =====================================
echo.

rem Set environment variables
set SERVER_PORT=8903
set WRAPPER_PORT=8767
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set MCP_KEEP_ALIVE=true
set PORT=%WRAPPER_PORT%

echo Starting A-MEM server...
start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info"

echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo Starting MCP connector...
echo Press Ctrl+C to stop the connector when finished.
echo.

python connector_mcp_wrapper.py

echo.
echo Connector stopped. Remember to close the server window as well.
pause
