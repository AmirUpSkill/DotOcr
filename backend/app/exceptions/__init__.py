from .storage_exceptions import (
    StorageError,
    FileUploadError,
    FileNotFoundError,
    FileValidationError,
    StorageConnectionError,
)

from .ocr_exceptions import (
    OcrError,
    OcrProcessingError,
    PromptNotFoundError,
    OcrApiError,
    OcrParsingError,
)

__all__ = [
    # Storage exceptions
    "StorageError",
    "FileUploadError",
    "FileNotFoundError",
    "FileValidationError",
    "StorageConnectionError",
    # OCR exceptions
    "OcrError",
    "OcrProcessingError",
    "PromptNotFoundError",
    "OcrApiError",
    "OcrParsingError",
]
