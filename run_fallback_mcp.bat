@echo off
echo =====================================
echo A-MEM Fallback MCP Server
echo =====================================
echo.

echo Setting up fallback mode...
set "DISABLE_CHROMADB=true"
set "DISABLE_LLM=true"

rem Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting fallback MCP server...
echo This simplified version should be compatible with Claude.
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.

python simple_mcp_wrapper.py

echo.
echo Server stopped.
pause
