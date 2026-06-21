"""
MongoDB Data Storage Schema
Defines the schema for storing review data in MongoDB
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)


class ReviewDocument(BaseModel):
    """Pydantic model for review document"""
    source: str
    review_id: str
    content: str
    rating: Optional[float] = None
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MongoDBStorage:
    """
    MongoDB storage layer for review data
    Handles CRUD operations and indexing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MongoDB connection
        
        Args:
            config: Configuration dictionary with MongoDB connection details
        """
        self.connection_string = config.get('mongodb_connection_string', 'mongodb://localhost:27017')
        self.database_name = config.get('mongodb_database', 'spotify_reviews')
        self.collection_name = config.get('mongodb_collection', 'reviews')
        
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            
            # Create indexes
            self._create_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _create_indexes(self) -> None:
        """Create indexes for efficient querying"""
        try:
            # Compound index on source and review_id for uniqueness
            self.collection.create_index(
                [('source', ASCENDING), ('review_id', ASCENDING)],
                unique=True,
                name='source_review_id_unique'
            )
            
            # Index on timestamp for time-based queries
            self.collection.create_index(
                [('timestamp', DESCENDING)],
                name='timestamp_index'
            )
            
            # Index on source for filtering
            self.collection.create_index(
                [('source', ASCENDING)],
                name='source_index'
            )
            
            # Index on rating for analysis
            self.collection.create_index(
                [('rating', ASCENDING)],
                name='rating_index'
            )
            
            # Index on created_at for tracking
            self.collection.create_index(
                [('created_at', DESCENDING)],
                name='created_at_index'
            )
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {str(e)}")
    
    def insert_review(self, review_data: Dict[str, Any]) -> bool:
        """
        Insert a single review into MongoDB
        
        Args:
            review_data: Dictionary containing review data
            
        Returns:
            bool: True if insert successful, False otherwise
        """
        try:
            # Add timestamps
            review_data['created_at'] = datetime.utcnow()
            review_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.insert_one(review_data)
            logger.debug(f"Inserted review with ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.debug(f"Review already exists: {review_data.get('review_id')}")
            return False
            
        except Exception as e:
            logger.error(f"Error inserting review: {str(e)}")
            return False
    
    def insert_reviews_batch(self, reviews: List[Dict[str, Any]]) -> int:
        """
        Insert multiple reviews in batch
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            int: Number of successfully inserted reviews
        """
        try:
            # Add timestamps
            timestamp = datetime.utcnow()
            for review in reviews:
                review['created_at'] = timestamp
                review['updated_at'] = timestamp
            
            result = self.collection.insert_many(reviews, ordered=False)
            inserted_count = len(result.inserted_ids)
            logger.info(f"Inserted {inserted_count} reviews in batch")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error in batch insert: {str(e)}")
            # Try inserting one by one
            inserted_count = 0
            for review in reviews:
                if self.insert_review(review):
                    inserted_count += 1
            return inserted_count
    
    def get_review_by_id(self, source: str, review_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific review by source and review_id
        
        Args:
            source: Data source type
            review_id: Review ID
            
        Returns:
            Review document or None if not found
        """
        try:
            review = self.collection.find_one({
                'source': source,
                'review_id': review_id
            })
            return review
            
        except Exception as e:
            logger.error(f"Error fetching review: {str(e)}")
            return None
    
    def get_reviews_by_source(
        self,
        source: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get reviews by source with optional filters
        
        Args:
            source: Data source type
            limit: Maximum number of reviews to return
            since: Only return reviews after this date
            until: Only return reviews before this date
            
        Returns:
            List of review documents
        """
        try:
            query = {'source': source}
            
            # Add date filters
            if since or until:
                query['timestamp'] = {}
                if since:
                    query['timestamp']['$gte'] = since
                if until:
                    query['timestamp']['$lte'] = until
            
            cursor = self.collection.find(query).sort('timestamp', DESCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            reviews = list(cursor)
            return reviews
            
        except Exception as e:
            logger.error(f"Error fetching reviews by source: {str(e)}")
            return []
    
    def get_all_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all reviews with optional filters
        
        Args:
            limit: Maximum number of reviews to return
            since: Only return reviews after this date
            until: Only return reviews before this date
            
        Returns:
            List of review documents
        """
        try:
            query = {}
            
            # Add date filters
            if since or until:
                query['timestamp'] = {}
                if since:
                    query['timestamp']['$gte'] = since
                if until:
                    query['timestamp']['$lte'] = until
            
            cursor = self.collection.find(query).sort('timestamp', DESCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            reviews = list(cursor)
            return reviews
            
        except Exception as e:
            logger.error(f"Error fetching all reviews: {str(e)}")
            return []
    
    def get_review_count(self, source: Optional[str] = None) -> int:
        """
        Get count of reviews
        
        Args:
            source: Optional source filter
            
        Returns:
            Count of reviews
        """
        try:
            query = {}
            if source:
                query['source'] = source
            
            count = self.collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"Error counting reviews: {str(e)}")
            return 0
    
    def get_source_distribution(self) -> Dict[str, int]:
        """
        Get distribution of reviews by source
        
        Returns:
            Dictionary with source as key and count as value
        """
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$source',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            results = self.collection.aggregate(pipeline)
            distribution = {doc['_id']: doc['count'] for doc in results}
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting source distribution: {str(e)}")
            return {}
    
    def delete_review(self, source: str, review_id: str) -> bool:
        """
        Delete a specific review
        
        Args:
            source: Data source type
            review_id: Review ID
            
        Returns:
            bool: True if delete successful, False otherwise
        """
        try:
            result = self.collection.delete_one({
                'source': source,
                'review_id': review_id
            })
            
            if result.deleted_count > 0:
                logger.info(f"Deleted review: {review_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting review: {str(e)}")
            return False
    
    def delete_reviews_by_source(self, source: str) -> int:
        """
        Delete all reviews from a specific source
        
        Args:
            source: Data source type
            
        Returns:
            Number of deleted reviews
        """
        try:
            result = self.collection.delete_many({'source': source})
            logger.info(f"Deleted {result.deleted_count} reviews from {source}")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting reviews by source: {str(e)}")
            return 0
    
    def update_review(self, source: str, review_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a specific review
        
        Args:
            source: Data source type
            review_id: Review ID
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            updates['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'source': source, 'review_id': review_id},
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated review: {review_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating review: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
