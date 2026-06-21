"""
User Behavior Analysis Module
Analyzes listening behavior patterns, goal extraction, and habit detection
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)


@dataclass
class ListeningGoal:
    """Listening goal extracted from text"""
    goal_type: str
    description: str
    confidence: float


@dataclass
class BehaviorPattern:
    """Detected behavior pattern"""
    pattern_type: str
    description: str
    frequency: int
    examples: List[str]


@dataclass
class BehaviorAnalysisResult:
    """Result of behavior analysis"""
    goals: List[ListeningGoal]
    patterns: List[BehaviorPattern]
    habit_indicators: Dict[str, int]
    summary: Dict[str, Any]


class BehaviorAnalyzer:
    """
    Analyzes user listening behavior from reviews
    Extracts goals, patterns, and habit indicators
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize behavior analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_frequency = config.get('min_frequency', 3)
        
        # Listening goal patterns
        self.goal_patterns = {
            'mood_matching': [
                r'mood', r'feeling', r'emotional', r'sad.*music',
                r'happy.*music', r'calm.*music', r'energetic.*music'
            ],
            'activity_matching': [
                r'workout', r'exercise', r'running', r'gym',
                r'study', r'work', r'focus', r'concentrate',
                r'sleep', r'relax', r'commute', r'drive'
            ],
            'discovery': [
                r'discover', r'new music', r'find.*new', r'explore',
                r'browse', r'search', r'new artists', r'new songs'
            ],
            'familiarity': [
                r'familiar', r'comfort', r'safe', r'known',
                r'favorite', r'usual', r'regular'
            ],
            'variety': [
                r'variety', r'different', r'diverse', r'mix',
                r'change', r'something new', r'not same'
            ]
        }
        
        # Habit indicator patterns
        self.habit_patterns = {
            'repetitive_listening': [
                r'always listen', r'every day', r'all the time',
                r'constantly', r'never change', r'same routine'
            ],
            'playlist_dependence': [
                r'playlist', r'my playlist', r'favorite playlist',
                r'saved playlist', r'custom playlist'
            ],
            'artist_loyalty': [
                r'favorite artist', r'always.*artist', r'only.*artist',
                r'artist.*fan', r'follow.*artist'
            ],
            'genre_preference': [
                r'love.*genre', r'only.*genre', r'prefer.*genre',
                r'favorite genre', r'genre.*fan'
            ],
            'time_based': [
                r'morning', r'night', r'evening', r'weekend',
                r'work.*day', r'commute', r'bedtime'
            ]
        }
    
    def analyze(self, reviews: List[Dict[str, Any]]) -> BehaviorAnalysisResult:
        """
        Analyze user behavior from reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            BehaviorAnalysisResult with analysis results
        """
        logger.info(f"Analyzing behavior from {len(reviews)} reviews")
        
        # Extract texts
        texts = [review.get('content', '') for review in reviews]
        
        # Extract listening goals
        goals = self._extract_goals(texts)
        
        # Detect behavior patterns
        patterns = self._detect_patterns(texts, reviews)
        
        # Count habit indicators
        habit_indicators = self._count_habit_indicators(texts)
        
        # Generate summary
        summary = {
            'total_reviews': len(reviews),
            'goals_extracted': len(goals),
            'patterns_detected': len(patterns),
            'habit_indicators_found': sum(habit_indicators.values())
        }
        
        logger.info(
            f"Behavior analysis complete: {len(goals)} goals, "
            f"{len(patterns)} patterns, {sum(habit_indicators.values())} habit indicators"
        )
        
        return BehaviorAnalysisResult(
            goals=goals,
            patterns=patterns,
            habit_indicators=habit_indicators,
            summary=summary
        )
    
    def _extract_goals(self, texts: List[str]) -> List[ListeningGoal]:
        """Extract listening goals from texts"""
        goals = []
        goal_counts = defaultdict(int)
        
        for text in texts:
            text_lower = text.lower()
            for goal_type, patterns in self.goal_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        goal_counts[goal_type] += 1
                        break
        
        # Filter by minimum frequency
        for goal_type, count in goal_counts.items():
            if count >= self.min_frequency:
                confidence = min(count / len(texts), 1.0)
                goal = ListeningGoal(
                    goal_type=goal_type,
                    description=self._generate_goal_description(goal_type),
                    confidence=confidence
                )
                goals.append(goal)
        
        return goals
    
    def _detect_patterns(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[BehaviorPattern]:
        """Detect behavior patterns"""
        patterns = []
        
        # Analyze content for patterns
        pattern_keywords = {
            'discovery_focused': ['discover', 'new', 'explore', 'find'],
            'habitual': ['always', 'usually', 'typically', 'routine'],
            'mood_based': ['mood', 'feeling', 'emotional'],
            'activity_based': ['workout', 'study', 'work', 'sleep'],
            'social': ['party', 'friends', 'social', 'share'],
            'nostalgic': ['old', 'classic', 'memories', 'nostalgia']
        }
        
        for pattern_type, keywords in pattern_keywords.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in keywords):
                    matches.append(text)
            
            if len(matches) >= self.min_frequency:
                pattern = BehaviorPattern(
                    pattern_type=pattern_type,
                    description=self._generate_pattern_description(pattern_type),
                    frequency=len(matches),
                    examples=matches[:3]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _count_habit_indicators(self, texts: List[str]) -> Dict[str, int]:
        """Count habit indicators in texts"""
        habit_counts = defaultdict(int)
        
        for text in texts:
            text_lower = text.lower()
            for habit_type, patterns in self.habit_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        habit_counts[habit_type] += 1
                        break
        
        return dict(habit_counts)
    
    def _generate_goal_description(self, goal_type: str) -> str:
        """Generate human-readable goal description"""
        descriptions = {
            'mood_matching': 'Finding music to match current mood',
            'activity_matching': 'Finding music for specific activities',
            'discovery': 'Discovering new music and artists',
            'familiarity': 'Listening to familiar, comfortable content',
            'variety': 'Seeking variety and new experiences'
        }
        return descriptions.get(goal_type, goal_type)
    
    def _generate_pattern_description(self, pattern_type: str) -> str:
        """Generate human-readable pattern description"""
        descriptions = {
            'discovery_focused': 'User focuses on discovering new content',
            'habitual': 'User has habitual listening patterns',
            'mood_based': 'User selects music based on mood',
            'activity_based': 'User selects music for activities',
            'social': 'User uses music in social contexts',
            'nostalgic': 'User seeks nostalgic content'
        }
        return descriptions.get(pattern_type, pattern_type)
    
    def analyze_user_segments(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Segment users based on behavior patterns
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary mapping segment to list of user IDs
        """
        segments = defaultdict(list)
        
        for review in reviews:
            author = review.get('author')
            content = review.get('content', '').lower()
            
            if not author:
                continue
            
            # Segment based on content patterns
            if any(word in content for word in ['discover', 'new', 'explore']):
                segments['discovery_focused'].append(author)
            elif any(word in content for word in ['playlist', 'favorite', 'routine']):
                segments['habitual'].append(author)
            elif any(word in content for word in ['mood', 'feeling']):
                segments['mood_based'].append(author)
            elif any(word in content for word in ['workout', 'study', 'work']):
                segments['activity_based'].append(author)
            else:
                segments['general'].append(author)
        
        # Remove duplicates
        for segment in segments:
            segments[segment] = list(set(segments[segment]))
        
        return dict(segments)
    
    def get_statistics(self, result: BehaviorAnalysisResult) -> Dict[str, Any]:
        """
        Get statistics from behavior analysis result
        
        Args:
            result: BehaviorAnalysisResult object
            
        Returns:
            Dictionary with statistics
        """
        goal_distribution = defaultdict(int)
        for goal in result.goals:
            goal_distribution[goal.goal_type] += 1
        
        pattern_distribution = defaultdict(int)
        for pattern in result.patterns:
            pattern_distribution[pattern.pattern_type] += 1
        
        return {
            'summary': result.summary,
            'goal_distribution': dict(goal_distribution),
            'pattern_distribution': dict(pattern_distribution),
            'habit_indicators': result.habit_indicators
        }
