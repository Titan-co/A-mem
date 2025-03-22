# Using A-MEM with Alternative API Providers

This document explains how to use the A-MEM system with alternative API providers like OpenRouter that return JSON responses in Markdown format.

## Background

When using alternative API providers (like OpenRouter or Anthropic Claude through API gateways), the JSON responses may be wrapped in Markdown code blocks like:

```
`json { "name": "Assistant", "role": "AI" }`
```

or

```
```json
{
  "name": "Assistant",
  "role": "AI"
}
```
```

This causes JSON parsing errors in the standard implementation. We've enhanced the code to handle these cases.

## Changes Made

1. **Enhanced Markdown Stripping**: We've improved the `strip_markdown_code_fences` function to handle various Markdown code block formats:
   - Triple backticks with multiline JSON
   - Triple backticks with single line JSON
   - Single backticks with JSON
   - Double backticks with JSON

2. **Robust API Controller**: The `OpenAIController` now:
   - Detects when a custom API base URL is used
   - Adds explicit instructions to avoid Markdown in responses
   - Has fallback handling when `response_format` isn't fully supported

3. **Enhanced JSON Extraction**: We've added an `_extract_best_json` method that tries multiple approaches to extract valid JSON:
   - Direct parsing
   - Regex-based extraction with increasing permissiveness
   - Fallback to default values when all else fails

4. **Safer Memory Evolution**: The `_process_memory_evolution` method now:
   - Adds explicit instructions to avoid Markdown
   - Uses the same enhanced JSON parsing
   - Has safe fallbacks for all fields with type checking

5. **Testing Tools**: We've added:
   - A test script for the Markdown stripping function
   - A batch file to run the test

## Configuration

When using alternative API providers:

1. Set the `OPENAI_API_URL` in your `.env` file:
   ```
   OPENAI_API_URL=https://openrouter.ai/api/v1/
   ```

2. Set your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Select a compatible model in your `.env`:
   ```
   LLM_MODEL=anthropic/claude-3-haiku-20240307
   ```

## Testing

Run the test script to ensure proper JSON parsing:

```
test_stripping.bat
```

This will verify that the system can handle different Markdown code block formats and extract valid JSON.
