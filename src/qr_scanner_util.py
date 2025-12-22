"""
QR Code Scanner Utility
Core QR scanning logic - independent of any AI framework
"""

import base64
import logging
from typing import Any
from io import BytesIO

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class QRCodeScanner:
    """Pure QR code detection and scanning utility"""

    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()

    def scan_image_file(self, image_path: str) -> dict[str, Any]:
        """
        Scan a QR code from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": f"Failed to load image from {image_path}",
                    "qr_found": False,
                    "scannable": False,
                }

            return self._analyze_qr_code(image)
        except Exception as e:
            logger.error(f"Error scanning image file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qr_found": False,
                "scannable": False,
            }

    def scan_image_base64(self, image_base64: str) -> dict[str, Any]:
        """
        Scan a QR code from a base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                return {
                    "success": False,
                    "error": "Failed to decode image from base64",
                    "qr_found": False,
                    "scannable": False,
                }

            return self._analyze_qr_code(image)
        except Exception as e:
            logger.error(f"Error scanning base64 image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qr_found": False,
                "scannable": False,
            }

    def _analyze_qr_code(self, image: np.ndarray) -> dict[str, Any]:
        """
        Analyze image for QR code detection and validation
        
        Args:
            image: OpenCV image matrix
            
        Returns:
            Analysis results
        """
        try:
            # Preprocess image for better QR detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply contrast enhancement for better detection
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Detect QR codes with OpenCV - try multi-detection first
            ret_val, decoded_info, points, straight_qr = (
                self.qr_detector.detectAndDecodeMulti(enhanced)
            )

            # Process multi-detection results
            if ret_val and decoded_info:
                # Filter out empty strings from decoded_info
                decoded_info = [info for info in decoded_info if info]
            else:
                decoded_info = []

            # If multi-detection didn't work, try single detection
            if not decoded_info:
                result = self.qr_detector.detectAndDecode(enhanced)
                # Handle both return formats (3 or 4 values depending on OpenCV version)
                if len(result) == 4:
                    ret_val, single_qr, points, straight_qr = result
                else:
                    ret_val, single_qr, points = result
                
                if single_qr:
                    decoded_info = [single_qr]
                else:
                    # No QR codes found
                    return {
                        "success": True,
                        "qr_found": False,
                        "scannable": False,
                        "message": "No QR code detected in the image",
                    }

            # Process detected QR codes
            qr_results = []
            for i, qr_text in enumerate(decoded_info):
                if qr_text:
                    qr_results.append(
                        {
                            "qr_index": i,
                            "content": qr_text,
                            "scannable": True,
                            "valid": True,
                            "length": len(qr_text),
                        }
                    )

            if qr_results:
                return {
                    "success": True,
                    "qr_found": True,
                    "scannable": True,
                    "qr_count": len(qr_results),
                    "qr_codes": qr_results,
                    "message": f"Successfully detected and scanned {len(qr_results)} QR code(s)",
                }
            else:
                return {
                    "success": True,
                    "qr_found": False,
                    "scannable": False,
                    "message": "QR code pattern detected but unable to decode",
                }

        except Exception as e:
            logger.error(f"Error analyzing QR code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qr_found": False,
                "scannable": False,
            }

    def scan_pdf_file(self, pdf_path: str) -> dict[str, Any]:
        """
        Scan QR codes from all images in a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with results for each image
        """
        try:
            from pdf2image import convert_from_path
            
            logger.info(f"Scanning PDF: {pdf_path}")
            
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            logger.info(f"Extracted {len(images)} pages from PDF")
            
            all_results = []
            total_qr_found = 0
            total_scannable = 0
            
            for page_num, image in enumerate(images, 1):
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Convert to BGR if RGB
                if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Scan this page
                result = self._analyze_qr_code(img_array)
                result["page_number"] = page_num
                all_results.append(result)
                
                if result.get("qr_found"):
                    total_qr_found += 1
                if result.get("scannable"):
                    total_scannable += 1
            
            return {
                "success": True,
                "total_pages": len(images),
                "pages_with_qr": total_qr_found,
                "pages_scannable": total_scannable,
                "qr_count": sum(r.get("qr_count", 0) for r in all_results),
                "pages": all_results,
                "message": f"Scanned {len(images)} pages, found QR codes in {total_qr_found} pages ({total_scannable} scannable)"
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "pdf2image library not installed",
                "qr_found": False
            }
        except Exception as e:
            logger.error(f"Error scanning PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qr_found": False
            }

    def scan_pdf_base64(self, pdf_base64: str) -> dict[str, Any]:
        """
        Scan QR codes from a base64-encoded PDF file
        
        Args:
            pdf_base64: Base64-encoded PDF data
            
        Returns:
            Dictionary with results for each page
        """
        try:
            from pdf2image import convert_from_bytes
            
            # Decode base64
            pdf_data = base64.b64decode(pdf_base64)
            logger.info("Scanning base64-encoded PDF")
            
            # Convert PDF to images
            images = convert_from_bytes(pdf_data)
            logger.info(f"Extracted {len(images)} pages from PDF")
            
            all_results = []
            total_qr_found = 0
            total_scannable = 0
            
            for page_num, image in enumerate(images, 1):
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Convert to BGR if RGB
                if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Scan this page
                result = self._analyze_qr_code(img_array)
                result["page_number"] = page_num
                all_results.append(result)
                
                if result.get("qr_found"):
                    total_qr_found += 1
                if result.get("scannable"):
                    total_scannable += 1
            
            return {
                "success": True,
                "total_pages": len(images),
                "pages_with_qr": total_qr_found,
                "pages_scannable": total_scannable,
                "qr_count": sum(r.get("qr_count", 0) for r in all_results),
                "pages": all_results,
                "message": f"Scanned {len(images)} pages, found QR codes in {total_qr_found} pages ({total_scannable} scannable)"
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "pdf2image library not installed",
                "qr_found": False
            }
        except Exception as e:
            logger.error(f"Error scanning PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qr_found": False
            }
