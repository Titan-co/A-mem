@echo off
echo =====================================
echo A-MEM ChromaDB Activation and Fix
echo =====================================
echo.

echo Step 1: Setting up cache directories...
python initialize_cache.py --force
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Cache setup failed!
  goto error
)
echo.

echo Step 2: Testing ChromaDB functionality...
python test_chromadb.py
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: ChromaDB test failed!
  goto error
)
echo.

echo SUCCESS! ChromaDB is now working properly.
echo.
echo You can now use the full A-MEM system with ChromaDB enabled.
echo To run the system with ChromaDB, simply do not set the DISABLE_CHROMADB environment variable.
echo.
goto end

:error
echo.
echo There were errors during ChromaDB activation.
echo Please check the logs for details.
echo.

:end
pause
