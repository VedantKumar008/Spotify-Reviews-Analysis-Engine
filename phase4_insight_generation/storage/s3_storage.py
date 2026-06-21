"""
S3 Data Lake Storage
Handles storage of raw data in AWS S3 or Google Cloud Storage
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging
import json
import os

logger = logging.getLogger(__name__)


class S3Storage:
    """
    S3 storage layer for raw data archival
    Supports AWS S3 and Google Cloud Storage (via S3-compatible API)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize S3 connection
        
        Args:
            config: Configuration dictionary with S3 connection details
        """
        self.bucket_name = config.get('s3_bucket_name')
        self.region = config.get('s3_region', 'us-east-1')
        self.access_key = config.get('s3_access_key')
        self.secret_key = config.get('s3_secret_key')
        self.endpoint_url = config.get('s3_endpoint_url')  # For GCS or other S3-compatible services
        self.prefix = config.get('s3_prefix', 'spotify-reviews/raw')
        
        self.s3_client = None
        self.bucket = None
    
    def connect(self) -> bool:
        """
        Establish connection to S3
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            s3_config = {
                'region_name': self.region,
                'aws_access_key_id': self.access_key,
                'aws_secret_access_key': self.secret_key
            }
            
            if self.endpoint_url:
                s3_config['endpoint_url'] = self.endpoint_url
            
            self.s3_client = boto3.client('s3', **s3_config)
            
            # Test connection by checking if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to connect to S3: {str(e)}")
            return False
    
    def upload_raw_data(
        self,
        source: str,
        data: Any,
        filename: Optional[str] = None
    ) -> bool:
        """
        Upload raw data to S3
        
        Args:
            source: Data source type
            data: Data to upload (can be dict, list, or string)
            filename: Optional custom filename
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f"{source}_{timestamp}.json"
            
            # Generate S3 key
            key = f"{self.prefix}/{source}/{filename}"
            
            # Convert data to JSON string
            if isinstance(data, (dict, list)):
                content = json.dumps(data, default=str, indent=2)
            else:
                content = str(data)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType='application/json'
            )
            
            logger.info(f"Uploaded raw data to S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return False
    
    def download_raw_data(self, source: str, filename: str) -> Optional[Any]:
        """
        Download raw data from S3
        
        Args:
            source: Data source type
            filename: Filename to download
            
        Returns:
            Downloaded data or None if error
        """
        try:
            key = f"{self.prefix}/{source}/{filename}"
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            
            logger.info(f"Downloaded raw data from S3: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return None
    
    def list_files(self, source: Optional[str] = None) -> List[str]:
        """
        List files in S3 storage
        
        Args:
            source: Optional source filter
            
        Returns:
            List of file keys
        """
        try:
            prefix = f"{self.prefix}/"
            if source:
                prefix = f"{self.prefix}/{source}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def delete_file(self, source: str, filename: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            source: Data source type
            filename: Filename to delete
            
        Returns:
            bool: True if delete successful, False otherwise
        """
        try:
            key = f"{self.prefix}/{source}/{filename}"
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Deleted file from S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close S3 connection (no explicit close needed for boto3)"""
        pass
