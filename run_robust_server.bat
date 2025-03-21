@echo off
echo Starting A-MEM MCP Server with robust error handling...

:: Activate virtual environment
call .venv\Scripts\activate

:: Start the server with detailed logging
echo Starting server...
python server_robust.py
