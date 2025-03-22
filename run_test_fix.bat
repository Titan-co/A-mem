@echo off
echo =====================================
echo A-MEM Fix Verification Test
echo =====================================
echo.

rem Set environment variables to bypass LLM calls
set "DISABLE_LLM=true"
set "DISABLE_CHROMADB=true"

echo Testing memory creation directly (with LLM disabled)...
python debug_memory_creation.py --direct

if %ERRORLEVEL% EQU 0 (
  echo.
  echo SUCCESS! The fix was applied correctly.
  echo The system now properly imports the OS module.
) else (
  echo.
  echo ERROR: The test failed. Please check the logs.
)

echo.
echo Test complete!
pause
