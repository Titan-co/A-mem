@echo off
echo =====================================
echo A-MEM Complete Debug Suite
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
if not exist .cache (
  mkdir .cache
  mkdir .cache\chromadb_data
  mkdir .cache\sentence_transformers
  mkdir .cache\transformers
  mkdir .cache\onnx_models
  echo Cache directories created.
) else (
  echo Cache directories already exist.
)
echo.

rem Check OpenAI API key in .env file
set has_api_key=0
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "OPENAI_API_KEY"') do (
  set api_key=%%b
  if "%%b"=="your_openai_api_key_here" (
    echo WARNING: OpenAI API key is not set in .env file
    echo To use the LLM functionality, you need to set a valid API key.
    echo.
    set /p update_key="Would you like to enter an API key now? (y/n): "
    if /i "!update_key!"=="y" (
      set /p new_key="Enter your OpenAI API key: "
      powershell -Command "(Get-Content .env) -replace 'OPENAI_API_KEY=your_openai_api_key_here', 'OPENAI_API_KEY=!new_key!' | Set-Content .env"
      echo API key updated in .env file.
      set has_api_key=1
    )
  ) else (
    echo API key found in .env file.
    set has_api_key=1
  )
)

rem Check port in .env file
set PORT=8903
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo STEP 1: Running basic diagnostics...
python detailed_debug.py
echo.

echo STEP 2: Testing direct memory creation...
python debug_memory_creation.py --direct
echo.

echo Would you like to start the server and test the API? (y/n)
set /p start_server="> "

if /i "%start_server%"=="y" (
  echo.
  echo STEP 3: Starting server with full logging...
  echo Starting server on port %PORT%...
  echo The server will run in a separate window.
  echo.
  
  rem Start server in a new window with full logging
  start "A-MEM Server" cmd /c "python -u -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level debug 2> server_full_log.txt"
  
  echo Waiting 15 seconds for server to start...
  timeout /t 15 /nobreak > nul
  
  echo STEP 4: Testing memory creation via API...
  python debug_memory_creation.py --api %PORT%
  
  echo.
  echo Do you want to stop the server now? (y/n)
  set /p stop_server="> "
  
  if /i "%stop_server%"=="y" (
    echo Stopping server...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr 0.0.0.0:%PORT%') do (
      taskkill /F /PID %%a 2>nul
    )
    echo Server stopped.
  ) else (
    echo Server is still running. Remember to stop it manually when done.
  )
)

echo.
echo Complete debug process finished!
echo.
echo Log Files:
echo - detailed_debug.log: General diagnostics
echo - memory_creation_debug.log: Memory creation tests
echo - server_full_log.txt: Server logs (if server was started)
echo.
echo If you're still having issues, check these log files for detailed error information.
echo.

pause
