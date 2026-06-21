"""
Metadata Enrichment Module
Enriches reviews with user profiling and content classification
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile extracted from reviews"""
    user_id: str
    activity_level: str
    source_credibility: float
    listening_patterns: Dict[str, Any]
    preferences: List[str]


@dataclass
class ContentClassification:
    """Classification of review content"""
    topic: str
    intent: str
    sentiment_proxy: str
    discovery_related: bool


class MetadataEnricher:
    """
    Enriches reviews with additional metadata
    Performs user profiling and content classification
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metadata enricher
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.user_profiles: Dict[str, UserProfile] = {}
        self.min_reviews_for_profile = config.get('min_reviews_for_profile', 3)
    
    def enrich_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single review with additional metadata
        
        Args:
            review: Review dictionary
            
        Returns:
            Enriched review dictionary
        """
        enriched = review.copy()
        
        # Add content classification
        classification = self._classify_content(review)
        enriched['content_classification'] = {
            'topic': classification.topic,
            'intent': classification.intent,
            'sentiment_proxy': classification.sentiment_proxy,
            'discovery_related': classification.discovery_related
        }
        
        # Add user profile (if enough data)
        author = review.get('author')
        if author:
            user_profile = self._get_or_create_user_profile(author, review)
            enriched['user_profile'] = {
                'activity_level': user_profile.activity_level,
                'source_credibility': user_profile.source_credibility,
                'listening_patterns': user_profile.listening_patterns,
                'preferences': user_profile.preferences
            }
        
        return enriched
    
    def _classify_content(self, review: Dict[str, Any]) -> ContentClassification:
        """
        Classify review content
        
        Args:
            review: Review dictionary
            
        Returns:
            ContentClassification object
        """
        content = review.get('content', '').lower()
        
        # Determine topic
        topic = self._determine_topic(content)
        
        # Determine intent
        intent = self._determine_intent(content)
        
        # Determine sentiment proxy (based on keywords)
        sentiment_proxy = self._determine_sentiment_proxy(content)
        
        # Check if discovery-related
        discovery_related = self._is_discovery_related(content)
        
        return ContentClassification(
            topic=topic,
            intent=intent,
            sentiment_proxy=sentiment_proxy,
            discovery_related=discovery_related
        )
    
    def _determine_topic(self, content: str) -> str:
        """Determine the main topic of the review"""
        topics = {
            'discovery': ['discover', 'recommend', 'new music', 'find songs'],
            'recommendations': ['recommend', 'algorithm', 'suggestion'],
            'ui_ux': ['interface', 'app', 'crash', 'bug', 'slow'],
            'pricing': ['price', 'cost', 'subscription', 'premium', 'free'],
            'content': ['song', 'artist', 'album', 'playlist'],
            'features': ['feature', 'update', 'new', 'add'],
            'performance': ['performance', 'load', 'buffer', 'stream']
        }
        
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in content)
            topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return 'general'
    
    def _determine_intent(self, content: str) -> str:
        """Determine the intent of the review"""
        intents = {
            'complaint': ['hate', 'terrible', 'worst', 'fix', 'broken', 'frustrating'],
            'suggestion': ['should', 'could', 'add', 'improve', 'better if', 'wish'],
            'praise': ['love', 'great', 'amazing', 'best', 'excellent', 'perfect'],
            'question': ['how', 'why', 'what', '?', 'help'],
            'feedback': ['feedback', 'opinion', 'think', 'feel']
        }
        
        intent_scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in content)
            intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general'
    
    def _determine_sentiment_proxy(self, content: str) -> str:
        """Determine sentiment based on keyword analysis"""
        positive_words = ['good', 'great', 'love', 'amazing', 'excellent', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful', 'poor', 'broken']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _is_discovery_related(self, content: str) -> bool:
        """Check if content is related to music discovery"""
        discovery_keywords = [
            'discover', 'new music', 'find songs', 'recommend', 'suggestion',
            'algorithm', 'explore', 'browse', 'search', 'genre', 'artist'
        ]
        
        return any(keyword in content for keyword in discovery_keywords)
    
    def _get_or_create_user_profile(
        self,
        author: str,
        review: Dict[str, Any]
    ) -> UserProfile:
        """
        Get or create user profile for author
        
        Args:
            author: Author identifier
            review: Review to add to profile
            
        Returns:
            UserProfile object
        """
        if author not in self.user_profiles:
            self.user_profiles[author] = UserProfile(
                user_id=author,
                activity_level='low',
                source_credibility=0.5,
                listening_patterns={},
                preferences=[]
            )
        
        profile = self.user_profiles[author]
        
        # Update profile based on review
        self._update_user_profile(profile, review)
        
        return profile
    
    def _update_user_profile(self, profile: UserProfile, review: Dict[str, Any]) -> None:
        """
        Update user profile based on new review
        
        Args:
            profile: UserProfile to update
            review: New review data
        """
        # Update activity level (simplified)
        profile.activity_level = 'medium'  # Could be more sophisticated
        
        # Update source credibility based on review quality
        rating = review.get('rating')
        if rating:
            profile.source_credibility = min(1.0, profile.source_credibility + 0.1)
        
        # Extract listening patterns from content
        content = review.get('content', '').lower()
        
        if 'repeat' in content or 'loop' in content:
            profile.listening_patterns['repetitive'] = profile.listening_patterns.get('repetitive', 0) + 1
        
        if 'discover' in content or 'new' in content:
            profile.listening_patterns['discovery'] = profile.listening_patterns.get('discovery', 0) + 1
        
        if 'playlist' in content:
            profile.listening_patterns['playlist_based'] = profile.listening_patterns.get('playlist_based', 0) + 1
    
    def enrich_batch(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich a batch of reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            List of enriched review dictionaries
        """
        enriched = []
        for review in reviews:
            enriched_review = self.enrich_review(review)
            enriched.append(enriched_review)
        
        logger.info(f"Enriched {len(enriched)} reviews with metadata")
        
        return enriched
    
    def get_user_profiles(self) -> Dict[str, UserProfile]:
        """
        Get all user profiles
        
        Returns:
            Dictionary of user profiles
        """
        return self.user_profiles
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get enrichment statistics
        
        Returns:
            Dictionary with statistics
        """
        total_profiles = len(self.user_profiles)
        
        activity_levels = defaultdict(int)
        for profile in self.user_profiles.values():
            activity_levels[profile.activity_level] += 1
        
        avg_credibility = sum(
            p.source_credibility for p in self.user_profiles.values()
        ) / total_profiles if total_profiles > 0 else 0
        
        return {
            'total_user_profiles': total_profiles,
            'activity_level_distribution': dict(activity_levels),
            'average_source_credibility': avg_credibility
        }
