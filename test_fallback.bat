@echo off
echo =====================================
echo A-MEM Fallback Implementation Test
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

echo Testing fallback ChromaDB implementation...
python test_fallback_implementation.py

if %ERRORLEVEL% EQU 0 (
  echo.
  echo SUCCESS! The fallback implementation is working correctly.
  echo You can use the run_with_fallback.bat script to start the server.
) else (
  echo.
  echo ERROR: The fallback implementation test failed.
  echo Check fallback_test.log for details.
)

echo.
pause
