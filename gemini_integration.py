"""
Standalone Gemini Integration for QR Code Scanner
Use Google's Gemini API with QR code scanning
(Independent of MCP - can be used separately)
"""

import json
import base64
import os
import requests
from pathlib import Path
import google.generativeai as genai
from src.qr_scanner_util import QRCodeScanner


class GeminiQRScanner:
    """Integrate Gemini with QR code scanner"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini with API key
        
        Args:
            api_key: Your Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.qr_scanner = QRCodeScanner()  # Initialize QR scanner
        
        # Define QR scanner tools for Gemini
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "scan_qr_code_from_file",
                    "description": "Scan and validate QR codes in a label image file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "Path to the image file (PNG, JPG, BMP, etc.)"
                            }
                        },
                        "required": ["image_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scan_qr_code_from_base64",
                    "description": "Scan and validate QR codes from base64 encoded image",
                    "parameters": {
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
            },
            {
                "type": "function",
                "function": {
                    "name": "scan_qr_code_from_url",
                    "description": "Scan and validate QR codes from an image URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "HTTP/HTTPS URL to the image"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

    def process_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """
        Process tool calls from Gemini
        
        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
            
        Returns:
            JSON string with tool results
        """
        if tool_name == "scan_qr_code_from_file":
            result = self.qr_scanner.scan_image_file(tool_input["image_path"])
            return json.dumps(result)
        
        elif tool_name == "scan_qr_code_from_base64":
            result = self.qr_scanner.scan_image_base64(tool_input["image_base64"])
            return json.dumps(result)
        
        elif tool_name == "scan_qr_code_from_url":
            url = tool_input.get("url")
            try:
                if not url.startswith(('http://', 'https://')):
                    return json.dumps({
                        "success": False,
                        "qr_found": False,
                        "error": "URL must start with http:// or https://"
                    })
                
                headers = {'User-Agent': 'Gemini-QR-Scanner/1.0'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                image_data = base64.b64encode(response.content).decode('utf-8')
                result = self.qr_scanner.scan_image_base64(image_data)
                return json.dumps(result)
                
            except requests.exceptions.Timeout:
                return json.dumps({
                    "success": False,
                    "qr_found": False,
                    "error": "Request timeout - URL took too long to respond"
                })
            except requests.exceptions.ConnectionError:
                return json.dumps({
                    "success": False,
                    "qr_found": False,
                    "error": "Could not connect to URL"
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "qr_found": False,
                    "error": str(e)
                })
        
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def scan_with_gemini(self, user_message: str) -> str:
        """
        Use Gemini to analyze and respond to QR scanning tasks
        
        Args:
            user_message: User's request about QR code scanning
            
        Returns:
            Gemini's response
        """
        messages = [
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        # Initial request to Gemini
        response = self.model.generate_content(
            messages,
            tools=self.tools
        )
        
        # Handle tool calls in a loop
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if this is a function call
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                tool_name = function_call.name
                tool_args = {key: value for key, value in function_call.args.items()}
                
                # Execute the tool
                tool_result = self.process_tool_call(tool_name, tool_args)
                
                # Add tool result to conversation
                messages.append({
                    "role": "model",
                    "content": part
                })
                
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "function_result",
                            "id": function_call.id,
                            "result": json.loads(tool_result)
                        }
                    ]
                })
                
                # Get next response from Gemini
                response = self.model.generate_content(messages, tools=self.tools)
            else:
                # Text response - we're done
                break
        
        # Extract final text response
        if response.text:
            return response.text
        else:
            return "No response from Gemini"

    def batch_scan_with_gemini(self, image_directory: str, analysis_request: str = None) -> str:
        """
        Scan multiple QR codes in a directory with Gemini analysis
        
        Args:
            image_directory: Path to directory with images
            analysis_request: Custom analysis request (optional)
            
        Returns:
            Gemini's analysis
        """
        import os
        
        # Get all images in directory
        images = []
        for filename in os.listdir(image_directory):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                filepath = os.path.join(image_directory, filename)
                images.append(filepath)
        
        if not images:
            return "No images found in directory"
        
        # Build message for Gemini
        if analysis_request is None:
            analysis_request = "Please scan all QR codes and provide a summary"
        
        message = f"{analysis_request}\n\nImages to scan:\n"
        for img in images:
            message += f"- {img}\n"
        
        return self.scan_with_gemini(message)


# Example usage functions

def example_1_simple_scan():
    """Example: Simple QR code scan"""
    print("\n=== Example 1: Simple QR Scan ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    response = scanner.scan_with_gemini(
        "Check if the QR code in /path/to/label.jpg is scannable and tell me what it contains"
    )
    print(response)


def example_2_batch_scan():
    """Example: Batch scan multiple images"""
    print("\n=== Example 2: Batch Scan ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    response = scanner.batch_scan_with_gemini(
        "/path/to/images",
        "Scan all QR codes and provide a detailed report on which ones are readable"
    )
    print(response)


def example_3_conversation():
    """Example: Multi-turn conversation with Gemini"""
    print("\n=== Example 3: Interactive Conversation ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    
    # First request
    response1 = scanner.scan_with_gemini(
        "Scan the QR code in product-001.jpg"
    )
    print("Gemini:", response1)
    
    # Follow-up request
    response2 = scanner.scan_with_gemini(
        "Now check product-002.jpg and compare with the first one"
    )
    print("Gemini:", response2)


def example_4_with_base64():
    """Example: Scan image from base64"""
    print("\n=== Example 4: Base64 Image Scan ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    
    # Read image and convert to base64
    image_path = "/path/to/label.jpg"
    if Path(image_path).exists():
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        response = scanner.scan_with_gemini(
            f"Scan this QR code from base64 and tell me if it's readable"
        )
        print(response)
    else:
        print(f"Image not found: {image_path}")


def example_5_quality_analysis():
    """Example: Analyze QR code quality"""
    print("\n=== Example 5: QR Code Quality Analysis ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    response = scanner.scan_with_gemini(
        "Scan the QR code in label.jpg and provide a detailed quality analysis. "
        "Tell me about the contrast, clarity, size, and any damage"
    )
    print(response)


def example_6_custom_tool_integration():
    """Example: Using custom business logic with Gemini"""
    print("\n=== Example 6: Custom Business Logic ===")
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable")
        return
    
    scanner = GeminiQRScanner(api_key)
    
    # Custom prompt for specific use case
    response = scanner.scan_with_gemini(
        """I have a batch of product labels. For each one:
        1. Scan the QR code
        2. Check if it's readable
        3. Extract the product URL or ID
        4. Verify the format matches expected pattern
        
        Start with label-batch-001.jpg and process the entire batch.
        Provide a compliance report at the end."""
    )
    print(response)


if __name__ == "__main__":
    import os
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Setup Instructions:")
        print("==================")
        print("1. Get your Gemini API key from: https://ai.google.dev/")
        print("2. Set environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key'")
        print("\nThen run examples:")
        print("   python gemini_integration.py")
    else:
        print("Examples available:")
        print("==================")
        print("example_1_simple_scan() - Basic QR scanning")
        print("example_2_batch_scan() - Scan multiple images")
        print("example_3_conversation() - Multi-turn conversation")
        print("example_4_with_base64() - Base64 image scanning")
        print("example_5_quality_analysis() - QR code quality analysis")
        print("example_6_custom_tool_integration() - Custom business logic")
        print("\nRun any example: python -c 'from gemini_integration import example_1_simple_scan; example_1_simple_scan()'")
