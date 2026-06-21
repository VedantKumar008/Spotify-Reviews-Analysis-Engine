"""
Theme Taxonomy Module
Creates hierarchical theme structure and maps theme relationships
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Theme:
    """Theme in the taxonomy"""
    theme_id: str
    name: str
    parent_id: Optional[str]
    level: int
    description: str
    keywords: List[str]
    frequency: int


@dataclass
class ThemeRelationship:
    """Relationship between themes"""
    theme_id_1: str
    theme_id_2: str
    relationship_type: str  # parent-child, related, co-occurring
    strength: float


class ThemeTaxonomy:
    """
    Creates and manages hierarchical theme taxonomy
    Organizes themes into parent-child relationships and maps theme evolution
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize theme taxonomy
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.themes: Dict[str, Theme] = {}
        self.relationships: List[ThemeRelationship] = []
        
        # Define base taxonomy structure
        self.base_taxonomy = {
            'discovery': {
                'description': 'Music discovery and exploration',
                'level': 0,
                'children': ['discover_weekly', 'ai_dj', 'daily_mix', 'radio', 'search']
            },
            'recommendations': {
                'description': 'Recommendation system experiences',
                'level': 0,
                'children': ['algorithm_quality', 'personalization', 'variety', 'context_awareness']
            },
            'ui_ux': {
                'description': 'User interface and user experience',
                'level': 0,
                'children': ['navigation', 'performance', 'design', 'crashes_bugs']
            },
            'content': {
                'description': 'Content-related feedback',
                'level': 0,
                'children': ['artists', 'genres', 'playlists', 'albums', 'songs']
            },
            'features': {
                'description': 'Spotify features and functionality',
                'level': 0,
                'children': ['offline_mode', 'cross_platform', 'social_features', 'premium_features']
            }
        }
        
        # Sub-theme definitions
        self.sub_themes = {
            'discover_weekly': {
                'description': 'Discover Weekly playlist feedback',
                'keywords': ['discover weekly', 'dw', 'weekly discovery']
            },
            'ai_dj': {
                'description': 'AI DJ feature feedback',
                'keywords': ['ai dj', 'dj', 'spotify dj', 'ai-dj']
            },
            'daily_mix': {
                'description': 'Daily Mix playlists feedback',
                'keywords': ['daily mix', 'mix 1', 'mix 2', 'mix 3']
            },
            'radio': {
                'description': 'Radio feature feedback',
                'keywords': ['radio', 'song radio', 'artist radio']
            },
            'search': {
                'description': 'Search functionality feedback',
                'keywords': ['search', 'find', 'browse', 'lookup']
            },
            'algorithm_quality': {
                'description': 'Recommendation algorithm quality',
                'keywords': ['algorithm', 'recommendation quality', 'suggestions']
            },
            'personalization': {
                'description': 'Personalization effectiveness',
                'keywords': ['personalize', 'custom', 'tailored', 'my taste']
            },
            'variety': {
                'description': 'Content variety in recommendations',
                'keywords': ['variety', 'diverse', 'different', 'not repetitive']
            },
            'context_awareness': {
                'description': 'Context-aware recommendations',
                'keywords': ['context', 'mood', 'situation', 'time', 'activity']
            }
        }
    
    def build_taxonomy(self, reviews: List[Dict[str, Any]]) -> Dict[str, Theme]:
        """
        Build theme taxonomy from reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary mapping theme_id to Theme objects
        """
        logger.info(f"Building theme taxonomy from {len(reviews)} reviews")
        
        # Initialize base themes
        for theme_id, theme_info in self.base_taxonomy.items():
            self.themes[theme_id] = Theme(
                theme_id=theme_id,
                name=theme_id.replace('_', ' ').title(),
                parent_id=None,
                level=theme_info['level'],
                description=theme_info['description'],
                keywords=[],
                frequency=0
            )
        
        # Initialize sub-themes
        for parent_id, theme_info in self.base_taxonomy.items():
            for child_id in theme_info['children']:
                if child_id in self.sub_themes:
                    child_info = self.sub_themes[child_id]
                    self.themes[child_id] = Theme(
                        theme_id=child_id,
                        name=child_id.replace('_', ' ').title(),
                        parent_id=parent_id,
                        level=1,
                        description=child_info['description'],
                        keywords=child_info['keywords'],
                        frequency=0
                    )
        
        # Count theme frequencies from reviews
        for review in reviews:
            content = review.get('content', '').lower()
            
            for theme_id, theme in self.themes.items():
                # Check if theme keywords appear in content
                if theme.keywords:
                    if any(keyword in content for keyword in theme.keywords):
                        theme.frequency += 1
                else:
                    # For base themes without keywords, use name matching
                    if theme.name.lower() in content:
                        theme.frequency += 1
        
        # Build relationships
        self._build_relationships()
        
        logger.info(f"Taxonomy built: {len(self.themes)} themes, {len(self.relationships)} relationships")
        
        return self.themes
    
    def _build_relationships(self) -> None:
        """Build relationships between themes"""
        # Parent-child relationships
        for theme_id, theme in self.themes.items():
            if theme.parent_id:
                relationship = ThemeRelationship(
                    theme_id_1=theme.parent_id,
                    theme_id_2=theme_id,
                    relationship_type='parent-child',
                    strength=1.0
                )
                self.relationships.append(relationship)
        
        # Co-occurrence relationships (simplified)
        # In production, this would analyze actual co-occurrence patterns
        related_pairs = [
            ('discover_weekly', 'algorithm_quality'),
            ('ai_dj', 'personalization'),
            ('daily_mix', 'variety'),
            ('search', 'discovery'),
            ('personalization', 'context_awareness')
        ]
        
        for theme_id_1, theme_id_2 in related_pairs:
            if theme_id_1 in self.themes and theme_id_2 in self.themes:
                relationship = ThemeRelationship(
                    theme_id_1=theme_id_1,
                    theme_id_2=theme_id_2,
                    relationship_type='related',
                    strength=0.7
                )
                self.relationships.append(relationship)
    
    def get_theme_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get hierarchical structure of themes
        
        Returns:
            Dictionary mapping parent theme to list of child themes
        """
        hierarchy = defaultdict(list)
        
        for theme_id, theme in self.themes.items():
            if theme.parent_id:
                hierarchy[theme.parent_id].append(theme_id)
        
        return dict(hierarchy)
    
    def get_theme_by_level(self, level: int) -> List[Theme]:
        """
        Get themes at a specific level
        
        Args:
            level: Theme level (0 for top-level, 1 for sub-themes)
            
        Returns:
            List of Theme objects at the specified level
        """
        return [theme for theme in self.themes.values() if theme.level == level]
    
    def get_theme_evolution(self, reviews_by_time: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Track theme evolution over time
        
        Args:
            reviews_by_time: Dictionary mapping time period to list of reviews
            
        Returns:
            Dictionary with theme evolution data
        """
        evolution = {}
        
        for time_period, reviews in reviews_by_time.items():
            period_themes = {}
            
            for review in reviews:
                content = review.get('content', '').lower()
                
                for theme_id, theme in self.themes.items():
                    if theme.keywords:
                        if any(keyword in content for keyword in theme.keywords):
                            period_themes[theme_id] = period_themes.get(theme_id, 0) + 1
            
            evolution[time_period] = period_themes
        
        return evolution
    
    def get_theme_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about themes
        
        Returns:
            Dictionary with theme statistics
        """
        total_themes = len(self.themes)
        total_frequency = sum(theme.frequency for theme in self.themes.values())
        
        level_distribution = defaultdict(int)
        for theme in self.themes.values():
            level_distribution[theme.level] += 1
        
        top_themes = sorted(
            self.themes.values(),
            key=lambda t: t.frequency,
            reverse=True
        )[:10]
        
        return {
            'total_themes': total_themes,
            'total_frequency': total_frequency,
            'level_distribution': dict(level_distribution),
            'top_themes': [
                {'theme_id': t.theme_id, 'name': t.name, 'frequency': t.frequency}
                for t in top_themes
            ],
            'total_relationships': len(self.relationships)
        }
