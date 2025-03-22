@echo off
echo Starting improved MCP wrapper...
echo.
echo This will start a server on port 8765 and handle MCP protocol.
echo Press Ctrl+C to stop the server when done.
echo.

:: Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else (
  echo No virtual environment found, using system Python
)

:: Set Python path explicitly if needed
set PYTHONPATH=%CD%

:: Run the improved MCP wrapper
python improved_mcp_wrapper.py

echo.
if %ERRORLEVEL% NEQ 0 (
  echo Error: MCP wrapper exited with code %ERRORLEVEL%
  echo Check mcp_debug.log for more information
) else (
  echo MCP wrapper exited successfully
)

pause
