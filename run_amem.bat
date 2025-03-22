@echo off
echo =====================================
echo A-MEM Memory System
echo =====================================
echo.

rem Initialize cache directories if they don't exist
if not exist .cache (
  echo Creating cache directories...
  mkdir .cache
  mkdir .cache\chromadb_data
  mkdir .cache\sentence_transformers
  mkdir .cache\transformers
  mkdir .cache\onnx_models
  echo Cache directories created.
)

rem Check for OpenAI API key
set api_key_set=0
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "OPENAI_API_KEY"') do (
  set api_key=%%b
  if "%%b"=="your_openai_api_key_here" (
    echo WARNING: OpenAI API key is not set in .env file.
    echo Some functionality may be limited.
    echo.
    set /p update_key="Would you like to enter an API key now? (y/n): "
    if /i "!update_key!"=="y" (
      set /p new_key="Enter your OpenAI API key: "
      powershell -Command "(Get-Content .env) -replace 'OPENAI_API_KEY=your_openai_api_key_here', 'OPENAI_API_KEY=!new_key!' | Set-Content .env"
      echo API key updated in .env file.
      set api_key_set=1
    )
  ) else (
    echo OpenAI API key is configured.
    set api_key_set=1
  )
)

echo What would you like to do?
echo 1. Run server with full functionality
echo 2. Run server with fallback mode (no OpenAI/ChromaDB)
echo 3. Run comprehensive diagnostics
echo 4. Test memory creation directly
echo 5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
  echo.
  echo Starting server with full functionality...
  python -m uvicorn simple_server:app --host 0.0.0.0 --port 8903 --log-level info
  goto end
)

if "%choice%"=="2" (
  echo.
  echo Starting server in fallback mode...
  set "DISABLE_CHROMADB=true"
  set "DISABLE_LLM=true"
  python -m uvicorn simple_server:app --host 0.0.0.0 --port 8903 --log-level info
  goto end
)

if "%choice%"=="3" (
  echo.
  echo Running comprehensive diagnostics...
  python detailed_debug.py
  goto end
)

if "%choice%"=="4" (
  echo.
  echo Testing memory creation directly...
  python debug_memory_creation.py --direct
  goto end
)

echo Exiting...

:end
echo.
echo Done!
pause
