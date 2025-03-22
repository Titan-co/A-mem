@echo off
echo =====================================
echo A-MEM Fallback Server
echo =====================================
echo.

rem Get port from .env file or use default
set PORT=8767
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting fallback server on port %PORT%...
echo This is a simplified server implementation without ChromaDB or LLM dependencies.
echo.
echo Press Ctrl+C to stop the server.
echo.

python fallback_server.py

echo.
echo Server stopped.
pause
