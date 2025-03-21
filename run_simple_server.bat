@echo off
cd /d D:\MCP\A-mem
echo Starting Simple A-MEM MCP Server...
echo.
echo Current directory: %CD%
echo.
echo Starting server with debug output...
C:\Users\zsun2\AppData\Local\Programs\Python\Python312\python.exe simple_server.py
pause
