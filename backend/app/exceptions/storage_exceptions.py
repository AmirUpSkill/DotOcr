"""
Custom exceptions for storage operations.
"""


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class FileUploadError(StorageError):
    """Raised when file upload fails."""
    pass


class FileNotFoundError(StorageError):
    """Raised when a requested file is not found in storage."""
    pass


class FileValidationError(StorageError):
    """Raised when file validation fails."""
    pass


class StorageConnectionError(StorageError):
    """Raised when storage service connection fails."""
    pass
