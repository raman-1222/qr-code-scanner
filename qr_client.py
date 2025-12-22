"""
QR Scanner Client - Use your deployed QR scanner via HTTP
Works with any deployed instance (Cloud Run, Render, etc.)
"""

import requests
import base64
from pathlib import Path
from typing import Optional, Dict, Any


class QRScannerClient:
    """Client to interact with deployed QR scanner API"""

    def __init__(self, api_url: str):
        """
        Initialize client with API URL
        
        Args:
            api_url: Base URL of deployed QR scanner
                    e.g., "https://qr-scanner-xxx.run.app"
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}

    def scan_file(self, image_path: str) -> Dict[str, Any]:
        """
        Scan QR code from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Scan results
        """
        try:
            response = self.session.get(
                f"{self.api_url}/scan/file",
                params={"image_path": image_path}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "qr_found": False}

    def scan_upload(self, image_path: str) -> Dict[str, Any]:
        """
        Upload image and scan QR code
        
        Args:
            image_path: Path to image file to upload
            
        Returns:
            Scan results
        """
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.api_url}/scan/upload",
                    files=files
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "qr_found": False}
        except FileNotFoundError:
            return {"error": f"File not found: {image_path}", "qr_found": False}

    def scan_base64(self, image_data: str) -> Dict[str, Any]:
        """
        Scan QR code from base64 image
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            Scan results
        """
        try:
            response = self.session.post(
                f"{self.api_url}/scan/base64",
                json={"image_base64": image_data}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "qr_found": False}

    def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Scan QR code from image URL
        
        Args:
            url: HTTP/HTTPS URL to image
            
        Returns:
            Scan results
        """
        try:
            response = self.session.post(
                f"{self.api_url}/scan/url",
                json={"url": url}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "qr_found": False}

    def scan_from_file_base64(self, image_path: str) -> Dict[str, Any]:
        """
        Read file and scan as base64
        
        Args:
            image_path: Path to image file
            
        Returns:
            Scan results
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            return self.scan_base64(image_data)
        except FileNotFoundError:
            return {"error": f"File not found: {image_path}", "qr_found": False}

    def batch_scan(self, image_paths: list) -> Dict[str, Any]:
        """
        Scan multiple images at once
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Batch scan results
        """
        try:
            images = []
            for path in image_paths:
                with open(path, 'rb') as f:
                    images.append({
                        "name": Path(path).name,
                        "data": base64.b64encode(f.read()).decode('utf-8')
                    })
            
            response = self.session.post(
                f"{self.api_url}/scan/batch",
                json={"images": images}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
        except FileNotFoundError as e:
            return {"error": str(e)}


# Convenience functions for quick use

def quick_scan(api_url: str, image_path: str) -> Dict[str, Any]:
    """Quick scan without creating client"""
    client = QRScannerClient(api_url)
    return client.scan_upload(image_path)


def quick_scan_url(api_url: str, url: str) -> Dict[str, Any]:
    """Quick scan from URL without creating client"""
    client = QRScannerClient(api_url)
    return client.scan_url(url)


def quick_batch_scan(api_url: str, image_paths: list) -> Dict[str, Any]:
    """Quick batch scan without creating client"""
    client = QRScannerClient(api_url)
    return client.batch_scan(image_paths)


# Example usage
if __name__ == "__main__":
    import json
    
    # Replace with your deployed API URL
    API_URL = "https://your-deployment-url.run.app"
    
    # Create client
    client = QRScannerClient(API_URL)
    
    # Check health
    print("Health Check:")
    print(json.dumps(client.health_check(), indent=2))
    
    # Scan single image
    print("\nScan Single Image:")
    result = client.scan_upload("path/to/image.jpg")
    print(json.dumps(result, indent=2))
    
    # Batch scan
    print("\nBatch Scan:")
    results = client.batch_scan([
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ])
    print(json.dumps(results, indent=2))
