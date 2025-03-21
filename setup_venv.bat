@echo off
echo Creating virtual environment for A-MEM MCP Server...

:: Create virtual environment
python -m venv .venv
call .venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Install additional dependencies
pip install python-dotenv pydantic-settings fastapi uvicorn

:: Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt')"

echo Setup complete! You can now run the server with run_server.bat
echo.
pause
