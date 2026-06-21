"""
Pattern Recognition Module
Detects recurring complaints, recommendation quality patterns, and listening behavior patterns
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Detected pattern"""
    pattern_type: str
    pattern: str
    frequency: int
    confidence: float
    examples: List[str]


@dataclass
class PatternRecognitionResult:
    """Result of pattern recognition"""
    complaints: List[Pattern]
    recommendation_patterns: List[Pattern]
    listening_patterns: List[Pattern]
    summary: Dict[str, Any]


class PatternDetector:
    """
    Detects patterns in user feedback
    Identifies recurring complaints, recommendation quality issues, and listening behaviors
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pattern detector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_frequency = config.get('min_frequency', 5)
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        
        # Complaint patterns
        self.complaint_patterns = {
            'repetitive': [
                r'repetitive', r'same songs', r'always the same', r'looping',
                r'repeat', r'over and over', r'again and again'
            ],
            'limited_variety': [
                r'limited variety', r'not enough variety', r'lack of variety',
                r'same artists', r'same genre', r'boring'
            ],
            'algorithm_issues': [
                r'algorithm', r'recommendation.*bad', r'suggestions.*poor',
                r'not working', r'broken', r'wrong recommendations'
            ],
            'ui_problems': [
                r'crash', r'bug', r'slow', r'lag', r'freeze', r'not loading',
                r'interface.*bad', r'design.*poor'
            ],
            'discovery_difficult': [
                r'hard to find', r'difficult to discover', r'can.*t find',
                r'search.*bad', r'browse.*difficult'
            ]
        }
        
        # Recommendation quality patterns
        self.recommendation_patterns = {
            'predictable': [
                r'predictable', r'know.*what.*coming', r'expect.*same',
                r'not surprised', r'boring recommendations'
            ],
            'irrelevant': [
                r'irrelevant', r'not relevant', r'don.*t like',
                r'not my taste', r'wrong for me'
            ],
            'context_aware': [
                r'context', r'mood', r'situation', r'time.*day',
                r'activity', r'workout', r'study'
            ],
            'variety': [
                r'variety', r'diverse', r'different', r'new.*artists',
                r'explore', r'discover'
            ]
        }
        
        # Listening behavior patterns
        self.listening_patterns = {
            'habitual': [
                r'same playlist', r'favorite playlist', r'always listen',
                r'routine', r'habit', r'comfort zone'
            ],
            'mood_based': [
                r'mood', r'feeling', r'emotional', r'sad.*music',
                r'happy.*music', r'angry.*music'
            ],
            'activity_based': [
                r'workout', r'exercise', r'running', r'study', r'work',
                r'focus', r'sleep', r'commute'
            ],
            'discovery_focused': [
                r'discover', r'new music', r'explore', r'find.*new',
                r'browse', r'search'
            ],
            'nostalgic': [
                r'old songs', r'classics', r'nostalgia', r'memories',
                r'childhood', r'throwback'
            ]
        }
    
    def detect_patterns(self, reviews: List[Dict[str, Any]]) -> PatternRecognitionResult:
        """
        Detect all patterns in reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            PatternRecognitionResult with all detected patterns
        """
        logger.info(f"Detecting patterns in {len(reviews)} reviews")
        
        # Extract texts
        texts = [review.get('content', '') for review in reviews]
        
        # Detect complaint patterns
        complaints = self._detect_complaint_patterns(texts, reviews)
        
        # Detect recommendation patterns
        recommendation_patterns = self._detect_recommendation_patterns(texts, reviews)
        
        # Detect listening patterns
        listening_patterns = self._detect_listening_patterns(texts, reviews)
        
        # Generate summary
        summary = {
            'total_reviews': len(reviews),
            'complaints_found': len(complaints),
            'recommendation_patterns_found': len(recommendation_patterns),
            'listening_patterns_found': len(listening_patterns)
        }
        
        logger.info(
            f"Pattern detection complete: {len(complaints)} complaints, "
            f"{len(recommendation_patterns)} recommendation patterns, "
            f"{len(listening_patterns)} listening patterns"
        )
        
        return PatternRecognitionResult(
            complaints=complaints,
            recommendation_patterns=recommendation_patterns,
            listening_patterns=listening_patterns,
            summary=summary
        )
    
    def _detect_complaint_patterns(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Detect complaint patterns"""
        patterns = []
        
        for complaint_type, regex_list in self.complaint_patterns.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                for pattern in regex_list:
                    if re.search(pattern, text_lower):
                        matches.append((i, text))
                        break
            
            if len(matches) >= self.min_frequency:
                confidence = min(len(matches) / len(texts), 1.0)
                if confidence >= self.confidence_threshold:
                    examples = [text for _, text in matches[:3]]
                    pattern = Pattern(
                        pattern_type='complaint',
                        pattern=complaint_type,
                        frequency=len(matches),
                        confidence=confidence,
                        examples=examples
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_recommendation_patterns(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Detect recommendation quality patterns"""
        patterns = []
        
        for pattern_type, regex_list in self.recommendation_patterns.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                for pattern in regex_list:
                    if re.search(pattern, text_lower):
                        matches.append((i, text))
                        break
            
            if len(matches) >= self.min_frequency:
                confidence = min(len(matches) / len(texts), 1.0)
                if confidence >= self.confidence_threshold:
                    examples = [text for _, text in matches[:3]]
                    pattern = Pattern(
                        pattern_type='recommendation',
                        pattern=pattern_type,
                        frequency=len(matches),
                        confidence=confidence,
                        examples=examples
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_listening_patterns(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[Pattern]:
        """Detect listening behavior patterns"""
        patterns = []
        
        for pattern_type, regex_list in self.listening_patterns.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                for pattern in regex_list:
                    if re.search(pattern, text_lower):
                        matches.append((i, text))
                        break
            
            if len(matches) >= self.min_frequency:
                confidence = min(len(matches) / len(texts), 1.0)
                if confidence >= self.confidence_threshold:
                    examples = [text for _, text in matches[:3]]
                    pattern = Pattern(
                        pattern_type='listening',
                        pattern=pattern_type,
                        frequency=len(matches),
                        confidence=confidence,
                        examples=examples
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def extract_ngrams(self, texts: List[str], n: int = 3) -> List[Tuple[str, int]]:
        """
        Extract frequent n-grams from texts
        
        Args:
            texts: List of texts
            n: N-gram size
            
        Returns:
            List of (n-gram, frequency) tuples
        """
        ngram_counts = Counter()
        
        for text in texts:
            words = text.lower().split()
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngram_counts[ngram] += 1
        
        # Filter by minimum frequency
        filtered_ngrams = [
            (ngram, count) for ngram, count in ngram_counts.items()
            if count >= self.min_frequency
        ]
        
        # Sort by frequency
        filtered_ngrams.sort(key=lambda x: x[1], reverse=True)
        
        return filtered_ngrams[:20]  # Return top 20
    
    def get_statistics(self, result: PatternRecognitionResult) -> Dict[str, Any]:
        """
        Get statistics from pattern recognition result
        
        Args:
            result: PatternRecognitionResult object
            
        Returns:
            Dictionary with statistics
        """
        complaint_types = defaultdict(int)
        for pattern in result.complaints:
            complaint_types[pattern.pattern] += 1
        
        recommendation_types = defaultdict(int)
        for pattern in result.recommendation_patterns:
            recommendation_types[pattern.pattern] += 1
        
        listening_types = defaultdict(int)
        for pattern in result.listening_patterns:
            listening_types[pattern.pattern] += 1
        
        return {
            'summary': result.summary,
            'complaint_types': dict(complaint_types),
            'recommendation_types': dict(recommendation_types),
            'listening_types': dict(listening_types),
            'total_patterns': (
                len(result.complaints) +
                len(result.recommendation_patterns) +
                len(result.listening_patterns)
            )
        }
