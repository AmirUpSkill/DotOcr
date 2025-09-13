"""
Custom exceptions for OCR operations.
"""


class OcrError(Exception):
    """Base exception for OCR-related errors."""
    pass


class OcrProcessingError(OcrError):
    """Raised when OCR processing fails."""
    pass


class PromptNotFoundError(OcrError):
    """Raised when a specified prompt is not found."""
    pass


class OcrApiError(OcrError):
    """Raised when external OCR API calls fail."""
    pass


class OcrParsingError(OcrError):
    """Raised when OCR response parsing fails."""
    pass
