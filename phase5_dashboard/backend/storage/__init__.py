"""
Storage Package
"""

from .mongodb_schema import MongoDBStorage, ReviewDocument

# S3Storage is available but not imported by default to avoid boto3 dependency
# Uncomment the following line if you need S3 storage functionality:
# from .s3_storage import S3Storage

__all__ = [
    'MongoDBStorage',
    'ReviewDocument',
    # 'S3Storage'  # Uncomment if needed
]
