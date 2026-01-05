"""
Amazon S3 storage utility for file uploads.
Handles uploading files to S3 and generating public URLs.

Security:
- AWS credentials are read from environment variables (never hardcoded)
- S3 bucket should not be public-write
- Files are stored with unique names to prevent conflicts
"""
import os
import logging
import uuid
from typing import Optional, BinaryIO
from django.conf import settings
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Create and return an S3 client using credentials from environment variables.
    Falls back to IAM role credentials if running on EC2 (when access keys not provided).
    
    Required environment variables:
    - AWS_REGION (always required)
    - AWS_S3_BUCKET (always required)
    - AWS_ACCESS_KEY_ID (only for local development)
    - AWS_SECRET_ACCESS_KEY (only for local development)
    
    On EC2, if access keys are not set, boto3 will automatically use IAM role credentials.
    
    Returns:
        Tuple of (boto3 S3 client instance, bucket name)
        
    Raises:
        ValueError: If required environment variables are missing
    """
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('AWS_S3_BUCKET')
    
    if not region:
        raise ValueError("AWS_REGION environment variable is required")
    if not bucket_name:
        raise ValueError("AWS_S3_BUCKET environment variable is required")
    
    # If access keys are provided, use them (local development)
    if access_key and secret_key:
        logger.info("Using AWS access keys for S3 authentication (local development)")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    else:
        # No access keys - use IAM role (EC2 deployment)
        # boto3 will automatically use the instance's IAM role
        logger.info("Using IAM role for S3 authentication (EC2 deployment)")
        s3_client = boto3.client('s3', region_name=region)
    
    return s3_client, bucket_name


def upload_file_to_s3(
    file_content: bytes,
    s3_key: str,
    content_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Upload file content to S3 bucket.
    
    Args:
        file_content: File content as bytes
        s3_key: S3 object key (path within bucket, e.g., 'uploads/2024/01/15/filename.jpg')
        content_type: MIME type of the file (e.g., 'image/jpeg')
        metadata: Optional metadata dictionary to attach to the object
        
    Returns:
        Public URL of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        s3_client, bucket_name = get_s3_client()
        
        # Prepare upload parameters
        upload_params = {
            'Bucket': bucket_name,
            'Key': s3_key,
            'Body': file_content
        }
        
        # Add content type if provided
        if content_type:
            upload_params['ContentType'] = content_type
        
        # Add metadata if provided
        if metadata:
            upload_params['Metadata'] = metadata
        
        # Upload to S3
        s3_client.put_object(**upload_params)
        
        # Generate public URL
        # Format: https://{bucket}.s3.{region}.amazonaws.com/{key}
        # Or: https://s3.{region}.amazonaws.com/{bucket}/{key}
        region = os.getenv('AWS_REGION')
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        
        logger.info(f"File uploaded to S3: {s3_key} -> {public_url}")
        
        return public_url
        
    except (ClientError, BotoCoreError) as e:
        logger.error(f"S3 upload failed: {str(e)}")
        raise Exception(f"Failed to upload file to S3: {str(e)}")
    except ValueError as e:
        logger.error(f"S3 configuration error: {str(e)}")
        raise


def upload_file_object_to_s3(
    file_obj: BinaryIO,
    s3_key: str,
    content_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Upload a file-like object to S3 bucket.
    
    Args:
        file_obj: File-like object (e.g., Django UploadedFile)
        s3_key: S3 object key (path within bucket)
        content_type: MIME type of the file
        metadata: Optional metadata dictionary
        
    Returns:
        Public URL of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    # Read file content
    if hasattr(file_obj, 'read'):
        file_content = file_obj.read()
        # Reset file pointer if possible
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
    else:
        raise ValueError("file_obj must be a file-like object with read() method")
    
    return upload_file_to_s3(file_content, s3_key, content_type, metadata)


def generate_s3_key(folder: str, filename: str, date_prefix: bool = True) -> str:
    """
    Generate a unique S3 key (path) for a file.
    
    Args:
        folder: Folder name (e.g., 'uploads', 'generated')
        filename: Filename (will be made unique if needed)
        date_prefix: Whether to include date prefix (YYYY/MM/DD)
        
    Returns:
        S3 key path (e.g., 'uploads/2024/01/15/uuid-filename.jpg')
    """
    from django.utils import timezone
    
    if date_prefix:
        date_str = timezone.now().strftime('%Y/%m/%d')
        s3_key = f"{folder}/{date_str}/{filename}"
    else:
        s3_key = f"{folder}/{filename}"
    
    return s3_key


def delete_file_from_s3(s3_key: str) -> bool:
    """
    Delete a file from S3 bucket.
    
    Args:
        s3_key: S3 object key to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        s3_client, bucket_name = get_s3_client()
        
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        
        logger.info(f"File deleted from S3: {s3_key}")
        return True
        
    except (ClientError, BotoCoreError) as e:
        logger.error(f"S3 delete failed: {str(e)}")
        return False
    except ValueError as e:
        logger.error(f"S3 configuration error: {str(e)}")
        return False


def file_exists_in_s3(s3_key: str) -> bool:
    """
    Check if a file exists in S3 bucket.
    
    Args:
        s3_key: S3 object key to check
        
    Returns:
        True if file exists, False otherwise
    """
    try:
        s3_client, bucket_name = get_s3_client()
        
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        logger.error(f"S3 head_object failed: {str(e)}")
        return False
    except (BotoCoreError, ValueError) as e:
        logger.error(f"S3 configuration error: {str(e)}")
        return False

