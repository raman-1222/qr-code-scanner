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

            # Upscale for small/tilted codes
            upscaled = cv2.resize(enhanced, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            # Adaptive threshold to increase edge contrast
            thresh = cv2.adaptiveThreshold(upscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 31, 10)

            qr_codes: list[str] = []
            angles = [0, -25, 25, -45, 45, 90]
            image_variants = [enhanced, upscaled, thresh]

            for variant in image_variants:
                for angle in angles:
                    try:
                        if angle == 0:
                            rotated = variant
                        else:
                            h, w = variant.shape[:2]
                            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
                            rotated = cv2.warpAffine(variant, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

                        ret_val, decoded_info, points, straight_qr = (
                            self.qr_detector.detectAndDecodeMulti(rotated)
                        )

                        if decoded_info is not None:
                            if isinstance(decoded_info, np.ndarray):
                                decoded_list = decoded_info.tolist()
                            elif isinstance(decoded_info, (list, tuple)):
                                decoded_list = list(decoded_info)
                            else:
                                decoded_list = [decoded_info]

                            for qr_data in decoded_list:
                                if qr_data is None:
                                    continue

                                qr_str = str(qr_data).strip().strip("()' \"")
                                if not qr_str:
                                    continue
                                # Reject coordinate blobs
                                if qr_str[0] == '[':
                                    continue
                                if all(c.isdigit() or c.isspace() or c in '.,[]()-' for c in qr_str):
                                    continue
                                has_letters = any(c.isalpha() for c in qr_str)
                                if has_letters or qr_str.startswith(('http://', 'https://', 'ftp://')):
                                    qr_codes.append(qr_str)

                        if qr_codes:
                            break  # stop rotating once we found something
                    except Exception as e:
                        logger.debug(f"Rotation {angle} detection failed: {e}")
                if qr_codes:
                    break

            # If still nothing, try single detect on enhanced image
            if not qr_codes:
                try:
                    result = self.qr_detector.detectAndDecode(enhanced)
                    single_qr = result[1] if len(result) > 1 else None

                    if single_qr is not None:
                        qr_str = str(single_qr).strip().strip("()' \"")
                        if qr_str and len(qr_str) > 0:
                            qr_codes.append(qr_str)
                except Exception as e:
                    logger.debug(f"Single detection failed: {e}")            
            # Return results
            if qr_codes:
                qr_results = [
                    {
                        "qr_index": i,
                        "content": code,
                        "scannable": True,
                        "valid": True,
                        "length": len(code)
                    }
                    for i, code in enumerate(qr_codes)
                ]
                return {
                    "success": True,
                    "qr_found": True,
                    "scannable": True,
                    "qr_count": len(qr_codes),
                    "qr_codes": qr_results,
                    "message": f"Successfully detected and scanned {len(qr_codes)} QR code(s)",
                }
            else:
                return {
                    "success": True,
                    "qr_found": False,
                    "scannable": False,
                    "message": "No QR code detected in the image",
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
            
            # Convert PDF pages to images at higher DPI for better QR detection
            images = convert_from_path(pdf_path, dpi=300)
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
            images = convert_from_bytes(pdf_data, dpi=300)
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
