@echo off
echo Installing dependencies for A-MEM...
pip install -r requirements.txt
pip install python-dotenv pydantic-settings fastapi uvicorn
echo Installing NLTK data...
python -c "import nltk; nltk.download('punkt')"
echo Dependencies installation complete.
pause
