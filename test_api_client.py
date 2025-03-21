"""
Test script for diagnosing the OpenAI API client issues
"""
import os
from dotenv import load_dotenv
import json
import traceback

# Load environment variables
load_dotenv()

def test_openai_api_connection():
    """Test the OpenAI API connection with detailed logging"""
    try:
        # Get API settings
        api_key = os.getenv("OPENAI_API_KEY")
        api_url = os.getenv("OPENAI_API_URL")
        model = os.getenv("LLM_MODEL", "gpt-4")
        
        print(f"Testing API connection:")
        print(f"API Key: {'[SET]' if api_key else '[NOT SET]'}")
        print(f"API URL: {api_url}")
        print(f"Model: {model}")
        
        # Import OpenAI
        from openai import OpenAI
        
        # Initialize client
        client_args = {"api_key": api_key}
        if api_url:
            client_args["base_url"] = api_url
            
        client = OpenAI(**client_args)
        
        # Test simple completion
        print("\n1. Testing simple completion...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=50
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response content: {response.choices[0].message.content}")
        
        # Test JSON format completion with json_object
        print("\n2. Testing JSON output with json_object format...")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You must respond with a JSON object."},
                    {"role": "user", "content": "Return a JSON with your name and role."}
                ],
                response_format={"type": "json_object"},
                max_tokens=100
            )
            
            print(f"Response type: {type(response)}")
            print(f"Response content: {response.choices[0].message.content}")
            
            # Try parsing the JSON
            try:
                json_response = json.loads(response.choices[0].message.content)
                print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Raw content: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error with json_object format: {e}")
            print(traceback.format_exc())
        
        # Alternative: Try with explicit JSON instructions
        print("\n3. Testing with explicit JSON instructions...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in JSON format."},
                {"role": "user", "content": "Return a JSON object with fields 'name' and 'role'. Format it as valid JSON."}
            ],
            max_tokens=100
        )
        
        print(f"Response content: {response.choices[0].message.content}")
        
        # Try parsing the JSON
        try:
            json_response = json.loads(response.choices[0].message.content)
            print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
        
        print("\nAPI test completed successfully!")
        return True
    except Exception as e:
        print(f"Error testing API: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("OpenAI API Client Test")
    print("=" * 50)
    
    test_openai_api_connection()
