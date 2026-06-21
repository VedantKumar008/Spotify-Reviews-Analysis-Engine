"""
Spotify Community Forum Scraper
Fetches discussions from Spotify Community Forums
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin

from .base_connector import BaseConnector, ReviewData, DataSourceType

logger = logging.getLogger(__name__)


class ForumScraper(BaseConnector):
    """
    Connector for scraping Spotify Community Forums
    Uses web scraping with BeautifulSoup
    """
    
    BASE_URL = "https://community.spotify.com"
    FORUM_CATEGORIES = [
        't5/Help/ct-p/help',
        't5/Ideas/ct-p/ideas',
        't5/Account-Payments/ct-p/account-payments',
        't5/Spotify-on-Desktop/ct-p/desktop',
        't5/Spotify-on-Mobile/ct-p/mobile',
        't5/Spotify-on-Other-Platforms/ct-p/other-platforms'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', self.BASE_URL)
        self.categories = config.get('categories', self.FORUM_CATEGORIES)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_source_type(self) -> DataSourceType:
        return DataSourceType.FORUM
    
    def connect(self) -> bool:
        """Test connection to Spotify Community Forums"""
        try:
            response = self.session.get(self.base_url, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Spotify Community Forums: {str(e)}")
            return False
    
    def fetch_reviews(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """
        Fetch discussions from Spotify Community Forums
        
        Args:
            limit: Maximum number of discussions to fetch
            since: Only fetch discussions after this date
            until: Only fetch discussions before this date
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        total_limit = limit or 300
        
        logger.info(f"Fetching forum discussions from {len(self.categories)} categories")
        
        for category in self.categories:
            if len(reviews) >= total_limit:
                break
            
            try:
                category_reviews = self._fetch_category(category, total_limit - len(reviews), since, until)
                reviews.extend(category_reviews)
                
                self._apply_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching category {category}: {str(e)}")
                continue
        
        if limit:
            reviews = reviews[:limit]
        
        logger.info(f"Fetched {len(reviews)} forum discussions")
        return reviews
    
    def _fetch_category(
        self,
        category: str,
        limit: int,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[ReviewData]:
        """Fetch discussions from a specific category"""
        reviews = []
        url = urljoin(self.base_url, category)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find discussion threads
            thread_links = soup.find_all('a', class_='lia-link-navigation')
            
            for link in thread_links[:limit]:
                if len(reviews) >= limit:
                    break
                
                try:
                    thread_url = urljoin(self.base_url, link.get('href'))
                    thread_data = self._fetch_thread(thread_url, category, since, until)
                    
                    if thread_data:
                        reviews.append(thread_data)
                        
                except Exception as e:
                    logger.warning(f"Error fetching thread: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error fetching category {category}: {str(e)}")
        
        return reviews
    
    def _fetch_thread(
        self,
        url: str,
        category: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Optional[ReviewData]:
        """Fetch a single forum thread"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract post content
            post_body = soup.find('div', class_='lia-message-body-content')
            content = post_body.get_text(strip=True) if post_body else ""
            
            # Extract title
            title_elem = soup.find('h1', class_='lia-message-subject')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Combine title and content
            full_content = f"{title}\n\n{content}" if title else content
            
            # Extract author
            author_elem = soup.find('span', class_='lia-message-author-username')
            author = author_elem.get_text(strip=True) if author_elem else None
            
            # Extract timestamp
            timestamp = None
            time_elem = soup.find('span', class_='local-date')
            if time_elem:
                try:
                    timestamp = self._parse_forum_date(time_elem.get_text(strip=True))
                except:
                    pass
            
            # Extract kudos/likes as rating proxy
            rating = None
            kudos_elem = soup.find('span', class_='lia-kudos-count')
            if kudos_elem:
                try:
                    kudos = int(kudos_elem.get_text(strip=True))
                    rating = min(5, max(1, (kudos / 5) + 1)) if kudos > 0 else None
                except:
                    pass
            
            # Extract reply count
            reply_count = 0
            reply_elem = soup.find('span', class_='lia-message-count')
            if reply_elem:
                try:
                    reply_count = int(reply_elem.get_text(strip=True))
                except:
                    pass
            
            # Apply date filters
            if since and timestamp and timestamp < since:
                return None
            if until and timestamp and timestamp > until:
                return None
            
            review_id = url.split('/')[-1] or f"forum_{hash(url)}"
            
            metadata = {
                'category': category,
                'reply_count': reply_count,
                'post_type': 'forum_thread'
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
            
        except Exception as e:
            logger.warning(f"Error parsing thread {url}: {str(e)}")
            return None
    
    def _parse_forum_date(self, date_str: str) -> datetime:
        """Parse forum date string to datetime"""
        # This is a simplified parser - would need to be enhanced for production
        try:
            # Try common formats
            for fmt in ['%B %d, %Y', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
        except:
            pass
        
        # Fallback to current time if parsing fails
        return datetime.now()
    
    def disconnect(self) -> None:
        """Close session"""
        self.session.close()
