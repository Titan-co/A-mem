@echo off
echo A-MEM Simple MCP Wrapper
echo =======================
echo.

:: Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%

:: Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

:: Run the simple MCP wrapper
echo Starting simple MCP wrapper on port %PORT%...
echo This is a simplified wrapper that handles just the basic MCP protocol.
echo.
echo Press Ctrl+C to stop the wrapper.
echo.
python simple_mcp_wrapper.py

pause
