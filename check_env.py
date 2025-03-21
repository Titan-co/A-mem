import os
from dotenv import load_dotenv

def main():
    # Load .env file
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    api_url = os.getenv("OPENAI_API_URL")
    
    print("Environment Variables:")
    print(f"OPENAI_API_KEY: {'[SET]' if api_key else '[NOT SET]'}")
    if api_key:
        masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "[TOO SHORT]"
        print(f"  Length: {len(api_key)} chars")
        print(f"  Value: {masked_key}")
    
    print(f"OPENAI_API_URL: {'[SET]' if api_url else '[NOT SET]'}")
    if api_url:
        print(f"  Value: {api_url}")
    
    # Check other environment variables
    print("\nOther Environment Variables:")
    for key, value in os.environ.items():
        if key.startswith("OPENAI_") and key not in ["OPENAI_API_KEY", "OPENAI_API_URL"]:
            masked_value = value[:3] + "..." + value[-3:] if len(value) > 6 else value
            print(f"{key}: {masked_value}")
    
    # Check config settings
    try:
        from config import settings
        print("\nConfig Settings:")
        print(f"MODEL_NAME: {settings.MODEL_NAME}")
        print(f"LLM_BACKEND: {settings.LLM_BACKEND}")
        print(f"LLM_MODEL: {settings.LLM_MODEL}")
        print(f"API_KEY: {'[SET]' if settings.API_KEY else '[NOT SET]'}")
        if settings.API_KEY:
            masked_key = settings.API_KEY[:6] + "..." + settings.API_KEY[-4:] if len(settings.API_KEY) > 10 else "[TOO SHORT]"
            print(f"  Length: {len(settings.API_KEY)} chars")
            print(f"  Value: {masked_key}")
        
        print(f"API_URL: {'[SET]' if settings.API_URL else '[NOT SET]'}")
        if settings.API_URL:
            print(f"  Value: {settings.API_URL}")
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    # Create a simple OpenAI client to test the API key
    try:
        from openai import OpenAI
        
        # Test without API URL
        print("\nTesting OpenAI API Key (Standard OpenAI API):")
        try:
            client = OpenAI(api_key=api_key)
            response = client.models.list()
            print("  API Key works with standard OpenAI API!")
            print(f"  Available models: {len(response.data)}")
        except Exception as e:
            print(f"  Error with standard OpenAI API: {e}")
        
        # Test with API URL if provided
        if api_url:
            print("\nTesting OpenAI API Key with custom API URL:")
            try:
                client = OpenAI(api_key=api_key, base_url=api_url)
                response = client.models.list()
                print("  API Key works with custom API URL!")
                print(f"  Available models: {len(response.data)}")
            except Exception as e:
                print(f"  Error with custom API URL: {e}")
    except ImportError:
        print("OpenAI package not installed")

if __name__ == "__main__":
    main()
