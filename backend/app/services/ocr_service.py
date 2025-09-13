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
    """OCR service using Mistral API with direct file upload."""
    
    def __init__(self):
        if not settings.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is required")
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        self.model = "mistral-ocr-latest"
        logger.info("OcrService initialized")
    
    def process_document(self, storage_key: str, prompt_id: str, original_filename: str) -> Dict[str, Any]:
        """
        Process document by uploading directly to Mistral.
        
        Args:
            storage_key: Key in MinIO storage
            prompt_id: ID of the prompt to use
            original_filename: Original filename (needed for Mistral upload)
        """
        start_time = time.time()
        request_id = f"ocr_{uuid.uuid4().hex[:8]}"
        uploaded_file_id = None
        
        try:
            # Step 1: Validate prompt
            prompts = load_prompts()
            if not any(p["id"] == prompt_id for p in prompts):
                raise PromptNotFoundError(f"Prompt '{prompt_id}' not found")
            
            # Step 2: Get file data from MinIO
            logger.info(f"Retrieving file from storage: {storage_key}")
            file_data = storage_service.get_file_data(storage_key)
            
            # Step 3: Upload file directly to Mistral
            logger.info(f"Uploading file to Mistral: {original_filename}")
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": original_filename,
                    "content": file_data,
                },
                purpose="ocr"
            )
            uploaded_file_id = uploaded_file.id
            logger.info(f"File uploaded to Mistral with ID: {uploaded_file_id}")
            
            # Step 4: Get signed URL from Mistral
            signed_url_response = self.client.files.get_signed_url(file_id=uploaded_file_id)
            signed_url = signed_url_response.url
            logger.info(f"Got signed URL from Mistral")
            
            # Step 5: Process with OCR
            response = self.client.ocr.process(
                model=self.model,
                document={
                    "type": "document_url",
                    "document_url": signed_url
                },
                include_image_base64=False
            )
            
            # Step 6: Extract content
            if hasattr(response, 'pages') and response.pages:
                pages_content = [page.markdown for page in response.pages]
                ocr_content = "\n\n---\n\n".join(pages_content) if len(pages_content) > 1 else pages_content[0]
            elif hasattr(response, 'content'):
                ocr_content = response.content
            else:
                ocr_content = "No content extracted"
            
            # Process content
            markdown = ocr_content.strip()
            raw_text = self._clean_markdown(ocr_content)
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "data": {
                    "markdown": markdown,
                    "rawText": raw_text
                },
                "metadata": {
                    "storage_key": storage_key,
                    "model": self.model,
                    "processing_time_ms": int(processing_time * 1000),
                    "request_id": request_id,
                    "file_size_kb": len(file_data) / 1024
                }
            }
            
        except SDKError as e:
            logger.error(f"Mistral API error: {e}")
            raise OcrProcessingError(f"OCR API failed: {str(e)}")
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise OcrProcessingError(f"Processing failed: {str(e)}")
        finally:
            if uploaded_file_id:
                try:
                    logger.info(f"Cleaning up Mistral file: {uploaded_file_id}")
                    self.client.files.delete(file_id=uploaded_file_id)
                except Exception as e:
                    logger.warning(f"Failed to delete Mistral file {uploaded_file_id}: {e}")
    
    @staticmethod
    def _clean_markdown(content: str) -> str:
        """Remove markdown syntax for plain text output."""
        cleaned = re.sub(r'[#*`-]\s*', '', content)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        return cleaned.strip()

# Singleton
ocr_service = OcrService()
