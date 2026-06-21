"""
Twitter Connector
Fetches tweets and conversations from X/Twitter related to Spotify discovery
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import tweepy
import logging

from .base_connector import BaseConnector, ReviewData, DataSourceType

logger = logging.getLogger(__name__)


class TwitterConnector(BaseConnector):
    """
    Connector for fetching Spotify-related tweets from X/Twitter
    Uses Twitter API v2
    """
    
    SEARCH_QUERIES = [
        'spotify discovery',
        'spotify recommendations',
        'spotify discover weekly',
        'spotify ai dj',
        'spotify daily mix',
        'spotify music discovery',
        'spotify algorithm',
        'spotify new music'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bearer_token = config.get('twitter_bearer_token')
        self.api_key = config.get('twitter_api_key')
        self.api_secret = config.get('twitter_api_secret')
        self.access_token = config.get('twitter_access_token')
        self.access_token_secret = config.get('twitter_access_token_secret')
        self.search_queries = config.get('search_queries', self.SEARCH_QUERIES)
        self.client = None
    
    def _get_source_type(self) -> DataSourceType:
        return DataSourceType.TWITTER
    
    def connect(self) -> bool:
        """Connect to Twitter API"""
        try:
            if self.bearer_token:
                # Use bearer token for app-only auth
                self.client = tweepy.Client(bearer_token=self.bearer_token)
            elif self.api_key and self.api_secret:
                # Use API key/secret for user context
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
            else:
                logger.error("No Twitter credentials provided")
                return False
            
            # Test connection
            self.client.get_me()
            logger.info("Successfully connected to Twitter API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Twitter: {str(e)}")
            return False
    
    def fetch_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch tweets from Twitter based on search queries
        
        Args:
            limit: Maximum number of tweets to fetch
            since: Only fetch tweets after this date
            until: Only fetch tweets before this date
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        total_limit = limit or 500
        tweets_per_query = min(100, total_limit // len(self.search_queries))
        
        logger.info(f"Fetching Twitter tweets for {len(self.search_queries)} queries")
        
        for query in self.search_queries:
            if len(reviews) >= total_limit:
                break
            
            try:
                logger.info(f"Searching Twitter for: {query}")
                
                # Build query with Spotify-related keywords
                search_query = f"{query} -is:retweet lang:en"
                
                # Set time range for search
                start_time = since.isoformat() if since else None
                end_time = until.isoformat() if until else None
                
                tweets = self.client.search_recent_tweets(
                    query=search_query,
                    max_results=min(100, tweets_per_query),
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                    expansions=['author_id'],
                    start_time=start_time,
                    end_time=end_time
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        try:
                            tweet_data = self._parse_tweet(tweet, query)
                            reviews.append(tweet_data)
                            
                            if len(reviews) >= total_limit:
                                break
                                
                        except Exception as e:
                            logger.warning(f"Error parsing tweet: {str(e)}")
                            continue
                
                logger.info(f"Fetched {len(tweets.data) if tweets.data else 0} tweets for '{query}'")
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error searching for '{query}': {str(e)}")
                continue
        
        if limit:
            reviews = reviews[:limit]
        
        logger.info(f"Fetched {len(reviews)} Twitter tweets")
        return reviews
    
    def _parse_tweet(self, tweet, query: str) -> ReviewData:
        """Parse a Twitter tweet into ReviewData"""
        review_id = f"tweet_{tweet.id}"
        content = tweet.text
        
        # Use public metrics as proxy for rating
        metrics = tweet.public_metrics or {}
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # Normalize to 1-5 scale based on engagement
        engagement_score = likes + (retweets * 2) + (replies * 1.5)
        rating = min(5, max(1, (engagement_score / 50) + 1)) if engagement_score > 0 else None
        
        # Author
        author = str(tweet.author_id) if tweet.author_id else None
        
        # Timestamp
        timestamp = tweet.created_at
        
        # URL
        url = f"https://twitter.com/i/web/status/{tweet.id}"
        
        metadata = {
            'search_query': query,
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'quote_count': metrics.get('quote_count', 0),
            'impression_count': metrics.get('impression_count', 0)
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
