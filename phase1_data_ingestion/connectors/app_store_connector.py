"""
App Store Reviews Connector
Fetches reviews from Apple App Store for Spotify app
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import logging

from .base_connector import BaseConnector, ReviewData, DataSourceType

logger = logging.getLogger(__name__)


class AppStoreConnector(BaseConnector):
    """
    Connector for fetching reviews from Apple App Store
    Uses App Store RSS feed and web scraping
    """
    
    SPOTIFY_APP_ID = "324684580"  # Spotify app ID on App Store
    BASE_URL = "https://apps.apple.com/us/app/spotify/id{app_id}"
    RSS_URL = "https://rss.applemarketingtools.com/api/v2/us/apps/{app_id}/reviews"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id', self.SPOTIFY_APP_ID)
        self.country = config.get('country', 'us')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_source_type(self) -> DataSourceType:
        return DataSourceType.APP_STORE
    
    def connect(self) -> bool:
        """Test connection to App Store"""
        try:
            response = self.session.get(
                self.BASE_URL.format(app_id=self.app_id),
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to App Store: {str(e)}")
            return False
    
    def fetch_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch reviews from App Store RSS feed
        
        Args:
            limit: Maximum number of reviews to fetch
            since: Only fetch reviews after this date
            until: Only fetch reviews before this date
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        page = 1
        max_pages = 10  # Safety limit
        
        while len(reviews) < (limit or float('inf')) and page <= max_pages:
            logger.info(f"Fetching App Store reviews page {page}")
            
            try:
                page_reviews = self._fetch_page(page, since, until)
                reviews.extend(page_reviews)
                
                if not page_reviews:
                    logger.info(f"No more reviews found on page {page}")
                    break
                
                page += 1
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break
        
        if limit:
            reviews = reviews[:limit]
        
        return reviews
    
    def _fetch_page(
        self,
        page: int,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """Fetch reviews from Apple Marketing Tools API"""
        url = self.RSS_URL.format(app_id=self.app_id)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            reviews = []
            
            # Parse JSON response from Apple Marketing Tools API
            if 'feed' in data and 'entry' in data['feed']:
                entries = data['feed']['entry']
                
                for entry in entries:
                    try:
                        review = self._parse_json_entry(entry)
                        
                        # Apply date filters
                        if since and review.timestamp and review.timestamp < since:
                            continue
                        if until and review.timestamp and review.timestamp > until:
                            continue
                        
                        reviews.append(review)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing entry: {str(e)}")
                        continue
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error fetching reviews: {str(e)}")
            return []
    
    def _parse_json_entry(self, entry: Dict[str, Any]) -> ReviewData:
        """Parse a single JSON entry from Apple Marketing Tools API"""
        review_id = entry.get('id', {}).get('label')
        
        # Get content
        content = ""
        if 'content' in entry:
            if isinstance(entry['content'], dict) and 'label' in entry['content']:
                content = entry['content']['label']
            elif isinstance(entry['content'], str):
                content = entry['content']
        
        # Get title
        title = ""
        if 'title' in entry:
            if isinstance(entry['title'], dict) and 'label' in entry['title']:
                title = entry['title']['label']
            elif isinstance(entry['title'], str):
                title = entry['title']
        
        # Combine title and content
        full_content = f"{title}. {content}" if title else content
        
        # Rating
        rating = None
        if 'im:rating' in entry:
            if isinstance(entry['im:rating'], dict) and 'label' in entry['im:rating']:
                try:
                    rating = float(entry['im:rating']['label'])
                except:
                    pass
            elif isinstance(entry['im:rating'], (int, float)):
                rating = float(entry['im:rating'])
        
        # Author
        author = None
        if 'author' in entry:
            if isinstance(entry['author'], dict):
                if 'name' in entry['author']:
                    if isinstance(entry['author']['name'], dict) and 'label' in entry['author']['name']:
                        author = entry['author']['name']['label']
                    elif isinstance(entry['author']['name'], str):
                        author = entry['author']['name']
        
        # Timestamp
        timestamp = None
        if 'updated' in entry:
            if isinstance(entry['updated'], dict) and 'label' in entry['updated']:
                try:
                    timestamp = datetime.fromisoformat(entry['updated']['label'].replace('Z', '+00:00'))
                except:
                    pass
            elif isinstance(entry['updated'], str):
                try:
                    timestamp = datetime.fromisoformat(entry['updated'].replace('Z', '+00:00'))
                except:
                    pass
        
        # Version
        version = None
        if 'im:version' in entry:
            if isinstance(entry['im:version'], dict) and 'label' in entry['im:version']:
                version = entry['im:version']['label']
            elif isinstance(entry['im:version'], str):
                version = entry['im:version']
        
        # URL
        url = None
        if 'link' in entry:
            if isinstance(entry['link'], list) and len(entry['link']) > 0:
                if isinstance(entry['link'][0], dict) and 'attributes' in entry['link'][0]:
                    url = entry['link'][0]['attributes'].get('href')
            elif isinstance(entry['link'], dict) and 'attributes' in entry['link']:
                url = entry['link']['attributes'].get('href')
        
        metadata = {
            'app_version': version,
            'country': self.country
        }
        
        return ReviewData(
            source=self.source_type,
            review_id=review_id,
            content=full_content,
            rating=rating,
            author=author,
            timestamp=timestamp,
            url=url,
            metadata=metadata
        )
    
    def _parse_entry(self, entry) -> ReviewData:
        """Parse a single RSS entry into ReviewData (legacy method)"""
        review_id = entry.find('id').text if entry.find('id') else None
        content = entry.find('content').text if entry.find('content') else ""
        title = entry.find('title').text if entry.find('title') else ""
        
        # Combine title and content
        full_content = f"{title}. {content}" if title else content
        
        # Rating
        rating = None
        rating_elem = entry.find('im:rating')
        if rating_elem:
            rating = float(rating_elem.text)
        
        # Author
        author = None
        author_elem = entry.find('author')
        if author_elem:
            name_elem = author_elem.find('name')
            if name_elem:
                author = name_elem.text
        
        # Timestamp
        timestamp = None
        updated_elem = entry.find('updated')
        if updated_elem:
            try:
                timestamp = datetime.fromisoformat(updated_elem.text.replace('Z', '+00:00'))
            except:
                pass
        
        # Version
        version = None
        version_elem = entry.find('im:version')
        if version_elem:
            version = version_elem.text
        
        # URL
        url = None
        url_elem = entry.find('link')
        if url_elem:
            url = url_elem.get('href')
        
        metadata = {
            'app_version': version,
            'country': self.country
        }
        
        return ReviewData(
            source=self.source_type,
            review_id=review_id,
            content=full_content,
            rating=rating,
            author=author,
            timestamp=timestamp,
            url=url,
            metadata=metadata
        )
    
    def disconnect(self) -> None:
        """Close session"""
        self.session.close()
