@echo off
echo =====================================
echo A-MEM Memory Control Protocol Server
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

rem Get port from .env file or use default
set PORT=8903
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting MCP server...
echo This will make the memory system available to Claude.
echo.

echo Press Ctrl+C to stop the server.
echo.

rem Start the improved MCP wrapper
C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe improved_mcp_wrapper.py

echo.
echo Server stopped.
pause
