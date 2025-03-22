@echo off
echo Starting improved MCP wrapper...
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo This will start a server on port %PORT% and handle MCP protocol.
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

:: Set environment variable for the MCP wrapper to use
set "PORT=%PORT%"

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
