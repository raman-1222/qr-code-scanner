import base64
import json
import logging
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .qr_scanner_util import QRCodeScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("qr-code-scanner")

# Initialize QR code scanner
qr_scanner = QRCodeScanner()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    """Handle tool calls"""
    
    if name == "scan_qr_code_from_file":
        image_path = arguments.get("image_path")
        if not image_path:
            return json.dumps({"error": "image_path is required"})

        result = qr_scanner.scan_image_file(image_path)
        return json.dumps(result, indent=2)

    elif name == "scan_qr_code_from_base64":
        image_base64 = arguments.get("image_base64")
        if not image_base64:
            return json.dumps({"error": "image_base64 is required"})

        result = qr_scanner.scan_image_base64(image_base64)
        return json.dumps(result, indent=2)

    elif name == "scan_qr_code_from_url":
        url = arguments.get("url")
        if not url:
            return json.dumps({"error": "url is required"})
        
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return json.dumps({
                    "success": False,
                    "qr_found": False,
                    "error": "URL must start with http:// or https://"
                })
            
            # Download image with timeout
            headers = {'User-Agent': 'QR-Code-Scanner-MCP/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Convert to base64 and scan
            image_data = base64.b64encode(response.content).decode('utf-8')
            result = qr_scanner.scan_image_base64(image_data)
            return json.dumps(result, indent=2)
            
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
        except requests.exceptions.HTTPError as e:
            return json.dumps({
                "success": False,
                "qr_found": False,
                "error": f"HTTP error: {e.response.status_code}"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "qr_found": False,
                "error": f"Error downloading/scanning URL: {str(e)}"
            })

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="scan_qr_code_from_file",
            description="Scan and validate QR codes in a label image file. Returns whether a QR code is present and if it's scannable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file (supports PNG, JPG, BMP, etc.)",
                    }
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="scan_qr_code_from_base64",
            description="Scan and validate QR codes in a base64 encoded image. Returns whether a QR code is present and if it's scannable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_base64": {
                        "type": "string",
                        "description": "Base64 encoded image data (PNG, JPG, BMP, etc.)",
                    }
                },
                "required": ["image_base64"],
            },
        ),
        Tool(
            name="scan_qr_code_from_url",
            description="Scan and validate QR codes from an image URL. Downloads the image and analyzes it for QR codes. Supports HTTP and HTTPS URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "HTTP/HTTPS URL to the image (PNG, JPG, BMP, etc.)",
                    }
                },
                "required": ["url"],
            },
        ),
    ]


async def main():
    """Run the MCP server"""
    logger.info("QR Code Scanner MCP Server started")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
