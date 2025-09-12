from __future__ import annotations
import typing
from pathlib import Path

MB = 1_048_576
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

def get_file_size_kb(file: typing.BinaryIO) -> float:
    """
    Return file size in kilobytes (float).
    Moves the cursor back to 0 after measuring.
    """
    file.seek(0, 2)          
    size_bytes = file.tell()
    file.seek(0)            
    return size_bytes / 1024

def validate_file_type(file: typing.BinaryIO, filename: str) -> None:
    """
    Raise ValueError if extension is not whitelisted.
    We do NOT trust the mime-type from the client.
    """
    suffix = Path(filename.lower()).suffix
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension {suffix!r}. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

def sanitize_filename(name: str) -> str:
    """
    Return a filesystem-safe string.
    Keeps alphanumerics, dash, underscore, dot.
    """
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip()