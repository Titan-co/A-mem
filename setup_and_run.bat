@echo off
echo Setting up A-MEM Server
echo =======================

echo Installing required packages...
python -m pip install fastapi uvicorn pydantic-settings python-dotenv sentence-transformers chromadb rank_bm25 nltk transformers litellm numpy scikit-learn openai

echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt')"

echo Starting A-MEM Server...
python -m uvicorn server:app --host 0.0.0.0 --port 8000
