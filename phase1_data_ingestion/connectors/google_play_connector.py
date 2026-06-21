"""
Google Play Store Reviews Connector
Fetches reviews from Google Play Store for Spotify app
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from google_play_scraper import Sort, reviews as gp_reviews
import logging

from .base_connector import BaseConnector, ReviewData, DataSourceType

logger = logging.getLogger(__name__)


class GooglePlayConnector(BaseConnector):
    """
    Connector for fetching reviews from Google Play Store
    Uses google-play-scraper library
    """
    
    SPOTIFY_PACKAGE_NAME = "com.spotify.music"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.package_name = config.get('package_name', self.SPOTIFY_PACKAGE_NAME)
        self.language = config.get('language', 'en')
        self.country = config.get('country', 'us')
    
    def _get_source_type(self) -> DataSourceType:
        return DataSourceType.GOOGLE_PLAY
    
    def connect(self) -> bool:
        """Test connection to Google Play Store"""
        try:
            # Try to fetch a small batch of reviews to test connection
            result, _ = gp_reviews(
                self.package_name,
                lang=self.language,
                country=self.country,
                sort=Sort.NEWEST,
                count=1
            )
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to connect to Google Play Store: {str(e)}")
            return False
    
    def fetch_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch reviews from Google Play Store
        
        Args:
            limit: Maximum number of reviews to fetch
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        count = limit or 1000
        continuation_token = None
        
        logger.info(f"Fetching up to {count} reviews from Google Play Store")
        
        while len(reviews) < count:
            try:
                batch_size = min(100, count - len(reviews))
                
                result, continuation_token = gp_reviews(
                    self.package_name,
                    lang=self.language,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=batch_size,
                    continuation_token=continuation_token
                )
                
                if not result:
                    logger.info("No more reviews available")
                    break
                
                # Parse and filter reviews
                for review in result:
                    try:
                        review_data = self._parse_review(review)
                        
                        # Apply date filters
                        if since and review_data.timestamp and review_data.timestamp < since:
                            continue
                        if until and review_data.timestamp and review_data.timestamp > until:
                            continue
                        
                        reviews.append(review_data)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing review: {str(e)}")
                        continue
                
                logger.info(f"Fetched {len(reviews)} reviews so far")
                
                if not continuation_token:
                    logger.info("Reached end of reviews")
                    break
                
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching batch: {str(e)}")
                break
        
        return reviews
    
    def _parse_review(self, review: Dict[str, Any]) -> ReviewData:
        """Parse a single review from Google Play Store"""
        review_id = review.get('reviewId')
        content = review.get('content', '')
        rating = review.get('score')
        author = review.get('userName')
        
        # Timestamp
        timestamp = None
        at = review.get('at')
        if at:
            try:
                timestamp = datetime.fromisoformat(at.replace('Z', '+00:00'))
            except:
                pass
        
        # Version
        version = review.get('appVersion')
        
        # Device
        device = review.get('device')
        
        # URL
        url = f"https://play.google.com/store/apps/details?id={self.package_name}&reviewId={review_id}"
        
        metadata = {
            'app_version': version,
            'device': device,
            'language': self.language,
            'country': self.country,
            'thumbs_up_count': review.get('thumbsUpCount', 0)
        }
        
        return ReviewData(
            source=self.source_type,
            review_id=review_id,
            content=content,
            rating=rating,
            author=author,
            timestamp=timestamp,
            url=url,
            metadata=metadata
        )
    
    def disconnect(self) -> None:
        """No persistent connection to close"""
        pass
