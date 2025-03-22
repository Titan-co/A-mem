@echo off
echo =====================================
echo A-MEM Server - Simple Test
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

rem Start the server with fallback mode in a new window
echo Starting server in fallback mode on port %PORT%...
set "DISABLE_CHROMADB=true"
set "DISABLE_LLM=true"
start "A-MEM Server" cmd /c "python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug 2>server_log.txt"

echo Waiting 10 seconds for server to start...
timeout /t 10 /nobreak > nul

echo Running simple diagnostic test...
python debug_test.py http://localhost:%PORT%

echo.
echo Test complete. Press any key to stop the server...
pause > nul

echo Stopping server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%PORT%') do (
  taskkill /F /PID %%a 2>nul
)

echo.
echo All done!
pause
