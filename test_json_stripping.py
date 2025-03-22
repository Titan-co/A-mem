"""
Test the JSON stripping function to ensure it works with different Markdown formats.
"""
import json
import sys
from memory_system import strip_markdown_code_fences

def test_markdown_json_stripping():
    """Test if our strip_markdown_code_fences function works properly"""
    print("\nTesting Markdown code fence stripping...")
    
    test_cases = [
        # Triple backticks multiline
        """```json
{"name": "test", "value": 123}
```""",
        
        # Triple backticks single line
        """```json {"name": "test", "value": 123}```""",
        
        # Single backticks
        """`json {"name": "test", "value": 123}`""",
        
        # Double backticks (rare but possible)
        """``json {"name": "test", "value": 123}``""",
        
        # Normal JSON (no backticks)
        """{"name": "test", "value": 123}""",
        
        # Real-world example from API response
        """```json { "name": "Assistant", "role": "AI" } ```"""
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\nTest case {i+1}:")
        print(f"Original: {case}")
        
        cleaned = strip_markdown_code_fences(case)
        print(f"Cleaned: {cleaned}")
        
        # Try to parse it
        try:
            parsed = json.loads(cleaned)
            print(f"✓ Successfully parsed JSON: {parsed}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON parse error: {e}")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Testing JSON Markdown Stripping Function")
    print("=" * 50)
    
    test_markdown_json_stripping()
