# Gemini Integration Guide

Quick guide to use QR Code Scanner MCP with Google Gemini API.

## Setup

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key
4. Copy your API key

### 2. Install Gemini Package

```bash
pip install google-generativeai
```

### 3. Set Environment Variable

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

**macOS/Linux:**
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

## Quick Start

### Example 1: Simple QR Code Scan

```python
from gemini_integration import GeminiQRScanner
import os

api_key = os.getenv("GOOGLE_API_KEY")
scanner = GeminiQRScanner(api_key)

response = scanner.scan_with_gemini(
    "Check if the QR code in product-001.jpg is scannable"
)
print(response)
```

**Output:**
```
The QR code in product-001.jpg is scannable. It contains a URL: https://example.com/product/001
```

### Example 2: Batch Process Multiple Images

```python
from gemini_integration import GeminiQRScanner
import os

api_key = os.getenv("GOOGLE_API_KEY")
scanner = GeminiQRScanner(api_key)

response = scanner.batch_scan_with_gemini(
    "/path/to/label/images",
    "Scan all QR codes and provide a quality report"
)
print(response)
```

### Example 3: Quality Analysis

```python
from gemini_integration import GeminiQRScanner
import os

api_key = os.getenv("GOOGLE_API_KEY")
scanner = GeminiQRScanner(api_key)

response = scanner.scan_with_gemini(
    "Scan the QR code and analyze its quality. "
    "Rate the contrast, clarity, and readability."
)
print(response)
```

## API Reference

### GeminiQRScanner Class

#### `__init__(api_key: str)`
Initialize the scanner with your Gemini API key.

```python
scanner = GeminiQRScanner(api_key)
```

#### `scan_with_gemini(user_message: str) -> str`
Send a request to Gemini with QR scanning capability.

```python
response = scanner.scan_with_gemini(
    "Check the QR code in my-label.jpg"
)
```

**Parameters:**
- `user_message` (str): Your request about QR code scanning

**Returns:**
- `str`: Gemini's response with QR scan results and analysis

#### `batch_scan_with_gemini(image_directory: str, analysis_request: str = None) -> str`
Scan all images in a directory.

```python
response = scanner.batch_scan_with_gemini(
    "/path/to/images",
    "Analyze all QR codes for quality"
)
```

**Parameters:**
- `image_directory` (str): Path to directory with images
- `analysis_request` (str, optional): Custom analysis request

**Returns:**
- `str`: Gemini's analysis of all QR codes

#### `process_tool_call(tool_name: str, tool_input: dict) -> str`
Manually process a tool call (advanced).

```python
result = scanner.process_tool_call(
    "scan_qr_code_from_file",
    {"image_path": "/path/to/image.jpg"}
)
```

## Advanced Usage

### Custom Analysis Prompts

```python
from gemini_integration import GeminiQRScanner
import os

api_key = os.getenv("GOOGLE_API_KEY")
scanner = GeminiQRScanner(api_key)

# Compliance check
response = scanner.scan_with_gemini(
    """Scan the QR codes in these product labels:
    - label-001.jpg
    - label-002.jpg
    - label-003.jpg
    
    For each code:
    1. Verify it's scannable
    2. Extract the product ID
    3. Check if ID matches expected format: PROD-XXXX
    4. Flag any issues
    
    Provide a compliance report."""
)
print(response)
```

### Error Handling

```python
from gemini_integration import GeminiQRScanner
import os

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    
    scanner = GeminiQRScanner(api_key)
    response = scanner.scan_with_gemini("Scan my-image.jpg")
    print(response)
    
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### Processing from Base64

```python
from gemini_integration import GeminiQRScanner
import os
import base64

api_key = os.getenv("GOOGLE_API_KEY")
scanner = GeminiQRScanner(api_key)

# Convert image to base64
with open("label.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# Use in prompt
response = scanner.scan_with_gemini(
    f"I have a base64 encoded image. Scan the QR code in it."
)
print(response)
```

## Comparison: Gemini vs Claude vs LlamaIndex

| Feature | Gemini | Claude | LlamaIndex |
|---------|--------|--------|-----------|
| QR Scanning | ✅ Yes | ✅ Yes | ✅ Yes |
| Tool Calling | ✅ Yes | ✅ Yes | ✅ Yes |
| Free Tier | ✅ Yes | ❌ No | ✅ Yes |
| Batch Processing | ✅ Easy | ✅ Yes | ✅ Yes |
| Custom Tools | ✅ Yes | ✅ Yes | ✅ Yes |
| Setup Complexity | Low | Low | Medium |

## Troubleshooting

### "Error: No API key provided"
```bash
export GOOGLE_API_KEY='your-key'
python your_script.py
```

### "ImportError: No module named google"
```bash
pip install google-generativeai
```

### "Tool call failed"
Ensure:
1. Image path is correct
2. Image format is supported (PNG, JPG, BMP)
3. QR code is visible in image

### Rate Limiting
Gemini has rate limits. If you hit them:
- Wait a few seconds before retrying
- Use batch processing efficiently
- Check your quota at [Google AI Studio](https://ai.google.dev/)

## Best Practices

1. **Error Handling**: Always wrap calls in try-except
2. **Rate Limiting**: Implement delays between batch operations
3. **Image Quality**: Ensure images have good lighting and contrast
4. **API Key Security**: Never commit API keys to version control
5. **Caching**: Cache results for repeated scans

## Complete Example

```python
import os
import json
from gemini_integration import GeminiQRScanner

def process_product_batch():
    """Complete example: Process product labels"""
    
    # Initialize
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY")
        return
    
    scanner = GeminiQRScanner(api_key)
    
    # Scan and analyze
    response = scanner.scan_with_gemini(
        """Process these product labels:
        1. Scan all QR codes
        2. Extract product IDs
        3. Verify scannability
        4. Generate compliance report
        
        Start with products/batch-1/"""
    )
    
    # Parse and use results
    print("Report:")
    print(response)
    
    # Save results
    with open("qr_scan_results.json", "w") as f:
        json.dump({"status": "completed", "report": response}, f)

if __name__ == "__main__":
    process_product_batch()
```

## Next Steps

1. ✅ Set up your API key
2. ✅ Test simple example
3. ✅ Integrate into your workflow
4. ✅ Scale to batch processing
5. ✅ Deploy to production

## Support

- Gemini Documentation: https://ai.google.dev/
- MCP Documentation: https://modelcontextprotocol.io/
- Issues: Check logs and error messages

## API Limits

Free tier rates (as of 2025):
- 15 requests per minute
- 1 million tokens per month
- Batch size: No limit

For higher limits, upgrade your plan.
