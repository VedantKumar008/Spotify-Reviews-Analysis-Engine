"""
Ingestion Pipeline Orchestrator
Main pipeline for coordinating data collection from all sources
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from connectors.app_store_connector import AppStoreConnector
from connectors.google_play_connector import GooglePlayConnector
from connectors.reddit_connector import RedditConnector
from connectors.twitter_connector import TwitterConnector
from connectors.forum_scraper import ForumScraper
from storage.mongodb_schema import MongoDBStorage
from storage.s3_storage import S3Storage

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Main ingestion pipeline that coordinates data collection
    from all sources and stores in MongoDB and S3
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ingestion pipeline
        
        Args:
            config: Configuration dictionary for all components
        """
        self.config = config
        self.connectors = {}
        self.mongodb = None
        self.s3 = None
        
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize all connectors and storage components"""
        # Initialize MongoDB storage
        mongodb_config = {
            'mongodb_connection_string': self.config.get('mongodb_connection_string'),
            'mongodb_database': self.config.get('mongodb_database', 'spotify_reviews'),
            'mongodb_collection': self.config.get('mongodb_collection', 'reviews')
        }
        self.mongodb = MongoDBStorage(mongodb_config)
        
        # Initialize S3 storage (optional)
        if self.config.get('s3_enabled', False):
            s3_config = {
                's3_bucket_name': self.config.get('s3_bucket_name'),
                's3_region': self.config.get('s3_region', 'us-east-1'),
                's3_access_key': self.config.get('s3_access_key'),
                's3_secret_key': self.config.get('s3_secret_key'),
                's3_endpoint_url': self.config.get('s3_endpoint_url'),
                's3_prefix': self.config.get('s3_prefix', 'spotify-reviews/raw')
            }
            self.s3 = S3Storage(s3_config)
        
        # Initialize connectors based on config
        if self.config.get('app_store_enabled', True):
            self.connectors['app_store'] = AppStoreConnector({
                'rate_limit_delay': self.config.get('app_store_rate_limit', 2.0),
                'max_retries': self.config.get('max_retries', 3),
                'timeout': self.config.get('timeout', 30)
            })
        
        if self.config.get('google_play_enabled', True):
            self.connectors['google_play'] = GooglePlayConnector({
                'rate_limit_delay': self.config.get('google_play_rate_limit', 1.0),
                'max_retries': self.config.get('max_retries', 3),
                'timeout': self.config.get('timeout', 30)
            })
        
        if self.config.get('reddit_enabled', True) and self.config.get('reddit_client_id'):
            self.connectors['reddit'] = RedditConnector({
                'reddit_client_id': self.config.get('reddit_client_id'),
                'reddit_client_secret': self.config.get('reddit_client_secret'),
                'reddit_user_agent': self.config.get('reddit_user_agent'),
                'rate_limit_delay': self.config.get('reddit_rate_limit', 1.0),
                'max_retries': self.config.get('max_retries', 3),
                'timeout': self.config.get('timeout', 30)
            })
        
        if self.config.get('twitter_enabled', True) and self.config.get('twitter_bearer_token'):
            self.connectors['twitter'] = TwitterConnector({
                'twitter_bearer_token': self.config.get('twitter_bearer_token'),
                'twitter_api_key': self.config.get('twitter_api_key'),
                'twitter_api_secret': self.config.get('twitter_api_secret'),
                'twitter_access_token': self.config.get('twitter_access_token'),
                'twitter_access_token_secret': self.config.get('twitter_access_token_secret'),
                'rate_limit_delay': self.config.get('twitter_rate_limit', 1.0),
                'max_retries': self.config.get('max_retries', 3),
                'timeout': self.config.get('timeout', 30)
            })
        
        if self.config.get('forum_enabled', True):
            self.connectors['forum'] = ForumScraper({
                'rate_limit_delay': self.config.get('forum_rate_limit', 2.0),
                'max_retries': self.config.get('max_retries', 3),
                'timeout': self.config.get('timeout', 30)
            })
        
        logger.info(f"Initialized {len(self.connectors)} connectors")
    
    def run_ingestion(
        self,
        limit_per_source: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete ingestion pipeline
        
        Args:
            limit_per_source: Maximum reviews to fetch per source
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            sources: List of specific sources to ingest (None = all)
            
        Returns:
            Dictionary with ingestion results
        """
        results = {
            'start_time': datetime.utcnow(),
            'sources': {},
            'total_reviews': 0,
            'errors': []
        }
        
        # Connect to storage
        if not self.mongodb.connect():
            error_msg = "Failed to connect to MongoDB"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        if self.s3:
            self.s3.connect()
        
        # Determine which sources to run
        sources_to_run = sources or list(self.connectors.keys())
        
        logger.info(f"Starting ingestion for sources: {sources_to_run}")
        
        # Run ingestion for each source
        for source_name in sources_to_run:
            if source_name not in self.connectors:
                logger.warning(f"Connector not found for source: {source_name}")
                continue
            
            try:
                source_result = self._ingest_source(
                    self.connectors[source_name],
                    source_name,
                    limit_per_source,
                    since,
                    until
                )
                results['sources'][source_name] = source_result
                results['total_reviews'] += source_result['fetched_count']
                
            except Exception as e:
                error_msg = f"Error ingesting from {source_name}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['sources'][source_name] = {
                    'success': False,
                    'error': str(e),
                    'fetched_count': 0
                }
        
        results['end_time'] = datetime.utcnow()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"Ingestion completed. Total reviews: {results['total_reviews']}")
        
        return results
    
    def _ingest_source(
        self,
        connector,
        source_name: str,
        limit: Optional[int],
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Ingest data from a single source
        
        Args:
            connector: Connector instance
            source_name: Name of the source
            limit: Maximum reviews to fetch
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            
        Returns:
            Dictionary with source ingestion results
        """
        result = {
            'success': False,
            'fetched_count': 0,
            'stored_count': 0,
            'error': None
        }
        
        try:
            # Connect to source
            if not connector.connect():
                raise Exception(f"Failed to connect to {source_name}")
            
            logger.info(f"Fetching reviews from {source_name}")
            
            # Fetch reviews
            reviews = connector.fetch_reviews_with_retry(
                limit=limit,
                since=since,
                until=until
            )
            
            result['fetched_count'] = len(reviews)
            
            if not reviews:
                logger.info(f"No reviews fetched from {source_name}")
                result['success'] = True
                return result
            
            # Store in MongoDB
            review_dicts = [review.to_dict() for review in reviews]
            stored_count = self.mongodb.insert_reviews_batch(review_dicts)
            result['stored_count'] = stored_count
            
            # Archive raw data to S3
            if self.s3:
                self.s3.upload_raw_data(
                    source_name,
                    review_dicts,
                    filename=f"{source_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                )
            
            result['success'] = True
            logger.info(f"Successfully ingested {stored_count} reviews from {source_name}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error ingesting from {source_name}: {str(e)}")
        
        finally:
            # Disconnect from source
            connector.disconnect()
        
        return result
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ingested data
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_reviews': self.mongodb.get_review_count(),
            'source_distribution': self.mongodb.get_source_distribution(),
            'last_ingestion': datetime.utcnow().isoformat()
        }
        
        return stats
    
    def disconnect(self) -> None:
        """Disconnect from all storage components"""
        if self.mongodb:
            self.mongodb.disconnect()
        if self.s3:
            self.s3.disconnect()
