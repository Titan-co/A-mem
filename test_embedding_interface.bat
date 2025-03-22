@echo off
echo =====================================
echo A-MEM Embedding Interface Test
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

echo Testing embedding function interface...
python test_embedding_interface.py

if %ERRORLEVEL% EQU 0 (
  echo.
  echo SUCCESS! The embedding functions now match ChromaDB's expected interface.
  echo You can now try using the standard implementation.
) else (
  echo.
  echo ERROR: The embedding interface test failed.
  echo Check embedding_test.log for details.
)

echo.
pause
