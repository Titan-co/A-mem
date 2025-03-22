@echo off
echo =====================================
echo A-MEM MCP Server - Fallback Mode
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

echo Starting the simplified server with fallback mode enabled...
echo This mode completely disables the chromadb and LLM for best compatibility
echo.

echo For debugging info, check the stderr_log.txt file
echo.

rem Create needed environment variables for fallback mode
set "DISABLE_CHROMADB=true"
set "DISABLE_LLM=true"

rem Start server with error logging
python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug 2>stderr_log.txt

echo.
echo Server stopped. Check stderr_log.txt for details.
pause
