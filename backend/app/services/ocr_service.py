"""
OCR Service for extracting text from scanned PDFs
Falls back to OCR when pdfplumber cannot extract text
"""

import logging
from enum import Enum
from typing import Optional, Tuple

import pytesseract
from PIL import Image
import pdf2image

logger = logging.getLogger(__name__)


class ExtractionMethod(str, Enum):
    """Method used to extract text from PDF"""

    PDFPLUMBER = "pdfplumber"
    OCR = "ocr"


class OCRService:
    """Service for OCR text extraction from scanned PDFs"""

    # Minimum text length to consider extraction successful
    MIN_TEXT_LENGTH = 100

    @staticmethod
    def should_use_ocr(extracted_text: Optional[str]) -> bool:
        """
        Determine if OCR should be used

        Args:
            extracted_text: Text extracted by pdfplumber

        Returns:
            True if OCR should be used
        """
        if not extracted_text:
            logger.info("No text extracted by pdfplumber, will use OCR")
            return True

        # Check if text is too short (likely scanned image)
        if len(extracted_text.strip()) < OCRService.MIN_TEXT_LENGTH:
            logger.info(
                f"Extracted text too short ({len(extracted_text)} chars), using OCR"
            )
            return True

        logger.info(f"Successfully extracted {len(extracted_text)} characters with pdfplumber")
        return False

    @staticmethod
    def extract_text_with_ocr(
        pdf_content: bytes,
    ) -> Tuple[Optional[str], int]:
        """
        Extract text from PDF using OCR

        Args:
            pdf_content: PDF file as bytes

        Returns:
            Tuple of (extracted_text, pages_processed)

        Raises:
            Exception: If OCR fails
        """
        try:
            logger.info("Starting OCR text extraction...")

            # Convert PDF to images
            images = pdf2image.convert_from_bytes(pdf_content)
            logger.info(f"Converted PDF to {len(images)} image(s)")

            # Extract text from each image using OCR
            text_parts = []
            for page_num, image in enumerate(images, 1):
                logger.debug(f"Processing page {page_num} with OCR")

                # Use pytesseract to extract text
                page_text = pytesseract.image_to_string(image)

                if page_text.strip():
                    text_parts.append(page_text)
                    logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                else:
                    logger.debug(f"No text extracted from page {page_num}")

            full_text = "\n".join(text_parts)
            logger.info(
                f"OCR extraction complete. Extracted {len(full_text)} total characters"
            )

            return full_text if full_text.strip() else None, len(images)

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise

    @staticmethod
    def compare_extractions(
        pdfplumber_text: Optional[str],
        ocr_text: Optional[str],
    ) -> Tuple[Optional[str], ExtractionMethod]:
        """
        Compare pdfplumber and OCR extractions

        Choose the better one based on:
        1. Length of extracted text
        2. Quality indicators

        Args:
            pdfplumber_text: Text from pdfplumber
            ocr_text: Text from OCR

        Returns:
            Tuple of (best_text, extraction_method)
        """
        if not pdfplumber_text and not ocr_text:
            logger.warning("No text extracted by either method")
            return None, ExtractionMethod.PDFPLUMBER

        if not ocr_text:
            logger.info("Using pdfplumber extraction (OCR not available)")
            return pdfplumber_text, ExtractionMethod.PDFPLUMBER

        if not pdfplumber_text:
            logger.info("Using OCR extraction (pdfplumber failed)")
            return ocr_text, ExtractionMethod.OCR

        # Both methods succeeded, choose the longer one
        pdfplumber_len = len(pdfplumber_text.strip())
        ocr_len = len(ocr_text.strip())

        logger.info(
            f"Both methods succeeded. pdfplumber: {pdfplumber_len} chars, OCR: {ocr_len} chars"
        )

        if pdfplumber_len >= ocr_len:
            logger.info("Choosing pdfplumber extraction (longer)")
            return pdfplumber_text, ExtractionMethod.PDFPLUMBER
        else:
            logger.info("Choosing OCR extraction (longer)")
            return ocr_text, ExtractionMethod.OCR
