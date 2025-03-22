@echo off
echo =====================================
echo A-MEM Server with ChromaDB Enabled
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
if %ERRORLEVEL% NEQ 0 (
  echo WARNING: Cache initialization had some issues.
  echo The server will still start, but ChromaDB might not work properly.
  echo.
  set /p continue="Do you want to continue anyway? (y/n): "
  if /i not "%continue%"=="y" goto end
)
echo.

rem Get port from .env file or use default
set PORT=8903
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting server with ChromaDB enabled...
echo.
echo This server will use ChromaDB for memory storage and retrieval.
echo Press Ctrl+C to stop the server.
echo.

rem Start the server with full functionality (ChromaDB enabled)
python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level info

echo.
echo Server stopped.

:end
echo.
echo Exiting...
pause
