import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.storage_service import storage_service
from app.services.ocr_service import ocr_service
from app.api.v1.schemas.parse import ParseSuccessResponse
from app.exceptions import FileUploadError, OcrProcessingError, PromptNotFoundError, FileValidationError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=ParseSuccessResponse,
    summary="Parse a Document",
    description="Uploads a document, processes it with Mistral OCR, and returns the extracted content."
)
async def parse_document(
    file: UploadFile = File(..., description="The document file (PDF, PNG, JPG) to process."),
    promptId: str = Form(..., description="The ID of the prompt to use for processing.")
):
    """
    Handles the core document parsing workflow.
    """
    storage_key = None
    try:
        # Step 1: Upload to MinIO (for local storage/backup)
        logger.info(f"Uploading file: {file.filename}")
        upload_metadata = await storage_service.upload_file(file)
        storage_key = upload_metadata["storage_key"]
        original_filename = upload_metadata["original_filename"]
        logger.info(f"File uploaded to MinIO. Storage key: {storage_key}")

        # Step 2: Process with OCR (uploads to Mistral internally)
        logger.info(f"Processing document with prompt: {promptId}")
        result = ocr_service.process_document(storage_key, promptId, original_filename)
        return result

    except (FileUploadError, OcrProcessingError, PromptNotFoundError, FileValidationError) as e:
        logger.error(f"Client error during parsing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error during parsing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")
    finally:
        # Clean up MinIO storage
        if storage_key:
            logger.info(f"Cleaning up storage key: {storage_key}")
            deleted = storage_service.delete_file(storage_key)
            if not deleted:
                logger.warning(f"Failed to clean up file: {storage_key}")
