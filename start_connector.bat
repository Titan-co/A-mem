@echo off
echo Starting A-MEM MCP Connector on port 8767...
echo Ensure the server is already running on port 8903.
echo.

set SERVER_PORT=8903
set PORT=8767
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set MCP_KEEP_ALIVE=true

python connector_mcp_wrapper.py
pause
