@echo off
echo =====================================
echo A-MEM Diagnostic and Server Launcher
echo =====================================
echo.

echo Running detailed diagnostics...
python detailed_debug.py
echo.

echo Do you want to start the server with full functionality? (Y/N)
set /p choice="> "

if /i "%choice%"=="Y" (
  echo Initializing cache directories...
  if not exist .cache (
    mkdir .cache
    mkdir .cache\chromadb_data
    mkdir .cache\sentence_transformers
    mkdir .cache\transformers
    mkdir .cache\onnx_models
    echo Cache directories created.
  )
  
  echo.
  echo Starting server with full functionality...
  echo Press Ctrl+C to stop the server.
  echo Error logs will be saved to server_error.log
  echo.
  
  rem Force Python to output errors immediately by adding -u flag
  python -u -m uvicorn simple_server:app --host 0.0.0.0 --port 8903 --log-level debug 2> server_error.log
  
  echo.
  echo Server stopped. Check server_error.log for any error details.
) else (
  echo Server not started.
)

echo.
echo If diagnostics failed, try these steps:
echo 1. Check your OpenAI API key in the .env file
echo 2. Ensure all dependencies are installed (pip install -r requirements.txt)
echo 3. Run 'python -c "import nltk; nltk.download(\"punkt\")"' to download NLTK data
echo 4. Check server_error.log for specific error details
echo.

pause
