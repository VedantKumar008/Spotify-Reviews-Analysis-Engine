"""
Quality Filtering Module
Filters reviews based on quality metrics and relevance
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class QualityFilterResult:
    """Result of quality filtering"""
    passed: bool
    score: float
    reasons: List[str]


class QualityFilter:
    """
    Filters reviews based on quality metrics
    Ensures only high-quality, relevant reviews are processed
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize quality filter
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_length = config.get('min_length', 20)
        self.max_length = config.get('max_length', 10000)
        self.min_words = config.get('min_words', 3)
        self.language_threshold = config.get('language_threshold', 0.7)
        self.relevance_threshold = config.get('relevance_threshold', 0.5)
        
        # Spotify-related keywords for relevance checking
        self.spotify_keywords = [
            'spotify', 'music', 'song', 'playlist', 'discover', 'recommend',
            'algorithm', 'dj', 'mix', 'radio', 'artist', 'genre', 'album',
            'listening', 'stream', 'play', 'shuffle', 'queue', 'library'
        ]
    
    def filter_review(self, review: Dict[str, Any]) -> QualityFilterResult:
        """
        Filter a single review based on quality metrics
        
        Args:
            review: Review dictionary
            
        Returns:
            QualityFilterResult with pass/fail and reasons
        """
        reasons = []
        score = 1.0
        content = review.get('content', '')
        
        # Check length
        length_score = self._check_length(content)
        if length_score < 0.5:
            reasons.append("Content length outside acceptable range")
        score *= length_score
        
        # Check word count
        word_score = self._check_word_count(content)
        if word_score < 0.5:
            reasons.append("Insufficient word count")
        score *= word_score
        
        # Check for meaningful content
        meaningful_score = self._check_meaningful(content)
        if meaningful_score < 0.5:
            reasons.append("Content lacks meaningful information")
        score *= meaningful_score
        
        # Check relevance to Spotify
        relevance_score = self._check_relevance(content)
        if relevance_score < self.relevance_threshold:
            reasons.append("Content not relevant to Spotify")
        score *= relevance_score
        
        # Check for excessive special characters
        special_char_score = self._check_special_characters(content)
        if special_char_score < 0.5:
            reasons.append("Excessive special characters")
        score *= special_char_score
        
        # Check for gibberish
        gibberish_score = self._check_gibberish(content)
        if gibberish_score < 0.5:
            reasons.append("Content appears to be gibberish")
        score *= gibberish_score
        
        passed = score >= 0.5 and len(reasons) == 0
        
        return QualityFilterResult(
            passed=passed,
            score=score,
            reasons=reasons
        )
    
    def _check_length(self, content: str) -> float:
        """Check if content length is within acceptable range"""
        length = len(content)
        
        if length < self.min_length:
            return 0.0
        elif length < self.min_length * 2:
            return 0.5
        elif length > self.max_length:
            return 0.3
        else:
            return 1.0
    
    def _check_word_count(self, content: str) -> float:
        """Check if content has sufficient words"""
        words = content.split()
        word_count = len(words)
        
        if word_count < self.min_words:
            return 0.0
        elif word_count < self.min_words * 2:
            return 0.5
        else:
            return 1.0
    
    def _check_meaningful(self, content: str) -> float:
        """Check if content has meaningful information"""
        # Check for common non-meaningful patterns
        non_meaningful_patterns = [
            r'^[.\s]*$',  # Only dots and spaces
            r'^[!@#$%^&*()]*$',  # Only special characters
            r'^(.)\1+$',  # Repeated single character
            r'^\d+$',  # Only numbers
        ]
        
        for pattern in non_meaningful_patterns:
            if re.match(pattern, content):
                return 0.0
        
        # Check for variety of characters
        unique_chars = len(set(content))
        if unique_chars < 5:
            return 0.3
        
        # Check for sentence structure (basic)
        if '.' in content or '!' in content or '?' in content:
            return 1.0
        
        return 0.8
    
    def _check_relevance(self, content: str) -> float:
        """Check if content is relevant to Spotify"""
        content_lower = content.lower()
        
        # Count Spotify-related keywords
        keyword_count = sum(
            1 for keyword in self.spotify_keywords
            if keyword in content_lower
        )
        
        # Calculate relevance score
        if keyword_count >= 3:
            return 1.0
        elif keyword_count >= 2:
            return 0.8
        elif keyword_count >= 1:
            return 0.6
        else:
            return 0.3
    
    def _check_special_characters(self, content: str) -> float:
        """Check for excessive special characters"""
        # Count special characters (non-alphanumeric, non-space)
        special_count = sum(
            1 for char in content
            if not char.isalnum() and not char.isspace()
        )
        
        total_chars = len(content)
        if total_chars == 0:
            return 0.0
        
        special_ratio = special_count / total_chars
        
        if special_ratio > 0.5:
            return 0.0
        elif special_ratio > 0.3:
            return 0.5
        else:
            return 1.0
    
    def _check_gibberish(self, content: str) -> float:
        """Check if content appears to be gibberish"""
        words = content.split()
        
        if len(words) == 0:
            return 0.0
        
        # Check for common gibberish patterns
        gibberish_patterns = [
            r'(.)\1{3,}',  # Repeated characters (4+ times)
            r'^[a-z]{20,}$',  # Very long single word
        ]
        
        for pattern in gibberish_patterns:
            if re.search(pattern, content.lower()):
                return 0.3
        
        # Check vowel ratio (gibberish often has low vowel ratio)
        vowels = 'aeiou'
        vowel_count = sum(1 for char in content.lower() if char in vowels)
        vowel_ratio = vowel_count / len(content) if len(content) > 0 else 0
        
        if vowel_ratio < 0.1:
            return 0.5
        
        return 1.0
    
    def filter_batch(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter a batch of reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Tuple of (passed reviews, failed reviews)
        """
        passed = []
        failed = []
        
        for review in reviews:
            result = self.filter_review(review)
            if result.passed:
                passed.append(review)
            else:
                failed.append({
                    **review,
                    'filter_result': {
                        'passed': result.passed,
                        'score': result.score,
                        'reasons': result.reasons
                    }
                })
        
        logger.info(
            f"Quality filtering: {len(passed)} passed, {len(failed)} failed"
        )
        
        return passed, failed
    
    def get_statistics(
        self,
        results: List[QualityFilterResult]
    ) -> Dict[str, Any]:
        """
        Get statistics from quality filtering results
        
        Args:
            results: List of QualityFilterResult objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        
        # Common failure reasons
        failure_reasons = {}
        for result in results:
            if not result.passed:
                for reason in result.reasons:
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        # Average score
        avg_score = sum(r.score for r in results) / total if total > 0 else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed / total if total > 0 else 0,
            'average_score': avg_score,
            'failure_reasons': failure_reasons
        }
