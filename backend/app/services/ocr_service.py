import uuid
import re
import time
from typing import Dict, Any
import logging
from mistralai import Mistral, SDKError
from app.core.config import settings
from app.services.storage_service import storage_service
from app.prompts.definitions import load_prompts
from app.exceptions import OcrProcessingError, PromptNotFoundError

logger = logging.getLogger(__name__)

class OcrService:
    """OCR service using Mistral API for document processing."""
    
    def __init__(self):
        if not settings.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is required")
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        self.model = "mistral-ocr-latest"
        logger.info("OcrService initialized")
    
    def process_document(self, storage_key: str, prompt_id: str) -> Dict[str, Any]:
        """Process document with Mistral OCR and return markdown + raw text."""
        start_time = time.time()
        request_id = f"ocr_{uuid.uuid4().hex[:8]}"
        
        try:
            # Validate prompt exists
            prompts = load_prompts()
            if not any(p["id"] == prompt_id for p in prompts):
                raise PromptNotFoundError(f"Prompt '{prompt_id}' not found")
            
            # Get file URL for Mistral to access
            file_url = storage_service.get_file_url(storage_key, expires_in_hours=2)
            
            # Call Mistral OCR API
            response = self.client.ocr.process(
                model=self.model,
                document={"type": "document_url", "document_url": file_url},
                include_image_base64=False
            )
            
            # Extract content from all pages
            if response.pages:
                pages_content = [page.markdown for page in response.pages]
                ocr_content = "\n\n---\n\n".join(pages_content) if len(pages_content) > 1 else pages_content[0]
            else:
                ocr_content = "No content extracted"
            
            # Process content
            markdown = ocr_content.strip()
            raw_text = self._clean_markdown(ocr_content)
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "data": {"markdown": markdown, "rawText": raw_text},
                "metadata": {
                    "storage_key": storage_key,
                    "model": self.model,
                    "processing_time_ms": int(processing_time * 1000),
                    "request_id": request_id,
                    "file_size_kb": len(storage_service.get_file_data(storage_key)) / 1024
                }
            }
            
        except SDKError as e:
            logger.error(f"Mistral API error: {e}")
            raise OcrProcessingError(f"OCR API failed: {str(e)}")
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise OcrProcessingError(f"Processing failed: {str(e)}")
    
    @staticmethod
    def _clean_markdown(content: str) -> str:
        """Remove markdown syntax for plain text output."""
        cleaned = re.sub(r'[#*`-]\s*', '', content)  # Remove markdown symbols
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)   # Normalize newlines
        return cleaned.strip()

# Singleton
ocr_service = OcrService()

