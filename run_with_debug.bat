@echo off
echo Running A-MEM Server with debugging...

:: Activate virtual environment
call .venv\Scripts\activate

:: Run the debug script first
echo Running diagnostic check...
python debug_server.py

:: Pause to let user read any error messages
echo.
echo Check for any errors above and in server_debug.log
echo Press any key to continue with server startup...
pause > nul

:: Start the server with detailed error output
echo.
echo Starting server with error trapping...
python -c "import sys, traceback; try: import uvicorn; uvicorn.run('server:app', host='0.0.0.0', port=8000, log_level='debug'); except Exception as e: print(f'ERROR: {e}'); traceback.print_exc(); input('Press Enter to exit...')"

:: Keep terminal open if there was an error
pause
