#!/usr/bin/env python3
"""
URL Scanning Examples

Demonstrates how to scan QR codes from image URLs
"""

import json
from qr_client import QRScannerClient, quick_scan_url


def example_1_basic_url_scan():
    """Basic URL scan - single image"""
    print("\n" + "="*60)
    print("Example 1: Basic URL Scan")
    print("="*60)
    
    # Using the convenience function
    api_url = "https://your-deployment.run.app"  # Replace with actual URL
    
    # Example image URL (replace with real label image)
    label_url = "https://example.com/label.jpg"
    
    print(f"\nScanning: {label_url}")
    
    # This would be called like:
    # result = quick_scan_url(api_url, label_url)
    
    print("\nExpected result:")
    print(json.dumps({
        "success": True,
        "qr_found": True,
        "scannable": True,
        "qr_count": 1,
        "qr_codes": [
            {
                "type": "QRCODE",
                "data": "https://example.com/product",
                "scannable": True
            }
        ],
        "message": "QR code found and is scannable"
    }, indent=2))


def example_2_client_approach():
    """Using the QRScannerClient class"""
    print("\n" + "="*60)
    print("Example 2: QRScannerClient Approach")
    print("="*60)
    
    code = '''
from qr_client import QRScannerClient

# Initialize client
client = QRScannerClient("https://your-deployment.run.app")

# Scan from URL
result = client.scan_url("https://example.com/product-label.jpg")

# Check if QR is scannable
if result.get("scannable"):
    qr_data = result["qr_codes"][0]["data"]
    print(f"QR Code found: {qr_data}")
else:
    print("QR code not scannable or not found")
'''
    print(code)


def example_3_lamatic_flow():
    """How to use in Lamatic.ai flow"""
    print("\n" + "="*60)
    print("Example 3: Lamatic.ai Flow Configuration")
    print("="*60)
    
    flow_config = '''
{
  "name": "Scan Product Label QR Code",
  "description": "Takes a label image URL and checks if QR code is scannable",
  "steps": [
    {
      "id": "input_label_url",
      "type": "input",
      "prompt": "Enter the URL of the product label image",
      "input_type": "text",
      "variable_name": "label_url"
    },
    {
      "id": "scan_qr",
      "type": "tool_call",
      "tool": "scan_qr_code_from_url",
      "input_mapping": {
        "url": "${label_url}"
      },
      "variable_name": "scan_result"
    },
    {
      "id": "check_scannable",
      "type": "condition",
      "condition": "${scan_result.scannable} == true",
      "true_branch": "success_step",
      "false_branch": "failure_step"
    },
    {
      "id": "success_step",
      "type": "output",
      "message": "✓ QR code is scannable! Data: ${scan_result.qr_codes[0].data}"
    },
    {
      "id": "failure_step",
      "type": "output",
      "message": "✗ QR code not found or not scannable"
    }
  ]
}
'''
    print(flow_config)


def example_4_batch_url_scanning():
    """Batch scanning multiple URLs"""
    print("\n" + "="*60)
    print("Example 4: Batch URL Scanning")
    print("="*60)
    
    code = '''
from qr_client import QRScannerClient

client = QRScannerClient("https://your-deployment.run.app")

# Multiple label URLs to scan
label_urls = [
    "https://example.com/label1.jpg",
    "https://example.com/label2.jpg",
    "https://example.com/label3.jpg"
]

results = {}
for url in label_urls:
    result = client.scan_url(url)
    results[url] = {
        "qr_found": result.get("qr_found"),
        "scannable": result.get("scannable"),
        "qr_data": result.get("qr_codes", [{}])[0].get("data")
    }

# Summary
scannable_count = sum(1 for r in results.values() if r["scannable"])
print(f"Processed: {len(results)} URLs")
print(f"Scannable: {scannable_count}")
print(f"Success rate: {(scannable_count/len(results))*100:.1f}%")
'''
    print(code)


def example_5_error_handling():
    """Handling errors gracefully"""
    print("\n" + "="*60)
    print("Example 5: Error Handling")
    print("="*60)
    
    code = '''
from qr_client import QRScannerClient

client = QRScannerClient("https://your-deployment.run.app")

try:
    # Scan from URL
    result = client.scan_url("https://example.com/label.jpg")
    
    # Check if request was successful
    if result.get("error"):
        print(f"Error: {result['error']}")
        # Common errors:
        # - "Could not connect to URL" (503)
        # - "Request timeout" (408)
        # - "Invalid image format"
    elif result.get("success"):
        if result.get("qr_found"):
            qr_codes = result.get("qr_codes", [])
            print(f"Found {len(qr_codes)} QR code(s)")
            for qr in qr_codes:
                print(f"  - Data: {qr['data']}")
                print(f"  - Scannable: {qr.get('scannable')}")
        else:
            print("No QR code found in image")
            
except Exception as e:
    print(f"Unexpected error: {e}")
'''
    print(code)


def example_6_direct_http_request():
    """Direct HTTP request using curl"""
    print("\n" + "="*60)
    print("Example 6: Direct HTTP Request (cURL)")
    print("="*60)
    
    curl_examples = '''
# Basic scan
curl -X POST https://your-deployment.run.app/scan/url \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://example.com/label.jpg"
  }'

# With jq for pretty output
curl -X POST https://your-deployment.run.app/scan/url \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com/label.jpg"}' | jq

# Check specific field (is QR scannable?)
curl -s -X POST https://your-deployment.run.app/scan/url \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com/label.jpg"}' | jq '.scannable'

# Full response with error handling
curl -w "\\nHTTP Status: %{http_code}\\n" \\
  -X POST https://your-deployment.run.app/scan/url \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com/label.jpg"}'
'''
    print(curl_examples)


if __name__ == "__main__":
    print("\n🔗 URL SCANNING EXAMPLES")
    print("=" * 60)
    print("These examples show how to scan QR codes from image URLs")
    print("using your deployed MCP/API server")
    
    example_1_basic_url_scan()
    example_2_client_approach()
    example_3_lamatic_flow()
    example_4_batch_url_scanning()
    example_5_error_handling()
    example_6_direct_http_request()
    
    print("\n" + "="*60)
    print("✅ For more details, see: URL_SCANNING.md")
    print("=" * 60)
