@echo off
echo =====================================
echo A-MEM Server - Standard Implementation
echo =====================================
echo.

rem Initialize cache directories
echo Initializing cache directories...
python initialize_cache.py
echo.

rem Modify chromadb_config.py to use standard implementation
echo Updating ChromaDB configuration...
echo # Auto-generated ChromaDB configuration> chromadb_config.py
echo # Generated on %date% %time%>> chromadb_config.py
echo.>> chromadb_config.py
echo # Using Standard Implementation>> chromadb_config.py
echo USE_DIRECT_EMBEDDING=True>> chromadb_config.py
echo USE_MONKEY_PATCH=False>> chromadb_config.py
echo USE_FALLBACK=False>> chromadb_config.py
echo.

rem Get port from .env file or use default
set PORT=8903
for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr /i "PORT="') do (
  set PORT=%%b
)
echo Using port: %PORT%
echo.

echo Starting server with standard implementation...
echo This implementation uses ChromaDB with custom embedding functions.
echo.

echo Press Ctrl+C to stop the server.
echo.

rem Set custom environment variables
set "PYTHONPATH=%cd%;%PYTHONPATH%"
set "CHROMADB_CACHE_DIR=%cd%\.cache"

rem Start server with standard implementation
python -m uvicorn simple_server:app --host 0.0.0.0 --port %PORT% --log-level info

echo.
echo Server stopped.
pause
