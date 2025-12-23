"""
QR Code Scanner Utility
Core QR scanning logic - independent of any AI framework
"""

import base64
import logging
import gc
import os
import tempfile
from typing import Any
from io import BytesIO
import os
import tempfile
import gc

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class QRCodeScanner:
    """Pure QR code detection and scanning utility"""

    def __init__(self):
        # OpenCV can emit noisy warnings like:
        # "decodingProcess QR: ECI is not supported properly".
        # This doesn't necessarily mean decoding failed (URLs often still decode),
        # but it can flood logs on hosted environments.
        try:
            if os.getenv("OPENCV_LOG_LEVEL", "ERROR").upper() == "ERROR":
                cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
        except Exception:
            pass
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
            if image.ndim == 2:
                gray = image
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply contrast enhancement for better detection
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            qr_codes: list[str] = []
            seen_qr: set[str] = set()
            angles = [0, 90, 180, 270]

            def _run_detection(variant: np.ndarray) -> None:
                nonlocal qr_codes
                for angle in angles:
                    try:
                        if angle == 0:
                            rotated = variant
                        else:
                            h, w = variant.shape[:2]
                            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
                            rotated = cv2.warpAffine(
                                variant,
                                M,
                                (w, h),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REPLICATE,
                            )

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

                                # OpenCV can sometimes surface non-string payloads; ignore them.
                                if not isinstance(qr_data, (str, bytes)):
                                    continue

                                qr_str = qr_data.decode("utf-8", errors="ignore") if isinstance(qr_data, bytes) else qr_data
                                qr_str = qr_str.strip().strip("()' \"")
                                if not qr_str:
                                    continue

                                # Reject coordinate/points blobs (sometimes come back as stringified arrays)
                                qr_str_lstripped = qr_str.lstrip()
                                if qr_str_lstripped.startswith('['):
                                    continue
                                if all(c.isdigit() or c.isspace() or c in '.,[]()-' for c in qr_str_lstripped):
                                    continue
                                has_letters = any(c.isalpha() for c in qr_str)
                                if has_letters or qr_str.startswith(('http://', 'https://', 'ftp://')):
                                    if qr_str not in seen_qr:
                                        seen_qr.add(qr_str)
                                        qr_codes.append(qr_str)
                    except Exception as e:
                        logger.debug(f"Rotation {angle} detection failed: {e}")

            # Pass 1: cheapest path (enhanced only)
            _run_detection(enhanced)

            # Pass 2: only if nothing found, try heavier preprocessing.
            if not qr_codes:
                # Upscale only when the image is relatively small; avoid huge memory spikes.
                max_dim = max(enhanced.shape[:2])
                if max_dim < 1800:
                    upscaled = cv2.resize(enhanced, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
                else:
                    upscaled = enhanced

                # Adaptive threshold can be expensive on very large images; cap its size.
                if max(upscaled.shape[:2]) > 2200:
                    scale = 2200 / float(max(upscaled.shape[:2]))
                    new_w = int(upscaled.shape[1] * scale)
                    new_h = int(upscaled.shape[0] * scale)
                    upscaled_for_thresh = cv2.resize(upscaled, (new_w, new_h), interpolation=cv2.INTER_AREA)
                else:
                    upscaled_for_thresh = upscaled

                thresh = cv2.adaptiveThreshold(
                    upscaled_for_thresh,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31,
                    10,
                )

                _run_detection(upscaled)
                if not qr_codes:
                    _run_detection(thresh)

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

            # Fallback: pyzbar decode (better at some tilted codes)
            if not qr_codes:
                try:
                    from pyzbar import pyzbar

                    # Try on grayscale and thresholded versions
                    candidates = [enhanced]
                    try:
                        candidates.append(thresh)
                    except Exception:
                        pass
                    for cand in candidates:
                        decoded = pyzbar.decode(cand)
                        for d in decoded:
                            # Only accept QR codes, not other barcode types
                            if d.type != 'QRCODE':
                                continue
                            data = d.data.decode('utf-8').strip()
                            if data:
                                qr_codes.append(data)
                        if qr_codes:
                            break
                except Exception as e:
                    logger.debug(f"pyzbar fallback failed: {e}")
            
            # Fallback: QReader (neural network-based, more robust)
            if not qr_codes:
                try:
                    from qreader import QReader
                    
                    # QReader works best with color images
                    if image.ndim == 2:
                        color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    else:
                        color_image = image
                    
                    qreader = QReader()
                    decoded_texts = qreader.detect_and_decode(image=color_image)
                    
                    if decoded_texts:
                        for text in decoded_texts:
                            if text and isinstance(text, str):
                                qr_codes.append(text.strip())
                                logger.debug(f"QReader found QR code: {text}")
                except ImportError:
                    logger.debug("QReader not available, skipping")
                except Exception as e:
                    logger.debug(f"QReader fallback failed: {e}")            
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
            from pdf2image.pdf2image import pdfinfo_from_path
            
            logger.info(f"Scanning PDF: {pdf_path}")
            
            # Render pages one-by-one to avoid holding the entire PDF as images in memory.
            # Keep memory low on Render free tier: default to a lower DPI.
            base_dpi = int(os.getenv("PDF_DPI", "150"))
            retry_dpi = int(os.getenv("PDF_RETRY_DPI", "200"))
            max_retry_pages = int(os.getenv("PDF_MAX_RETRY_PAGES", "5"))

            info = pdfinfo_from_path(pdf_path)
            total_pages = int(info.get("Pages", 0))
            if total_pages <= 0:
                raise ValueError("Could not determine PDF page count")

            logger.info(f"PDF has {total_pages} pages (dpi={base_dpi}, retry_dpi={retry_dpi})")
            
            all_results: list[dict[str, Any]] = []
            total_qr_found = 0
            total_scannable = 0
            retry_budget = max_retry_pages
            
            for page_num in range(1, total_pages + 1):
                # Convert just this page
                images = convert_from_path(
                    pdf_path,
                    dpi=base_dpi,
                    first_page=page_num,
                    last_page=page_num,
                )
                if not images:
                    result = {
                        "success": True,
                        "qr_found": False,
                        "scannable": False,
                        "message": "Failed to render PDF page",
                        "page_number": page_num,
                    }
                    all_results.append(result)
                    continue

                image = images[0]

                # Convert to grayscale early to reduce memory footprint.
                try:
                    image = image.convert("L")
                except Exception:
                    pass

                # Downscale very large pages before NumPy conversion.
                try:
                    w, h = image.size
                    max_side = int(os.getenv("PDF_MAX_SIDE", "1800"))
                    if max(w, h) > max_side:
                        scale = max_side / float(max(w, h))
                        new_w = max(1, int(w * scale))
                        new_h = max(1, int(h * scale))
                        image = image.resize((new_w, new_h))
                except Exception:
                    pass

                img_array = np.array(image)
                
                # Scan this page
                result = self._analyze_qr_code(img_array)

                # If no QR found at lower DPI, retry this page only at higher DPI.
                if (not result.get("qr_found")) and retry_dpi > base_dpi and retry_budget > 0:
                    try:
                        images_retry = convert_from_path(
                            pdf_path,
                            dpi=retry_dpi,
                            first_page=page_num,
                            last_page=page_num,
                        )
                        if images_retry:
                            retry_budget -= 1
                            img_retry_pil = images_retry[0]
                            try:
                                img_retry_pil = img_retry_pil.convert("L")
                            except Exception:
                                pass
                            try:
                                w2, h2 = img_retry_pil.size
                                max_side = int(os.getenv("PDF_MAX_SIDE", "1800"))
                                if max(w2, h2) > max_side:
                                    scale = max_side / float(max(w2, h2))
                                    new_w2 = max(1, int(w2 * scale))
                                    new_h2 = max(1, int(h2 * scale))
                                    img_retry_pil = img_retry_pil.resize((new_w2, new_h2))
                            except Exception:
                                pass

                            img_retry = np.array(img_retry_pil)
                            result_retry = self._analyze_qr_code(img_retry)
                            if result_retry.get("qr_found"):
                                result = result_retry
                    except Exception as e:
                        logger.debug(f"Retry render at dpi={retry_dpi} failed for page {page_num}: {e}")
                result["page_number"] = page_num
                all_results.append(result)
                
                if result.get("qr_found"):
                    total_qr_found += 1
                if result.get("scannable"):
                    total_scannable += 1

                # Drop references ASAP to keep memory flat.
                try:
                    del image
                    del images
                    del img_array
                except Exception:
                    pass
                if page_num % 2 == 0:
                    gc.collect()
            
            return {
                "success": True,
                "total_pages": total_pages,
                "pages_with_qr": total_qr_found,
                "pages_scannable": total_scannable,
                "qr_count": sum(r.get("qr_count", 0) for r in all_results),
                "pages": all_results,
                "message": f"Scanned {total_pages} pages, found QR codes in {total_qr_found} pages ({total_scannable} scannable)"
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
            # Decode base64 then scan via temp file to keep memory usage low.
            pdf_data = base64.b64decode(pdf_base64)
            logger.info("Scanning base64-encoded PDF (temp file)")

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_data)
                tmp_path = tmp.name

            try:
                return self.scan_pdf_file(tmp_path)
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            
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
