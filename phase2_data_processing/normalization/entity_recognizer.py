"""
Entity Recognition Module
Extracts named entities and Spotify-specific features from text
"""

from typing import Dict, Any, List, Optional, Set
import logging
from dataclasses import dataclass
from collections import defaultdict

import spacy
import re

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Named entity extracted from text"""
    text: str
    label: str
    start: int
    end: int
    confidence: float


@dataclass
class SpotifyFeature:
    """Spotify-specific feature extracted from text"""
    feature_name: str
    feature_type: str
    context: str


class EntityRecognizer:
    """
    Recognizes named entities and Spotify-specific features
    Uses spaCy for NER and custom patterns for Spotify features
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize entity recognizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.nlp = None
        
        # Spotify feature patterns
        self.spotify_features = {
            'discover_weekly': {
                'patterns': ['discover weekly', 'discover weekly playlist', 'dw'],
                'type': 'playlist'
            },
            'daily_mix': {
                'patterns': ['daily mix', 'daily mix 1', 'daily mix 2', 'daily mix 3'],
                'type': 'playlist'
            },
            'ai_dj': {
                'patterns': ['ai dj', 'dj', 'spotify dj', 'ai-dj'],
                'type': 'feature'
            },
            'radio': {
                'patterns': ['radio', 'song radio', 'artist radio', 'playlist radio'],
                'type': 'feature'
            },
            'release_radar': {
                'patterns': ['release radar', 'new releases'],
                'type': 'playlist'
            },
            'on_repeat': {
                'patterns': ['on repeat', 'repeat songs'],
                'type': 'playlist'
            },
            'time_capsule': {
                'patterns': ['time capsule', 'time capsule playlist'],
                'type': 'playlist'
            },
            'wrapped': {
                'patterns': ['wrapped', 'spotify wrapped', 'year in review'],
                'type': 'feature'
            },
            'blend': {
                'patterns': ['blend', 'blend playlist'],
                'type': 'playlist'
            },
            'family_mix': {
                'patterns': ['family mix', 'family playlist'],
                'type': 'playlist'
            }
        }
        
        # Genre patterns
        self.genre_patterns = [
            'pop', 'rock', 'hip hop', 'rap', 'r&b', 'jazz', 'classical',
            'electronic', 'edm', 'country', 'folk', 'blues', 'metal',
            'indie', 'alternative', 'punk', 'reggae', 'latin', 'k-pop',
            'lo-fi', 'ambient', 'techno', 'house', 'trap', 'soul'
        ]
        
        self._initialize_nlp()
    
    def _initialize_nlp(self) -> None:
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model loaded successfully for entity recognition")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}")
            logger.info("Entity recognition will use pattern matching only")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of Entity objects
        """
        entities = []
        
        if self.nlp:
            # Use spaCy NER
            doc = self.nlp(text)
            for ent in doc.ents:
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0  # spaCy doesn't provide confidence
                )
                entities.append(entity)
        
        return entities
    
    def extract_spotify_features(self, text: str) -> List[SpotifyFeature]:
        """
        Extract Spotify-specific features from text
        
        Args:
            text: Text to extract features from
            
        Returns:
            List of SpotifyFeature objects
        """
        features = []
        text_lower = text.lower()
        
        for feature_name, feature_info in self.spotify_features.items():
            for pattern in feature_info['patterns']:
                if pattern in text_lower:
                    # Find context around the pattern
                    context = self._extract_context(text, pattern)
                    
                    feature = SpotifyFeature(
                        feature_name=feature_name,
                        feature_type=feature_info['type'],
                        context=context
                    )
                    features.append(feature)
                    break  # Only add each feature once
        
        return features
    
    def extract_genres(self, text: str) -> List[str]:
        """
        Extract music genres mentioned in text
        
        Args:
            text: Text to extract genres from
            
        Returns:
            List of genre names
        """
        text_lower = text.lower()
        found_genres = []
        
        for genre in self.genre_patterns:
            if genre in text_lower:
                found_genres.append(genre)
        
        return found_genres
    
    def extract_artists(self, text: str) -> List[str]:
        """
        Extract artist names from text using NER
        
        Args:
            text: Text to extract artists from
            
        Returns:
            List of artist names
        """
        artists = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # PERSON entities might be artists
                if ent.label_ == 'PERSON':
                    artists.append(ent.text)
        
        return artists
    
    def extract_moods(self, text: str) -> List[str]:
        """
        Extract mood-related terms from text
        
        Args:
            text: Text to extract moods from
            
        Returns:
            List of mood terms
        """
        mood_patterns = [
            'happy', 'sad', 'angry', 'calm', 'energetic', 'relaxed',
            'upbeat', 'melancholy', 'chill', 'excited', 'peaceful',
            'romantic', 'nostalgic', 'motivational', 'focus', 'sleep',
            'workout', 'party', 'study', 'meditation', 'road trip'
        ]
        
        text_lower = text.lower()
        found_moods = []
        
        for mood in mood_patterns:
            if mood in text_lower:
                found_moods.append(mood)
        
        return found_moods
    
    def _extract_context(self, text: str, pattern: str, window: int = 50) -> str:
        """
        Extract context around a pattern in text
        
        Args:
            text: Full text
            pattern: Pattern to find
            window: Number of characters before and after
            
        Returns:
            Context string
        """
        pattern_lower = pattern.lower()
        text_lower = text.lower()
        
        idx = text_lower.find(pattern_lower)
        if idx == -1:
            return ""
        
        start = max(0, idx - window)
        end = min(len(text), idx + len(pattern) + window)
        
        context = text[start:end]
        return context.strip()
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities and features from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with all extracted information
        """
        return {
            'entities': self.extract_entities(text),
            'spotify_features': self.extract_spotify_features(text),
            'genres': self.extract_genres(text),
            'artists': self.extract_artists(text),
            'moods': self.extract_moods(text)
        }
    
    def extract_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Extract entities and features from multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of dictionaries with extracted information
        """
        results = []
        for text in texts:
            result = self.extract_all(text)
            results.append(result)
        
        return results
    
    def get_statistics(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics from entity extraction results
        
        Args:
            results: List of extraction result dictionaries
            
        Returns:
            Dictionary with statistics
        """
        total = len(results)
        
        # Count feature occurrences
        feature_counts = defaultdict(int)
        genre_counts = defaultdict(int)
        mood_counts = defaultdict(int)
        
        for result in results:
            for feature in result['spotify_features']:
                feature_counts[feature.feature_name] += 1
            
            for genre in result['genres']:
                genre_counts[genre] += 1
            
            for mood in result['moods']:
                mood_counts[mood] += 1
        
        return {
            'total_texts': total,
            'feature_counts': dict(feature_counts),
            'genre_counts': dict(genre_counts),
            'mood_counts': dict(mood_counts),
            'avg_entities_per_text': sum(len(r['entities']) for r in results) / total if total > 0 else 0
        }
