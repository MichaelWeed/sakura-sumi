"""Compression modules for OCR codebase compression."""

from .pdf_converter import PDFConverter
from .ocr_compression import OCRCompressor, create_ocr_compressor

__all__ = ['PDFConverter', 'OCRCompressor', 'create_ocr_compressor']

