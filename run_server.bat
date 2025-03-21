@echo off
cd /d D:\MCP\A-mem
echo Starting A-MEM MCP Server...
echo.
echo Make sure you've configured your OpenAI API key in the .env file!
echo Current directory: %CD%
echo.
echo Checking dependencies...
C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe -c "import sys; print('Python version:', sys.version)"
C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe -c "import fastapi, uvicorn; print('FastAPI version:', fastapi.__version__, 'Uvicorn version:', uvicorn.__version__)"
echo.
echo Starting server with debug output...
C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug

pause
