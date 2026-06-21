"""
Base Connector Class for Data Source Connectors
Provides common functionality for all data source connectors
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Enumeration of supported data source types"""
    APP_STORE = "app_store"
    GOOGLE_PLAY = "google_play"
    REDDIT = "reddit"
    TWITTER = "twitter"
    FORUM = "forum"
    WEB_SCRAPER = "web_scraper"


@dataclass
class ReviewData:
    """Standardized review data structure"""
    source: DataSourceType
    review_id: str
    content: str
    rating: Optional[float] = None
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert review data to dictionary"""
        return {
            "source": self.source.value,
            "review_id": self.review_id,
            "content": self.content,
            "rating": self.rating,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "url": self.url,
            "metadata": self.metadata or {}
        }


class BaseConnector(ABC):
    """
    Abstract base class for all data source connectors
    Provides common functionality and enforces interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with configuration
        
        Args:
            config: Configuration dictionary for the connector
        """
        self.config = config
        self.source_type = self._get_source_type()
        self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
        self.max_retries = config.get('max_retries', 3)
        self.timeout = config.get('timeout', 30)
        
    @abstractmethod
    def _get_source_type(self) -> DataSourceType:
        """Return the data source type for this connector"""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def fetch_reviews(
        self, 
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch reviews from the data source
        
        Args:
            limit: Maximum number of reviews to fetch
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            
        Returns:
            List of ReviewData objects
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the data source"""
        pass
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting by sleeping for configured delay"""
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)
    
    def _retry_on_failure(self, func, *args, **kwargs) -> Any:
        """
        Retry a function on failure with exponential backoff
        
        Args:
            func: Function to retry
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {self.source_type.value}. "
                    f"Retrying in {wait_time}s. Error: {str(e)}"
                )
                time.sleep(wait_time)
        
        raise last_exception
    
    def validate_review(self, review: ReviewData) -> bool:
        """
        Validate a review before processing
        
        Args:
            review: ReviewData object to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not review.content or not review.content.strip():
            logger.warning(f"Empty content for review {review.review_id}")
            return False
        
        if not review.review_id:
            logger.warning("Missing review_id")
            return False
        
        return True
    
    def fetch_reviews_with_retry(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch reviews with automatic retry logic
        
        Args:
            limit: Maximum number of reviews to fetch
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            
        Returns:
            List of ReviewData objects
        """
        try:
            reviews = self._retry_on_failure(
                self.fetch_reviews,
                limit=limit,
                since=since,
                until=until
            )
            
            # Validate and filter reviews
            valid_reviews = [
                review for review in reviews
                if self.validate_review(review)
            ]
            
            logger.info(
                f"Fetched {len(reviews)} reviews from {self.source_type.value}, "
                f"{len(valid_reviews)} valid after validation"
            )
            
            return valid_reviews
            
        except Exception as e:
            logger.error(f"Failed to fetch reviews from {self.source_type.value}: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
