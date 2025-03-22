@echo off
echo =====================================
echo A-MEM Fix Verification Test
echo =====================================
echo.

rem Set environment variables to bypass LLM calls
set "DISABLE_LLM=true"
set "DISABLE_CHROMADB=true"

echo Running verification script...
python verify_fix.py

if %ERRORLEVEL% EQU 0 (
  echo.
  echo SUCCESS! The fix was applied correctly.
  echo The system now properly respects the DISABLE_CHROMADB environment variable.
) else (
  echo.
  echo ERROR: The test failed. Please check the logs.
)

echo.
echo After fix verification, running the original test script for completeness...
python debug_memory_creation.py --direct

echo.
echo Testing complete!
pause
