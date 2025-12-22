# URL Image Scanning - Complete Guide

Now you can scan QR codes directly from image URLs without uploading files!

## Quick Start

### Using the HTTP API

```bash
curl -X POST https://your-api.run.app/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/label.jpg"}'
```

### Using Python Client

```python
from qr_client import QRScannerClient

client = QRScannerClient("https://your-api.run.app")
result = client.scan_url("https://example.com/label.jpg")

print(result)
# {
#   "success": true,
#   "qr_found": true,
#   "scannable": true,
#   "qr_count": 1,
#   "qr_codes": ["https://example.com"],
#   "message": "QR code found and is scannable"
# }
```

Or use the quick function:

```python
from qr_client import quick_scan_url

result = quick_scan_url(
    "https://your-api.run.app",
    "https://example.com/label.jpg"
)
```

## Supported URL Formats

✅ **HTTP URLs:** `http://example.com/image.jpg`  
✅ **HTTPS URLs:** `https://example.com/image.jpg`  
✅ **Image Formats:** PNG, JPG, JPEG, BMP, GIF, WEBP  
✅ **Large Files:** Images up to 100MB supported (network dependent)  
✅ **Redirects:** Automatic redirect following  

## Lamatic.ai Integration

### In a Lamatic Flow

**1. Set Up MCP**
- Connect MCP server with URL support enabled
- Configure Host URL: `https://your-api.run.app` (if using HTTP API wrapper)
- Or use direct MCP connection

**2. Create Step with Tool: `scan_qr_code_from_url`**

```json
{
  "tool": "scan_qr_code_from_url",
  "parameters": {
    "url": "{{ label_image_url }}"
  }
}
```

**3. Map Variables**
- Input: `label_image_url` from previous step
- Output: QR scan results (use in conditions/downstream steps)

**Example Workflow:**
```
1. User uploads label URL → Store in variable: label_url
2. Call MCP: scan_qr_code_from_url(label_url)
3. Check if scannable: if result.scannable === true
4. Return: "QR code is scannable" or process further
```

## Error Handling

### Common Issues & Solutions

**Timeout Error (408)**
- Image URL took too long to load
- Check internet connection to image source
- Try a different image or check URL validity

**Connection Error (503)**
- Cannot reach the image URL
- Verify URL is accessible from the server
- Check firewall rules

**HTTP Error (404, 403, 500)**
- Image URL returns error status
- Verify the URL points to a valid image
- Check authentication if image requires login

**Invalid URL Error (400)**
- URL must start with `http://` or `https://`
- Don't use `ftp://` or other protocols

## Response Format

All URL scans return the same format as file/base64 scans:

```json
{
  "success": true,
  "qr_found": true,
  "scannable": true,
  "qr_count": 1,
  "qr_codes": [
    {
      "type": "QRCODE",
      "data": "https://example.com",
      "scannable": true
    }
  ],
  "message": "QR code found and is scannable"
}
```

## Performance Tips

1. **Use CDN URLs** - Faster downloads from distributed servers
2. **Optimize Image Size** - Smaller images load faster (256x256px minimum)
3. **Batch Processing** - For multiple URLs, call in parallel where possible
4. **Caching** - Cache frequently used image URLs at your API level

## API Endpoint Reference

### POST /scan/url

**Request:**
```json
{
  "url": "https://example.com/label.jpg"
}
```

**Response (Success):**
```json
{
  "success": true,
  "qr_found": true,
  "scannable": true,
  "qr_count": 1,
  "qr_codes": [...],
  "message": "..."
}
```

**Response (Timeout):**
```json
{
  "detail": "Request timeout - URL took too long to respond"
}
```

**Response (Connection Error):**
```json
{
  "detail": "Could not connect to URL"
}
```

## MCP Tool Reference

### Tool: `scan_qr_code_from_url`

**Description:** Download and scan QR codes from an image URL

**Parameters:**
- `url` (string, required) - HTTP/HTTPS URL to image

**Returns:**
```json
{
  "success": boolean,
  "qr_found": boolean,
  "scannable": boolean,
  "qr_count": integer,
  "qr_codes": array,
  "message": string
}
```

## Security Notes

🔒 **URL Validation**
- Only HTTP/HTTPS protocols allowed
- No `file://` or `ftp://` URLs accepted
- URLs are validated before download

🔒 **Timeout Protection**
- 10-second timeout on downloads
- Prevents hanging on slow/stuck servers

🔒 **Size Limits**
- Reasonable file size limits enforced
- Protection against extremely large files

## Limitations

- Requires publicly accessible image URLs
- Cannot access password-protected URLs
- No proxy support (must be directly accessible)
- Maximum download time: 10 seconds
- No custom headers support

## Examples

### Scan Product Labels from E-Commerce
```python
# Get image URL from product page
product_url = "https://example-shop.com/products/label.jpg"
result = client.scan_url(product_url)

if result["scannable"]:
    qr_data = result["qr_codes"][0]["data"]
    # Process QR data (URL, tracking code, etc.)
```

### Lamatic Flow - Label Verification
```json
{
  "name": "Label QR Verification",
  "steps": [
    {
      "id": "get_image",
      "type": "input",
      "prompt": "Enter label image URL"
    },
    {
      "id": "scan_qr",
      "type": "tool_call",
      "tool": "scan_qr_code_from_url",
      "parameters": {
        "url": "{{ get_image.response }}"
      }
    },
    {
      "id": "check_scannable",
      "type": "condition",
      "condition": "{{ scan_qr.result.scannable == true }}",
      "true_step": "success",
      "false_step": "failure"
    }
  ]
}
```

### Batch URL Scanning in Python
```python
urls = [
    "https://example.com/label1.jpg",
    "https://example.com/label2.jpg",
    "https://example.com/label3.jpg"
]

results = []
for url in urls:
    result = client.scan_url(url)
    results.append({
        "url": url,
        "qr_found": result["qr_found"],
        "scannable": result["scannable"]
    })

# Summary
print(f"Total: {len(results)}")
print(f"QR Found: {sum(r['qr_found'] for r in results)}")
print(f"Scannable: {sum(r['scannable'] for r in results)}")
```

## Support

Need help? Check:
- `LAMATIC_INTEGRATION.md` - Lamatic.ai specific setup
- `QUICK_DEPLOY.md` - Deployment instructions
- `README.md` - General documentation
