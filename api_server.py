"""
HTTP API Wrapper for QR Code Scanner MCP
Expose the MCP server as a simple REST API for easy integration
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import base64
import json
import requests
from io import BytesIO
from src.qr_scanner_util import QRCodeScanner

app = FastAPI(
    title="QR Code Scanner API",
    description="Scan QR codes in images via HTTP",
    version="1.0.0"
)

qr_scanner = QRCodeScanner()


@app.get("/")
async def root():
    """API Information"""
    return {
        "service": "QR Code Scanner API",
        "version": "1.0.0",
        "endpoints": {
            "scan_file": "/scan/file?image_path=path/to/image.jpg",
            "scan_upload": "/scan/upload (POST with file)",
            "scan_url": "/scan/url (POST with JSON: {\"url\": \"https://...\"})",
            "scan_base64": "/scan/base64 (POST with JSON: {\"image_base64\": \"...\"})",
            "scan_batch": "/scan/batch (POST with multiple base64 images)",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "QR Code Scanner API"
    }


@app.get("/scan/file")
async def scan_file(image_path: str):
    """
    Scan QR code from file path
    
    Query Parameters:
    - image_path: Path to image file
    
    Example: /scan/file?image_path=/path/to/label.jpg
    """
    try:
        result = qr_scanner.scan_image_file(image_path)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scan/upload")
async def scan_upload(file: UploadFile = File(...)):
    """
    Scan QR code from uploaded image
    
    Upload an image file and get QR code scan results
    """
    try:
        contents = await file.read()
        
        # Convert to base64 and scan
        image_base64 = base64.b64encode(contents).decode('utf-8')
        result = qr_scanner.scan_image_base64(image_base64)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scan/url")
async def scan_url(data: dict):
    """
    Scan QR code from a URL
    
    Expected JSON:
    {
        "url": "https://example.com/label.jpg"
    }
    
    Supports HTTP and HTTPS URLs
    """
    try:
        if "url" not in data:
            raise ValueError("Missing 'url' in request body")
        
        url = data["url"]
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Download image with timeout
        headers = {
            'User-Agent': 'QR-Code-Scanner/1.0'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Scan the image
        result = qr_scanner.scan_image_base64(image_data)
        return JSONResponse(content=result)
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout - URL took too long to respond")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to URL")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scanning URL: {str(e)}")


@app.post("/scan/base64")
async def scan_base64(data: dict):
    """
    Scan QR code from base64 encoded image
    
    Expected JSON:
    {
        "image_base64": "base64-encoded-image-string"
    }
    """
    try:
        if "image_base64" not in data:
            raise ValueError("Missing 'image_base64' in request body")
        
        result = qr_scanner.scan_image_base64(data["image_base64"])
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scan/batch")
async def scan_batch(data: dict):
    """
    Scan multiple images (base64)
    
    Expected JSON:
    {
        "images": [
            {
                "name": "label-001.jpg",
                "data": "base64-encoded-string"
            },
            ...
        ]
    }
    """
    try:
        if "images" not in data:
            raise ValueError("Missing 'images' in request body")
        
        results = []
        for img in data["images"]:
            result = qr_scanner.scan_image_base64(img["data"])
            results.append({
                "name": img.get("name", "unknown"),
                "result": result
            })
        
        return JSONResponse(content={
            "total_images": len(results),
            "results": results
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scan/pdf-base64")
async def scan_pdf_base64(data: dict):
    """
    Scan QR codes from a base64-encoded PDF file
    
    Expected JSON:
    {
        "pdf_base64": "base64-encoded-pdf-string"
    }
    """
    try:
        if "pdf_base64" not in data:
            raise ValueError("Missing 'pdf_base64' in request body")
        
        result = qr_scanner.scan_pdf_base64(data["pdf_base64"])
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scan/pdf-url")
async def scan_pdf_url(data: dict):
    """
    Scan QR codes from a PDF file at a URL
    
    Expected JSON:
    {
        "url": "https://example.com/document.pdf"
    }
    
    Downloads the PDF and scans all pages for QR codes
    """
    try:
        if "url" not in data:
            raise ValueError("Missing 'url' in request body")
        
        url = data["url"]
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Download PDF to a temp file (avoids holding both bytes + base64 in memory)
        import tempfile
        import os

        headers = {'User-Agent': 'QR-Code-Scanner/1.0'}
        with requests.get(url, headers=headers, timeout=30, stream=True) as response:
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        tmp.write(chunk)

        try:
            result = qr_scanner.scan_pdf_file(tmp_path)
            return JSONResponse(content=result)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout - PDF URL took too long to respond")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to PDF URL")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error scanning PDF URL: {str(e)}")


@app.post("/scan/pdf")
async def scan_pdf(file: UploadFile = File(...)):
    """
    Scan QR codes from all pages in a PDF file
    
    Upload a PDF and get QR code scan results for each page
    """
    try:
        import tempfile
        import os

        contents = await file.read()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            result = qr_scanner.scan_pdf_file(tmp_path)
            return JSONResponse(content=result)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use PORT env variable (for Cloud Run), default to 8000
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
