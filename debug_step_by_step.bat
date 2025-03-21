@echo off
echo A-MEM Server Debugging - Step by Step
echo ====================================
echo.

:: Activate virtual environment
call .venv\Scripts\activate

:: Step 1: Check dependencies
echo Step 1: Checking dependencies...
python check_dependencies.py
echo.
echo Press any key to continue to step 2...
pause > nul

:: Step 2: Test imports
echo.
echo Step 2: Testing imports...
python test_imports.py
echo.
echo Press any key to continue to step 3...
pause > nul

:: Step 3: Inspect server
echo.
echo Step 3: Inspecting server.py...
python inspect_server.py
echo.
echo Press any key to continue to step 4...
pause > nul

:: Step 4: Try minimal server
echo.
echo Step 4: Testing minimal server...
echo This will start a minimal FastAPI server on port 8001.
echo Access http://localhost:8001/ in your browser to test it.
echo Press Ctrl+C to stop the server once you've verified it works.
echo.
echo Press any key to start the minimal server...
pause > nul
python minimal_server.py
echo.
echo Press any key to continue to step 5...
pause > nul

:: Step 5: Run the debug server
echo.
echo Step 5: Running server with debugging...
echo This will log detailed information to server_debug.log.
echo.
echo Press any key to start the debug server...
pause > nul
python debug_server.py

:: Keep terminal open
echo.
echo Debugging process complete.
echo Check server_debug.log for detailed information.
echo.
pause
