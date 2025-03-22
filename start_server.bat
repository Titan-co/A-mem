@echo off
echo =====================================
echo A-MEM Server Starter
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Cache initialization had some issues.
  pause
)
echo.

rem Set environment variables
set SERVER_PORT=8903
set PYTHONUNBUFFERED=1
set PYTHONPATH=%CD%
set DISABLE_CHROMADB=true
set DISABLE_LLM=true

echo Environment variables set:
echo SERVER_PORT=%SERVER_PORT%
echo PYTHONPATH=%PYTHONPATH%
echo DISABLE_CHROMADB=%DISABLE_CHROMADB%
echo DISABLE_LLM=%DISABLE_LLM%
echo.

echo Starting A-MEM Server on port %SERVER_PORT%...
echo Using simplified mode (DISABLE_CHROMADB=%DISABLE_CHROMADB%, DISABLE_LLM=%DISABLE_LLM%)
echo.
echo Press Ctrl+C to stop the server when finished.
echo.

python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info

echo.
echo Server stopped.
pause
