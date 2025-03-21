@echo off
echo Starting A-MEM MCP Server...

:: Activate virtual environment
call .venv\Scripts\activate

:: Check if .env exists
if not exist .env (
    echo Creating default .env file...
    echo OPENAI_API_KEY=your_api_key_here > .env
    echo MODEL_NAME=all-MiniLM-L6-v2 >> .env
    echo LLM_BACKEND=openai >> .env
    echo LLM_MODEL=gpt-4 >> .env
    echo.
    echo ⚠️ Please edit the .env file to set your OpenAI API key!
    pause
    exit /b
)

:: Start the server with detailed logging
echo Starting server...
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug
