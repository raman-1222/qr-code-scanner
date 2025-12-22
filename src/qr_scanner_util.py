"""
QR Code Scanner Utility
Core QR scanning logic - independent of any AI framework
"""

import base64
import logging
from typing import Any

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
            # Detect QR code
            ret_val, decoded_info, points, straight_qr = (
                self.qr_detector.detectAndDecodeMulti(image)
            )

            if not ret_val or not decoded_info:
                # Try single QR detection as fallback
                ret_val, decoded_info, points = self.qr_detector.detectAndDecode(
                    image
                )

                if not decoded_info:
                    return {
                        "success": True,
                        "qr_found": False,
                        "scannable": False,
                        "message": "No QR code detected in the image",
                    }

                decoded_info = [decoded_info]

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
