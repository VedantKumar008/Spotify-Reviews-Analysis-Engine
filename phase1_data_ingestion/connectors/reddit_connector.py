"""
Reddit Connector
Fetches discussions and comments from Reddit related to Spotify
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import praw
import logging

from .base_connector import BaseConnector, ReviewData, DataSourceType

logger = logging.getLogger(__name__)


class RedditConnector(BaseConnector):
    """
    Connector for fetching Spotify-related discussions from Reddit
    Uses PRAW (Python Reddit API Wrapper)
    """
    
    DEFAULT_SUBREDDITS = [
        'spotify',
        'music',
        'listentothis',
        'ifyoulikeblank',
        'discovermusic'
    ]
    
    SEARCH_QUERIES = [
        'spotify discovery',
        'spotify recommendations',
        'spotify discover weekly',
        'spotify ai dj',
        'spotify daily mix',
        'spotify music discovery'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get('reddit_client_id')
        self.client_secret = config.get('reddit_client_secret')
        self.user_agent = config.get('reddit_user_agent', 'SpotifyReviewAnalysis/1.0')
        self.subreddits = config.get('subreddits', self.DEFAULT_SUBREDDITS)
        self.search_queries = config.get('search_queries', self.SEARCH_QUERIES)
        self.reddit = None
    
    def _get_source_type(self) -> DataSourceType:
        return DataSourceType.REDDIT
    
    def connect(self) -> bool:
        """Connect to Reddit API"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # Test connection
            self.reddit.user.me()
            logger.info("Successfully connected to Reddit API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Reddit: {str(e)}")
            return False
    
    def fetch_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch posts and comments from Reddit
        
        Args:
            limit: Maximum number of posts/comments to fetch
            since: Only fetch posts after this date
            until: Only fetch posts before this date
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        total_limit = limit or 500
        
        logger.info(f"Fetching Reddit posts from subreddits: {self.subreddits}")
        
        # Fetch from subreddits
        for subreddit_name in self.subreddits:
            if len(reviews) >= total_limit:
                break
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.new(limit=100)
                
                for post in posts:
                    if len(reviews) >= total_limit:
                        break
                    
                    try:
                        # Parse post
                        post_data = self._parse_post(post, subreddit_name)
                        
                        # Apply date filters
                        if since and post_data.timestamp and post_data.timestamp < since:
                            continue
                        if until and post_data.timestamp and post_data.timestamp > until:
                            continue
                        
                        reviews.append(post_data)
                        
                        # Also fetch top comments
                        if len(reviews) < total_limit:
                            comments = self._fetch_post_comments(post, subreddit_name, since, until)
                            reviews.extend(comments)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing post: {str(e)}")
                        continue
                
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {str(e)}")
                continue
        
        # Also search for specific queries
        if len(reviews) < total_limit:
            reviews.extend(self._search_reddit(total_limit - len(reviews), since, until))
        
        if limit:
            reviews = reviews[:limit]
        
        logger.info(f"Fetched {len(reviews)} Reddit posts/comments")
        return reviews
    
    def _parse_post(self, post, subreddit_name: str) -> ReviewData:
        """Parse a Reddit post into ReviewData"""
        review_id = f"post_{post.id}"
        content = post.selftext or post.title
        
        # Upvotes as a proxy for rating (normalized to 1-5)
        upvotes = post.score
        rating = min(5, max(1, (upvotes / 100) + 1)) if upvotes > 0 else None
        
        author = str(post.author) if post.author else None
        
        # Timestamp
        timestamp = datetime.fromtimestamp(post.created_utc)
        
        # URL
        url = f"https://reddit.com{post.permalink}"
        
        metadata = {
            'subreddit': subreddit_name,
            'upvotes': upvotes,
            'num_comments': post.num_comments,
            'post_type': 'post'
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
    
    def _fetch_post_comments(
        self,
        post,
        subreddit_name: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """Fetch comments from a post"""
        comments = []
        
        try:
            post.comments.replace_more(limit=0)
            
            for comment in post.comments.list()[:20]:  # Limit to top 20 comments
                try:
                    if not hasattr(comment, 'body'):
                        continue
                    
                    comment_data = self._parse_comment(comment, subreddit_name)
                    
                    # Apply date filters
                    if since and comment_data.timestamp and comment_data.timestamp < since:
                        continue
                    if until and comment_data.timestamp and comment_data.timestamp > until:
                        continue
                    
                    comments.append(comment_data)
                    
                except Exception as e:
                    logger.warning(f"Error parsing comment: {str(e)}")
                    continue
            
        except Exception as e:
            logger.warning(f"Error fetching comments: {str(e)}")
        
        return comments
    
    def _parse_comment(self, comment, subreddit_name: str) -> ReviewData:
        """Parse a Reddit comment into ReviewData"""
        review_id = f"comment_{comment.id}"
        content = comment.body
        
        # Upvotes as a proxy for rating
        upvotes = comment.score
        rating = min(5, max(1, (upvotes / 50) + 1)) if upvotes > 0 else None
        
        author = str(comment.author) if comment.author else None
        
        # Timestamp
        timestamp = datetime.fromtimestamp(comment.created_utc)
        
        # URL
        url = f"https://reddit.com{comment.permalink}"
        
        metadata = {
            'subreddit': subreddit_name,
            'upvotes': upvotes,
            'post_type': 'comment',
            'parent_id': comment.parent_id
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
    
    def _search_reddit(
        self,
        limit: int,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """Search Reddit for specific queries"""
        reviews = []
        
        for query in self.search_queries:
            if len(reviews) >= limit:
                break
            
            try:
                logger.info(f"Searching Reddit for: {query}")
                
                for submission in self.reddit.subreddit("all").search(query, limit=50):
                    if len(reviews) >= limit:
                        break
                    
                    try:
                        post_data = self._parse_post(submission, 'all')
                        
                        # Apply date filters
                        if since and post_data.timestamp and post_data.timestamp < since:
                            continue
                        if until and post_data.timestamp and post_data.timestamp > until:
                            continue
                        
                        reviews.append(post_data)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing search result: {str(e)}")
                        continue
                
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error searching for '{query}': {str(e)}")
                continue
        
        return reviews
    
    def disconnect(self) -> None:
        """No persistent connection to close"""
        pass
