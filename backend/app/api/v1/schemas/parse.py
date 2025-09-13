from pydantic import BaseModel
from typing import Optional

class ParseResponseData(BaseModel):
    """The 'data' part of a successful parse response."""
    markdown: str
    rawText: str

class ParseResponseMetadata(BaseModel):
    """The 'metadata' part of a successful parse response."""
    storage_key: str
    model: str
    processing_time_ms: int
    request_id: str
    file_size_kb: float

class ParseSuccessResponse(BaseModel):
    """The full response structure for a successful parse operation."""
    success: bool = True
    data: ParseResponseData
    metadata: ParseResponseMetadata

class ErrorDetail(BaseModel):
    """Standardized structure for an API error."""
    code: str
    message: str

class ErrorResponse(BaseModel):
    """The full response structure for a failed operation."""
    success: bool = False
    error: ErrorDetail