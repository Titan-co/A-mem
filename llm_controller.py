from typing import Dict, Optional, Literal, Any
import os
import json
from abc import ABC, abstractmethod
from litellm import completion

class BaseLLMController(ABC):
    @abstractmethod
    def get_completion(self, prompt: str) -> str:
        """Get completion from LLM"""
        pass

class OpenAIController(BaseLLMController):
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, api_base: Optional[str] = None):
        try:
            from openai import OpenAI
            self.model = model
            if api_key is None:
                api_key = os.getenv('OPENAI_API_KEY')
            if api_key is None:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            # Initialize with custom base URL if provided
            client_kwargs = {"api_key": api_key}
            if api_base and api_base.strip():
                client_kwargs["base_url"] = api_base
                print(f"Using custom API base URL: {api_base}")
                
            self.client = OpenAI(**client_kwargs)
            # Store the API base for future reference
            self.using_custom_api = bool(api_base and api_base.strip())
        except ImportError:
            raise ImportError("OpenAI package not found. Install it with: pip install openai")
    
    def get_completion(self, prompt: str, response_format: dict, temperature: float = 0.7) -> str:
        try:
            # For custom API endpoints, we might need to use a different approach
            # Some providers don't fully support response_format, so add explicit instructions
            system_message = "You must respond with a JSON object."
            if self.using_custom_api:
                system_message += " Return only the raw JSON with no Markdown formatting, no code blocks, and no backticks."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_format,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            # If response_format causes issues with some providers, try without it
            if self.using_custom_api:
                print(f"Error with response_format: {e}. Trying without it...")
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You must respond with a raw JSON object. No Markdown formatting, no code blocks, no backticks."},
                            {"role": "user", "content": prompt + "\n\nIMPORTANT: Return only the raw JSON with no Markdown formatting or code blocks."}
                        ],
                        temperature=temperature,
                        max_tokens=1000
                    )
                    return response.choices[0].message.content
                except Exception as inner_e:
                    print(f"Also failed without response_format: {inner_e}")
                    raise
            else:
                raise

class OllamaController(BaseLLMController):
    def __init__(self, model: str = "llama2"):
        from ollama import chat
        self.model = model
    
    def _generate_empty_value(self, schema_type: str, schema_items: dict = None) -> Any:
        if schema_type == "array":
            return []
        elif schema_type == "string":
            return ""
        elif schema_type == "object":
            return {}
        elif schema_type == "number":
            return 0
        elif schema_type == "boolean":
            return False
        return None

    def _generate_empty_response(self, response_format: dict) -> dict:
        """Generate an empty response based on the response format"""
        if response_format.get("type") == "json_object":
            return {}
            
        # Fallback for older json_schema format
        if "json_schema" in response_format:
            schema = response_format["json_schema"]["schema"]
            result = {}
            
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    result[prop_name] = self._generate_empty_value(prop_schema["type"], 
                                                                prop_schema.get("items"))
            
        return {}
        
    def _clean_response(self, response: str) -> str:
        """Clean the response text by removing Markdown formatting.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Cleaned response text
        """
        # Import here to avoid circular imports
        from memory_system import strip_markdown_code_fences
        return strip_markdown_code_fences(response)

    def get_completion(self, prompt: str, response_format: dict, temperature: float = 0.7) -> str:
        try:
            # Add explicit instructions to avoid Markdown
            enhanced_prompt = prompt + "\n\nRETURN RAW JSON ONLY. NO MARKDOWN CODE BLOCKS OR BACKTICKS."
            
            response = completion(
                model="ollama_chat/{}".format(self.model),
                messages=[
                    {"role": "system", "content": "You must respond with a JSON object. Do not use Markdown formatting, code blocks, or backticks in your response."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                response_format=response_format,
            )
            
            # Clean response to remove any Markdown or code fences
            raw_response = response.choices[0].message.content
            return self._clean_response(raw_response)
        except Exception as e:
            print(f"Error in OllamaController: {e}")
            # Try to generate a default response
            empty_response = self._generate_empty_response(response_format)
            return json.dumps(empty_response)

class LLMController:
    """LLM-based controller for memory metadata generation"""
    def __init__(self, 
                 backend: Literal["openai", "ollama"] = "openai",
                 model: str = "gpt-4", 
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None):
        if backend == "openai":
            self.llm = OpenAIController(model, api_key, api_base)
        elif backend == "ollama":
            self.llm = OllamaController(model)
        else:
            raise ValueError("Backend must be one of: 'openai', 'ollama'")
            
    def get_completion(self, prompt: str, response_format: dict = None, temperature: float = 0.7) -> str:
        return self.llm.get_completion(prompt, response_format, temperature)
