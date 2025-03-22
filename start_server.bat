@echo off
echo Starting A-MEM Server on port 8903...
set SERVER_PORT=8903
python -m uvicorn simple_server:app --host 0.0.0.0 --port %SERVER_PORT% --log-level info
pause
