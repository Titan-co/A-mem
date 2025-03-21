@echo off
echo Installing required packages for A-MEM MCP Server...
echo.

echo Installing FastAPI and dependencies...
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv

echo.
echo Installing required packages from requirements.txt...
pip install -r requirements.txt

echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt')"

echo.
echo Setup complete! You can now run the server using the Claude Desktop.
echo.
pause
