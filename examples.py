"""
Example usage of the QR Code Scanner MCP Server
"""

import asyncio
import json
from src.server import qr_scanner


async def example_1_scan_file():
    """Example: Scan a QR code from a file"""
    print("\n=== Example 1: Scanning from File ===")
    
    # This would be your actual image path
    image_path = "path/to/your/label.jpg"
    
    result = qr_scanner.scan_image_file(image_path)
    print(json.dumps(result, indent=2))


async def example_2_scan_base64():
    """Example: Scan a QR code from base64"""
    print("\n=== Example 2: Scanning from Base64 ===")
    
    # Read an image file and convert to base64
    import base64
    
    image_path = "path/to/your/label.jpg"
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        result = qr_scanner.scan_image_base64(image_base64)
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")


async def example_3_claude_integration():
    """Example: Integration with Claude API"""
    print("\n=== Example 3: Claude Integration ===")
    
    example_code = """
from anthropic import Anthropic

client = Anthropic()

# Define the QR scanner tools
tools = [
    {
        "name": "scan_qr_code_from_file",
        "description": "Scan and check if QR codes in a label image are scannable",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file"
                }
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "scan_qr_code_from_base64",
        "description": "Scan QR codes from base64 encoded image",
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

# Use with Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "Please check if the QR code in /path/to/label.jpg is scannable"
        }
    ]
)

print(response)
    """
    print(example_code)


async def example_4_llamaindex_integration():
    """Example: Integration with LlamaIndex"""
    print("\n=== Example 4: LlamaIndex Integration ===")
    
    example_code = """
from llama_index.tools import MCP
from llama_index.agent import AgentRunner
from llama_index.llms import OpenAI

# Initialize the QR scanner MCP
qr_scanner = MCP(
    server_path="python",
    server_args=["-m", "src.server"]
)

# Create an agent
llm = OpenAI(model="gpt-4")
agent = AgentRunner.from_llm(
    llm=llm,
    tools=[qr_scanner]
)

# Use the agent
response = agent.chat(
    "Check if the QR code in /path/to/label.jpg is scannable"
)
print(response)
    """
    print(example_code)


async def main():
    """Run all examples"""
    print("=" * 50)
    print("QR Code Scanner MCP - Usage Examples")
    print("=" * 50)
    
    await example_1_scan_file()
    await example_2_scan_base64()
    await example_3_claude_integration()
    await example_4_llamaindex_integration()
    
    print("\n" + "=" * 50)
    print("For more information, see README.md")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
