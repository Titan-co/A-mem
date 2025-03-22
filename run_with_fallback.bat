@echo off
echo =====================================
echo A-MEM Server - Fallback Implementation
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

echo Starting server with fallback ChromaDB implementation...
echo This implementation avoids permission issues by using a simplified approach.
echo.

echo Press Ctrl+C to stop the server.
echo.

rem Start server with fallback mode explicitly enabled
python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level info

echo.
echo Server stopped.
pause
