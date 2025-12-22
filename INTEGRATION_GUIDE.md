# Integration Guide: QR Code Scanner MCP with LlamaIndex/Claude

## Overview

This guide explains how to integrate the QR Code Scanner MCP server with LlamaIndex and Claude AI.

## Quick Start

### 1. Start the MCP Server

```bash
cd qr_code_scanner
python -m src.server
```

The server will be ready to accept requests on localhost (or your deployment URL).

## Integration with Claude (via Claude API)

### Using Claude with Tool Calls

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define the QR scanner tool schema
tools = [
    {
        "name": "scan_qr_code_from_file",
        "description": "Scan a QR code from a label image and check if it's scannable",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "File path to the label image (PNG, JPG, etc.)"
                }
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "scan_qr_code_from_base64",
        "description": "Scan a QR code from a base64-encoded image",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64 encoded image data"
                }
            },
            "required": ["image_base64"]
        }
    }
]

# Create a message with Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "Please check if the QR code in my label image at /labels/product-001.jpg is scannable"
        }
    ]
)

print(response)

# Handle tool use in response
for block in response.content:
    if block.type == "tool_use":
        if block.name == "scan_qr_code_from_file":
            # Call your QR scanner
            from src.server import qr_scanner
            result = qr_scanner.scan_image_file(block.input["image_path"])
            print(json.dumps(result, indent=2))
```

### Conversation Loop with Claude

```python
from anthropic import Anthropic
import json
from src.server import qr_scanner

client = Anthropic()

def process_tool_call(tool_name, tool_input):
    """Process tool calls from Claude"""
    if tool_name == "scan_qr_code_from_file":
        return qr_scanner.scan_image_file(tool_input["image_path"])
    elif tool_name == "scan_qr_code_from_base64":
        return qr_scanner.scan_image_base64(tool_input["image_base64"])
    return {"error": "Unknown tool"}

def chat_with_qr_scanner(user_message):
    """Chat with Claude about QR codes"""
    messages = [{"role": "user", "content": user_message}]
    
    tools = [
        {
            "name": "scan_qr_code_from_file",
            "description": "Scan QR code from image file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"}
                },
                "required": ["image_path"]
            }
        },
        {
            "name": "scan_qr_code_from_base64",
            "description": "Scan QR code from base64 image",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_base64": {"type": "string"}
                },
                "required": ["image_base64"]
            }
        }
    ]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # Check if we need to handle tool calls
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            
            # Add assistant response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # No more tool calls, return final response
            return response.content[0].text

# Usage
result = chat_with_qr_scanner(
    "Check if the QR code in /labels/sample.jpg is scannable and tell me what it contains"
)
print(result)
```

## Integration with LlamaIndex

### Using as a Tool in LlamaIndex Agent

```python
from llama_index.agent import AgentRunner
from llama_index.llms import OpenAI
from llama_index.tools import FunctionTool
import json
from src.server import qr_scanner

# Create function tools
def scan_qr_from_file(image_path: str) -> str:
    """Scan QR code from image file"""
    result = qr_scanner.scan_image_file(image_path)
    return json.dumps(result)

def scan_qr_from_base64(image_base64: str) -> str:
    """Scan QR code from base64 image"""
    result = qr_scanner.scan_image_base64(image_base64)
    return json.dumps(result)

# Create tools
file_tool = FunctionTool.from_defaults(
    fn=scan_qr_from_file,
    name="scan_qr_from_file",
    description="Scan QR code from a label image file"
)

base64_tool = FunctionTool.from_defaults(
    fn=scan_qr_from_base64,
    name="scan_qr_from_base64",
    description="Scan QR code from base64 encoded image"
)

# Create agent
llm = OpenAI(model="gpt-4")
agent = AgentRunner.from_llm(
    llm=llm,
    tools=[file_tool, base64_tool],
    verbose=True
)

# Use agent
response = agent.chat(
    "Check the QR code in /labels/product-001.jpg and tell me if it's scannable"
)
print(response)
```

### Advanced LlamaIndex Integration with Workflow

```python
from llama_index.workflows import Workflow, StartEvent, StopEvent
from llama_index.llms import OpenAI
import json
from src.server import qr_scanner

class QRCodeScanningWorkflow(Workflow):
    """Workflow for processing and analyzing QR codes"""
    
    def __init__(self):
        super().__init__()
        self.llm = OpenAI(model="gpt-4")
    
    @staticmethod
    def scan_qr_code(image_path: str) -> dict:
        """Scan QR code from image"""
        return qr_scanner.scan_image_file(image_path)
    
    async def analyze_qr_result(self, result: dict) -> str:
        """Analyze QR code scanning result with LLM"""
        
        if result.get("scannable"):
            message = f"QR code found with content: {result['qr_codes'][0]['content']}"
        else:
            message = "No scannable QR code found in image"
        
        # Get LLM analysis
        response = await self.llm.acomplete(
            f"Analyze this QR code scan result: {json.dumps(result)}. "
            "Provide insights about the QR code quality and readability."
        )
        
        return response

# Usage
async def main():
    workflow = QRCodeScanningWorkflow()
    result = workflow.scan_qr_code("/labels/product-001.jpg")
    analysis = await workflow.analyze_qr_result(result)
    print(analysis)

import asyncio
asyncio.run(main())
```

## Batch Processing Multiple Images

```python
import os
import base64
import json
from src.server import qr_scanner
from anthropic import Anthropic

def batch_scan_images(image_directory: str) -> list:
    """Scan all images in a directory"""
    results = []
    
    for filename in os.listdir(image_directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            filepath = os.path.join(image_directory, filename)
            result = qr_scanner.scan_image_file(filepath)
            results.append({
                "filename": filename,
                "scan_result": result
            })
    
    return results

def analyze_batch_results(results: list, client: Anthropic) -> str:
    """Use Claude to analyze batch scanning results"""
    
    summary = f"Scanned {len(results)} images. Results:\n"
    for result in results:
        summary += f"- {result['filename']}: "
        if result['scan_result']['qr_found']:
            summary += f"QR code found and scannable"
        else:
            summary += f"No scannable QR code"
        summary += "\n"
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Analyze these QR code scan results and provide a summary:\n{summary}"
            }
        ]
    )
    
    return response.content[0].text

# Usage
from anthropic import Anthropic
results = batch_scan_images("/labels")
client = Anthropic()
analysis = analyze_batch_results(results, client)
print(analysis)
```

## Error Handling & Validation

```python
import json
from typing import Optional
from src.server import qr_scanner

def safe_scan_with_validation(
    image_path: str,
    max_retries: int = 3
) -> Optional[dict]:
    """Safely scan with validation and retry logic"""
    
    for attempt in range(max_retries):
        try:
            result = qr_scanner.scan_image_file(image_path)
            
            # Validate response
            if not isinstance(result, dict):
                print(f"Attempt {attempt + 1}: Invalid response type")
                continue
            
            if result.get('success') is False:
                print(f"Attempt {attempt + 1}: Scan failed - {result.get('error')}")
                continue
            
            return result
            
        except Exception as e:
            print(f"Attempt {attempt + 1}: Exception - {str(e)}")
            continue
    
    return None

# Usage with Claude integration
def robust_qr_check_with_claude(image_path: str) -> str:
    from anthropic import Anthropic
    
    client = Anthropic()
    scan_result = safe_scan_with_validation(image_path)
    
    if scan_result is None:
        return "Failed to scan QR code after multiple attempts"
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": f"Provide a summary of this QR code scan: {json.dumps(scan_result)}"
            }
        ]
    )
    
    return response.content[0].text
```

## Environment Setup for Integration

```bash
# Install required packages
pip install anthropic
pip install llama-index
pip install llama-index-llms-openai

# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# For LlamaIndex
export LLAMA_INDEX_LOG_LEVEL="info"
```

## Troubleshooting Integration

### Issue: Import errors
```bash
pip install --upgrade anthropic llama-index
```

### Issue: Tool not being called
- Ensure tool schema is correct
- Verify tool names match exactly
- Check that model supports tool use

### Issue: Slow responses
- Use smaller images
- Implement caching
- Use async operations

## Next Steps

1. Deploy the MCP server to your cloud platform
2. Configure Claude API keys
3. Set up LlamaIndex agents
4. Implement monitoring and logging
5. Test with your label images

For more details, see [DEPLOYMENT.md](DEPLOYMENT.md) and [README.md](README.md).
