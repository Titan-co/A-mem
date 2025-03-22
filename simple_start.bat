@echo off
echo =====================================
echo A-MEM Simple Starter
echo =====================================
echo.

rem Set environment variables
set SERVER_PORT=8903
set WRAPPER_PORT=8767
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set MCP_KEEP_ALIVE=true
set PORT=%WRAPPER_PORT%

echo Environment variables set:
echo PORT=%PORT%
echo SERVER_PORT=%SERVER_PORT%
echo PYTHONPATH=%PYTHONPATH%
echo.

echo Starting A-MEM server...
start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info"

echo Waiting 10 seconds for server to start...
timeout /t 10 /nobreak

echo Starting MCP connector...
echo Press Ctrl+C to stop when finished.
echo.

python connector_mcp_wrapper.py

echo Connector stopped.
pause
