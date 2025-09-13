from __future__ import annotations
import logging
import typing
import uuid
from datetime import datetime, timezone
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from app.core.config import settings
from app.utils.file_helpers import get_file_size_kb, validate_file_type, sanitize_filename
from app.exceptions import (
    FileUploadError,
    FileNotFoundError,
    FileValidationError,
    StorageConnectionError,
)

# Configure logger for this module
logger = logging.getLogger(__name__)

class StorageService:
    """
    Service for handling file operations with MinIO object storage.
    """
    
    def __init__(self):
        logger.info("Initializing StorageService")
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False  # Set to True for HTTPS
            )
            self.bucket_name = settings.MINIO_BUCKET_NAME
            logger.info(f"MinIO client configured for endpoint: {settings.MINIO_ENDPOINT}, bucket: {self.bucket_name}")
            self._ensure_bucket_exists()
            logger.info("StorageService initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize StorageService: {e}", exc_info=True)
            raise StorageConnectionError(f"Failed to initialize storage service: {str(e)}")
    
    def _ensure_bucket_exists(self) -> None:
        """
        Create the bucket if it doesn't exist.
        """
        logger.debug(f"Checking if bucket '{self.bucket_name}' exists")
        try:
            if not self.client.bucket_exists(self.bucket_name):
                logger.info(f"Bucket '{self.bucket_name}' does not exist, creating it")
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Successfully created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            logger.error(f"S3Error while checking/creating bucket '{self.bucket_name}': {e}", exc_info=True)
            raise StorageConnectionError(f"S3 error while managing bucket: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while ensuring bucket exists: {e}", exc_info=True)
            raise StorageConnectionError(f"Unexpected error managing bucket: {str(e)}")
    
    async def upload_file(self, file: UploadFile) -> dict:
        """
        Upload a file to MinIO and return metadata.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            dict: File metadata including storage_key, original_filename, etc.
            
        Raises:
            ValueError: If file type is not supported
            Exception: If upload fails
        """
        upload_start_time = datetime.now(timezone.utc)
        logger.info(f"Starting file upload for: {file.filename}")
        
        try:
            # Reset file pointer to beginning
            await file.seek(0)
            logger.debug("File pointer reset to beginning")
            
            # Validate file type
            logger.debug(f"Validating file type for: {file.filename}")
            if not file.filename:
                raise FileValidationError("Filename is required but was not provided")
            validate_file_type(file.file, file.filename)
            logger.debug("File type validation passed")
            
            # Generate unique storage key
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            # file.filename is guaranteed to be not None by validation above
            sanitized_name = sanitize_filename(file.filename)
            storage_key = f"{timestamp}_{unique_id}_{sanitized_name}"
            logger.debug(f"Generated storage key: {storage_key}")
            
            # Get file size
            file_size_kb = get_file_size_kb(file.file)
            logger.debug(f"File size: {file_size_kb} KB")
            
            # Reset file pointer again before upload
            await file.seek(0)
            
            # Upload to MinIO
            logger.info(f"Uploading file to MinIO with key: {storage_key}")
            # Use application/octet-stream as fallback if content_type is None
            content_type = file.content_type or "application/octet-stream"
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
                data=file.file,
                length=int(file_size_kb * 1024),  # Convert back to bytes
                content_type=content_type
            )
            
            upload_duration = (datetime.now(timezone.utc) - upload_start_time).total_seconds()
            
            # Return metadata
            metadata = {
                "storage_key": storage_key,
                "original_filename": file.filename,
                "file_size_kb": round(file_size_kb, 2),
                "content_type": file.content_type,
                "upload_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"File upload completed successfully in {upload_duration:.2f}s. "
                       f"Storage key: {storage_key}, Size: {file_size_kb:.2f} KB")
            
            return metadata
            
        except ValueError as e:
            logger.warning(f"File validation failed for '{file.filename}': {e}")
            # Re-raise as FileValidationError
            raise FileValidationError(str(e))
        except S3Error as e:
            logger.error(f"S3Error during file upload for '{file.filename}': {e}", exc_info=True)
            raise FileUploadError(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during upload of '{file.filename}': {e}", exc_info=True)
            raise FileUploadError(f"Unexpected error during file upload: {str(e)}")
    
    def get_file_url(self, storage_key: str, expires_in_hours: int = 1) -> str:
        """
        Generate a presigned URL to access the file.
        
        Args:
            storage_key: The unique key of the stored file
            expires_in_hours: How long the URL should be valid (default: 1 hour)
            
        Returns:
            str: Presigned URL for file access
        """
        logger.info(f"Generating presigned URL for file: {storage_key}, expires in {expires_in_hours} hours")
        
        try:
            from datetime import timedelta
            
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
                expires=timedelta(hours=expires_in_hours)
            )
            
            logger.info(f"Presigned URL generated successfully for: {storage_key}")
            logger.debug(f"Generated URL (first 50 chars): {url[:50]}...")
            
            return url
        except S3Error as e:
            logger.error(f"S3Error generating presigned URL for '{storage_key}': {e}", exc_info=True)
            raise FileNotFoundError(f"Failed to generate file URL: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL for '{storage_key}': {e}", exc_info=True)
            raise StorageConnectionError(f"Failed to generate file URL: {str(e)}")
    
    def get_file_data(self, storage_key: str) -> bytes:
        """
        Retrieve file data directly from storage.
        
        Args:
            storage_key: The unique key of the stored file
            
        Returns:
            bytes: File content as bytes
        """
        logger.info(f"Retrieving file data for: {storage_key}")
        
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=storage_key
            )
            data = response.read()
            response.close()
            response.release_conn()
            
            data_size_kb = len(data) / 1024
            logger.info(f"File data retrieved successfully for '{storage_key}': {data_size_kb:.2f} KB")
            
            return data
        except S3Error as e:
            logger.error(f"S3Error retrieving file data for '{storage_key}': {e}", exc_info=True)
            raise FileNotFoundError(f"Failed to retrieve file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving file data for '{storage_key}': {e}", exc_info=True)
            raise StorageConnectionError(f"Failed to retrieve file: {str(e)}")
    
    def delete_file(self, storage_key: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            storage_key: The unique key of the stored file
            
        Returns:
            bool: True if deletion was successful
        """
        logger.info(f"Attempting to delete file: {storage_key}")
        
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=storage_key
            )
            logger.info(f"File deleted successfully: {storage_key}")
            return True
        except S3Error as e:
            logger.error(f"S3Error deleting file '{storage_key}': {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file '{storage_key}': {e}", exc_info=True)
            return False
    
    def file_exists(self, storage_key: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            storage_key: The unique key of the stored file
            
        Returns:
            bool: True if file exists
        """
        logger.debug(f"Checking if file exists: {storage_key}")
        
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=storage_key
            )
            logger.debug(f"File '{storage_key}' exists in MinIO")
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.debug(f"File '{storage_key}' does not exist in MinIO")
            else:
                logger.warning(f"S3Error checking file existence for '{storage_key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking file existence for '{storage_key}': {e}", exc_info=True)
            return False

# Create a singleton instance
logger.info("Creating StorageService singleton instance")
storage_service = StorageService()
logger.info("StorageService singleton instance created successfully")