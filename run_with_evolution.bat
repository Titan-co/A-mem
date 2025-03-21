@echo off
echo Running A-MEM MCP Server with memory evolution enabled...

:: Activate virtual environment
call .venv\Scripts\activate

:: Start the server with detailed logging
echo Starting server...
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug
