"""
User Segmentation Module
Performs clustering-based and rule-based user segmentation
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


@dataclass
class UserSegment:
    """User segment definition"""
    segment_id: str
    segment_name: str
    description: str
    key_behaviors: List[str]
    discovery_challenges: List[str]
    motivations: List[str]
    size: int
    representative_quotes: List[str]


@dataclass
class SegmentationResult:
    """Result of user segmentation"""
    segments: List[UserSegment]
    total_users: int
    method_used: str


class UserSegmenter:
    """
    User segmentation using clustering and rule-based approaches
    Identifies distinct user segments based on behavior and preferences
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize user segmenter
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.method = config.get('method', 'hybrid')  # clustering, rule_based, hybrid
        self.n_clusters = config.get('n_clusters', 6)
        
        # Segment definitions
        self.segment_profiles = {
            'discovery_focused': {
                'description': 'Users who actively seek new music and artists',
                'key_behaviors': ['frequent discovery', 'explore new genres', 'browse recommendations'],
                'discovery_challenges': ['limited variety', 'repetitive recommendations'],
                'motivations': ['find fresh music', 'discover emerging artists']
            },
            'habitual_listener': {
                'description': 'Users who listen to familiar content and established playlists',
                'key_behaviors': ['repeat listening', 'playlist dependence', 'artist loyalty'],
                'discovery_challenges': ['resistance to change', 'comfort zone'],
                'motivations': ['comfort', 'familiarity', 'consistency']
            },
            'mood_based': {
                'description': 'Users who select music based on current mood or emotional state',
                'key_behaviors': ['mood matching', 'emotional listening', 'situation-based'],
                'discovery_challenges': ['context mismatch', 'limited mood detection'],
                'motivations': ['emotional regulation', 'mood enhancement']
            },
            'activity_based': {
                'description': 'Users who listen to music for specific activities (workout, study, etc.)',
                'key_behaviors': ['activity matching', 'routine listening', 'purpose-driven'],
                'discovery_challenges': ['activity-specific needs', 'context limitations'],
                'motivations': ['performance enhancement', 'focus', 'relaxation']
            },
            'genre_explorer': {
                'description': 'Users who actively explore and discover within specific genres',
                'key_behaviors': ['genre deep-dives', 'artist exploration', 'niche interests'],
                'discovery_challenges': ['limited cross-genre discovery', 'genre silos'],
                'motivations': ['genre expertise', 'curated experiences']
            },
            'casual_listener': {
                'description': 'Users with low engagement and passive consumption habits',
                'key_behaviors': ['background listening', 'low interaction', 'passive consumption'],
                'discovery_challenges': ['low motivation', 'lack of engagement'],
                'motivations': ['background noise', 'convenience']
            }
        }
    
    def segment_users(
        self,
        reviews: List[Dict[str, Any]]
    ) -> SegmentationResult:
        """
        Segment users based on their reviews and behavior
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            SegmentationResult with user segments
        """
        logger.info(f"Segmenting users from {len(reviews)} reviews using {self.method}")
        
        if self.method == 'clustering':
            result = self._clustering_segmentation(reviews)
        elif self.method == 'rule_based':
            result = self._rule_based_segmentation(reviews)
        else:  # hybrid
            result = self._hybrid_segmentation(reviews)
        
        logger.info(f"Segmentation complete: {len(result.segments)} segments identified")
        
        return result
    
    def _clustering_segmentation(self, reviews: List[Dict[str, Any]]) -> SegmentationResult:
        """Perform clustering-based segmentation"""
        # Group reviews by user
        user_reviews = defaultdict(list)
        for review in reviews:
            author = review.get('author')
            if author:
                user_reviews[author].append(review)
        
        # Extract features for each user
        user_features = []
        user_ids = []
        
        for user_id, user_review_list in user_reviews.items():
            features = self._extract_user_features(user_review_list)
            user_features.append(features)
            user_ids.append(user_id)
        
        if not user_features:
            return SegmentationResult(
                segments=[],
                total_users=0,
                method_used='clustering'
            )
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(user_features)
        
        # Cluster users
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Create segments from clusters
        segments = self._create_segments_from_clusters(
            user_ids,
            cluster_labels,
            user_reviews
        )
        
        return SegmentationResult(
            segments=segments,
            total_users=len(user_ids),
            method_used='clustering'
        )
    
    def _rule_based_segmentation(self, reviews: List[Dict[str, Any]]) -> SegmentationResult:
        """Perform rule-based segmentation"""
        # Group reviews by user
        user_reviews = defaultdict(list)
        for review in reviews:
            author = review.get('author')
            if author:
                user_reviews[author].append(review)
        
        # Assign segments based on rules
        user_segments = defaultdict(list)
        
        for user_id, user_review_list in user_reviews.items():
            segment = self._assign_segment_by_rules(user_review_list)
            user_segments[segment].append(user_id)
        
        # Create segment objects
        segments = []
        for segment_name, user_ids in user_segments.items():
            if segment_name in self.segment_profiles:
                profile = self.segment_profiles[segment_name]
                
                # Get representative quotes
                quotes = self._get_representative_quotes(user_reviews, user_ids[:5])
                
                segment = UserSegment(
                    segment_id=segment_name,
                    segment_name=segment_name,
                    description=profile['description'],
                    key_behaviors=profile['key_behaviors'],
                    discovery_challenges=profile['discovery_challenges'],
                    motivations=profile['motivations'],
                    size=len(user_ids),
                    representative_quotes=quotes
                )
                segments.append(segment)
        
        return SegmentationResult(
            segments=segments,
            total_users=len(user_reviews),
            method_used='rule_based'
        )
    
    def _hybrid_segmentation(self, reviews: List[Dict[str, Any]]) -> SegmentationResult:
        """Perform hybrid segmentation (clustering + rules)"""
        # First perform clustering
        clustering_result = self._clustering_segmentation(reviews)
        
        # Then refine with rules
        refined_segments = []
        
        for segment in clustering_result.segments:
            # Refine segment description based on rules
            if segment.segment_name in self.segment_profiles:
                profile = self.segment_profiles[segment.segment_name]
                segment.key_behaviors = profile['key_behaviors']
                segment.discovery_challenges = profile['discovery_challenges']
                segment.motivations = profile['motivations']
            
            refined_segments.append(segment)
        
        return SegmentationResult(
            segments=refined_segments,
            total_users=clustering_result.total_users,
            method_used='hybrid'
        )
    
    def _extract_user_features(self, user_reviews: List[Dict[str, Any]]) -> List[float]:
        """Extract numerical features from user reviews"""
        features = []
        
        # Number of reviews
        features.append(len(user_reviews))
        
        # Average rating
        ratings = [r.get('rating') for r in user_reviews if r.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        features.append(avg_rating)
        
        # Content length average
        content_lengths = [len(r.get('content', '')) for r in user_reviews]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        features.append(avg_length)
        
        # Discovery-related keywords
        discovery_keywords = ['discover', 'new', 'explore', 'find']
        discovery_count = 0
        for review in user_reviews:
            content = review.get('content', '').lower()
            discovery_count += sum(1 for kw in discovery_keywords if kw in content)
        features.append(discovery_count / len(user_reviews) if user_reviews else 0)
        
        # Habit-related keywords
        habit_keywords = ['always', 'usually', 'routine', 'same', 'repeat']
        habit_count = 0
        for review in user_reviews:
            content = review.get('content', '').lower()
            habit_count += sum(1 for kw in habit_keywords if kw in content)
        features.append(habit_count / len(user_reviews) if user_reviews else 0)
        
        return features
    
    def _assign_segment_by_rules(self, user_reviews: List[Dict[str, Any]]) -> str:
        """Assign user to segment based on rule-based logic"""
        # Combine all user content
        all_content = ' '.join([r.get('content', '') for r in user_reviews]).lower()
        
        # Score each segment
        segment_scores = {}
        
        for segment_name, profile in self.segment_profiles.items():
            score = 0
            for behavior in profile['key_behaviors']:
                if behavior in all_content:
                    score += 1
            segment_scores[segment_name] = score
        
        # Assign to highest scoring segment
        if segment_scores:
            return max(segment_scores, key=segment_scores.get)
        
        return 'casual_listener'
    
    def _create_segments_from_clusters(
        self,
        user_ids: List[str],
        cluster_labels: np.ndarray,
        user_reviews: Dict[str, List[Dict[str, Any]]]
    ) -> List[UserSegment]:
        """Create segment objects from clustering results"""
        segments = []
        segment_names = [
            'discovery_focused',
            'habitual_listener',
            'mood_based',
            'activity_based',
            'genre_explorer',
            'casual_listener'
        ]
        
        for cluster_id in range(len(set(cluster_labels))):
            # Get users in this cluster
            cluster_user_ids = [
                user_ids[i] for i, label in enumerate(cluster_labels)
                if label == cluster_id
            ]
            
            # Map cluster to segment name
            segment_name = segment_names[cluster_id % len(segment_names)]
            profile = self.segment_profiles.get(segment_name, {})
            
            # Get representative quotes
            quotes = self._get_representative_quotes(user_reviews, cluster_user_ids[:5])
            
            segment = UserSegment(
                segment_id=f"segment_{cluster_id}",
                segment_name=segment_name,
                description=profile.get('description', ''),
                key_behaviors=profile.get('key_behaviors', []),
                discovery_challenges=profile.get('discovery_challenges', []),
                motivations=profile.get('motivations', []),
                size=len(cluster_user_ids),
                representative_quotes=quotes
            )
            segments.append(segment)
        
        return segments
    
    def _get_representative_quotes(
        self,
        user_reviews: Dict[str, List[Dict[str, Any]]],
        user_ids: List[str]
    ) -> List[str]:
        """Get representative quotes from users"""
        quotes = []
        for user_id in user_ids:
            if user_id in user_reviews:
                reviews = user_reviews[user_id]
                if reviews:
                    # Get the longest review as representative
                    longest_review = max(reviews, key=lambda r: len(r.get('content', '')))
                    quotes.append(longest_review.get('content', '')[:200])
        
        return quotes
    
    def get_segment_statistics(self, result: SegmentationResult) -> Dict[str, Any]:
        """
        Get statistics from segmentation result
        
        Args:
            result: SegmentationResult object
            
        Returns:
            Dictionary with statistics
        """
        segment_sizes = {s.segment_name: s.size for s in result.segments}
        total_users = result.total_users
        
        return {
            'total_segments': len(result.segments),
            'total_users': total_users,
            'segment_sizes': segment_sizes,
            'method_used': result.method_used,
            'average_segment_size': total_users / len(result.segments) if result.segments else 0
        }
