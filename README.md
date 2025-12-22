# QR Code Scanner MCP Server

A Model Context Protocol (MCP) server that detects and validates QR codes in label images. Perfect for integration with LlamaIndex, Claude, and other AI applications.

## Features

- **QR Code Detection**: Detects QR codes in images
- **Multiple Format Support**: Supports PNG, JPG, BMP, and other common image formats
- **Base64 Support**: Can process images directly as base64-encoded strings
- **Scanability Validation**: Determines if detected QR codes are readable
- **Content Extraction**: Extracts and returns QR code data when readable

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. Clone or navigate to the project directory:
```bash
cd qr_code_scanner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the MCP Server

```bash
python -m src.server
```

Or using the installed script:
```bash
qr-code-scanner
```

### Available Tools

#### 1. `scan_qr_code_from_file`
Scan a QR code from an image file on disk.

**Parameters:**
- `image_path` (string, required): Path to the image file

**Response:**
```json
{
  "success": true,
  "qr_found": true,
  "scannable": true,
  "qr_count": 1,
  "qr_codes": [
    {
      "qr_index": 0,
      "content": "https://example.com",
      "scannable": true,
      "valid": true,
      "length": 19
    }
  ],
  "message": "Successfully detected and scanned 1 QR code(s)"
}
```

#### 2. `scan_qr_code_from_base64`
Scan a QR code from a base64-encoded image.

**Parameters:**
- `image_base64` (string, required): Base64 encoded image data

**Response:**
Same as above

## Integration with LlamaIndex/Claude

### Example: Using with Claude via MCP

```python
from anthropic import Anthropic

client = Anthropic()

# Your Claude client will automatically have access to the QR scanner tools
# when the MCP server is running

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "name": "scan_qr_code_from_file",
            "description": "Scan QR codes in images",
            "input_schema": {...}
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Check if the QR code in /path/to/label.jpg is scannable"
        }
    ]
)
```

## Deployment Options

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "-m", "src.server"]
```

Build and run:
```bash
docker build -t qr-code-scanner .
docker run -p 5000:5000 qr-code-scanner
```

### Cloud Deployment

The server can be deployed to:
- **AWS Lambda** (with proper containerization)
- **Google Cloud Run** (containerized)
- **Azure Container Instances**
- **Heroku** (with Procfile)

### Using with LlamaIndex

```python
from llama_index.tools import MCP
from llama_index.agent import AgentRunner

# Initialize the MCP tool
qr_scanner = MCP(
    server_path="python",
    server_args=["-m", "src.server"]
)

# Create an agent with QR scanning capability
agent = AgentRunner.from_llm(
    llm=llm,
    tools=[qr_scanner]
)
```

## Configuration

### Environment Variables

You can customize behavior with environment variables:

```bash
# Enable debug logging
export DEBUG=true

# Set image processing timeout (seconds)
export PROCESSING_TIMEOUT=30

# Set max image size (MB)
export MAX_IMAGE_SIZE=50
```

## Troubleshooting

### "No module named 'cv2'"
Install opencv-python:
```bash
pip install opencv-python
```

### QR Code Not Detected
- Ensure the image has good lighting and contrast
- The QR code should be at least 50x50 pixels
- The image resolution should be at least 100x100 pixels

### Slow Performance
- Reduce image resolution before scanning
- Use a more powerful machine or cloud instance
- Consider batch processing

## API Reference

### Response Structure

All responses follow this structure:

```json
{
  "success": true/false,
  "qr_found": true/false,
  "scannable": true/false,
  "qr_count": 0,
  "qr_codes": [
    {
      "qr_index": 0,
      "content": "QR code data",
      "scannable": true,
      "valid": true,
      "length": 100
    }
  ],
  "message": "Human readable message",
  "error": "Error message if applicable"
}
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue or submit a pull request.

## Version History

- **1.0.0** (Initial Release)
  - QR code detection from files and base64 images
  - Scanability validation
  - Multi-QR code support
  - MCP protocol compliance
