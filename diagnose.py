import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Module search paths: {sys.path}")

try:
    import server
    print("Successfully imported server module")
except ImportError as e:
    print(f"Error importing server module: {e}")

try:
    import nltk
    print("Successfully imported nltk")
except ImportError as e:
    print(f"Error importing nltk: {e}")

try:
    import fastapi
    print("Successfully imported fastapi")
except ImportError as e:
    print(f"Error importing fastapi: {e}")

try:
    import uvicorn
    print("Successfully imported uvicorn")
except ImportError as e:
    print(f"Error importing uvicorn: {e}")

try:
    import openai
    print("Successfully imported openai")
except ImportError as e:
    print(f"Error importing openai: {e}")

# Try to find the server.py file
server_path = os.path.join(os.getcwd(), "server.py")
print(f"Does server.py exist? {os.path.exists(server_path)}")
