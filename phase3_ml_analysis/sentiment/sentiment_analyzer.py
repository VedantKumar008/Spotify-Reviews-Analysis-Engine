"""
Sentiment Analysis Module
Performs multi-dimensional sentiment analysis including overall sentiment, aspect-based sentiment, and emotion detection
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

from textblob import TextBlob
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    overall_sentiment: str  # positive, negative, neutral
    sentiment_score: float  # -1 to 1
    confidence: float
    emotions: Dict[str, float]
    aspects: Dict[str, str]


class SentimentAnalyzer:
    """
    Multi-dimensional sentiment analyzer
    Performs overall sentiment, aspect-based sentiment, and emotion detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize sentiment analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        
        # Emotion keywords
        self.emotion_keywords = {
            'joy': ['happy', 'love', 'great', 'amazing', 'excellent', 'wonderful', 'fantastic', 'awesome'],
            'sadness': ['sad', 'disappointed', 'terrible', 'awful', 'bad', 'worst', 'hate', 'frustrated'],
            'anger': ['angry', 'furious', 'annoyed', 'irritated', 'mad', 'rage', 'upset'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'concerned'],
            'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'wow'],
            'disgust': ['disgusting', 'gross', 'terrible', 'awful', 'hate']
        }
        
        # Spotify-specific aspects
        self.spotify_aspects = {
            'discover_weekly': ['discover weekly', 'dw', 'weekly discovery'],
            'recommendations': ['recommend', 'suggestion', 'algorithm'],
            'ui_ux': ['interface', 'app', 'crash', 'bug', 'slow', 'design'],
            'content': ['song', 'artist', 'album', 'music', 'playlist'],
            'features': ['feature', 'update', 'new', 'add', 'improve'],
            'performance': ['performance', 'load', 'buffer', 'stream', 'speed']
        }
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with analysis results
        """
        # Overall sentiment using TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine overall sentiment
        if polarity > 0.1:
            overall_sentiment = 'positive'
        elif polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Confidence based on subjectivity and polarity strength
        confidence = min(abs(polarity) + (1 - subjectivity) * 0.5, 1.0)
        
        # Emotion detection
        emotions = self._detect_emotions(text)
        
        # Aspect-based sentiment
        aspects = self._analyze_aspects(text)
        
        return SentimentResult(
            overall_sentiment=overall_sentiment,
            sentiment_score=polarity,
            confidence=confidence,
            emotions=emotions,
            aspects=aspects
        )
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in text using keyword matching
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with emotion scores
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = min(score / 3.0, 1.0)  # Normalize to 0-1
        
        return emotion_scores
    
    def _analyze_aspects(self, text: str) -> Dict[str, str]:
        """
        Analyze sentiment for specific aspects
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping aspect to sentiment
        """
        text_lower = text.lower()
        aspect_sentiments = {}
        
        for aspect, keywords in self.spotify_aspects.items():
            # Check if aspect is mentioned
            if any(keyword in text_lower for keyword in keywords):
                # Analyze sentiment for sentences containing aspect keywords
                sentences = text.split('.')
                aspect_sentences = [
                    sent for sent in sentences
                    if any(keyword in sent.lower() for keyword in keywords)
                ]
                
                if aspect_sentences:
                    # Analyze sentiment of aspect-specific sentences
                    combined_text = '. '.join(aspect_sentences)
                    blob = TextBlob(combined_text)
                    polarity = blob.sentiment.polarity
                    
                    if polarity > 0.1:
                        sentiment = 'positive'
                    elif polarity < -0.1:
                        sentiment = 'negative'
                    else:
                        sentiment = 'neutral'
                    
                    aspect_sentiments[aspect] = sentiment
        
        return aspect_sentiments
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of SentimentResult objects
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[SentimentResult]) -> Dict[str, Any]:
        """
        Get statistics from sentiment analysis results
        
        Args:
            results: List of SentimentResult objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(results)
        
        # Sentiment distribution
        sentiment_counts = defaultdict(int)
        for result in results:
            sentiment_counts[result.overall_sentiment] += 1
        
        # Average sentiment score
        avg_score = sum(r.sentiment_score for r in results) / total if total > 0 else 0
        
        # Average confidence
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0
        
        # Emotion distribution
        emotion_totals = defaultdict(float)
        for result in results:
            for emotion, score in result.emotions.items():
                emotion_totals[emotion] += score
        
        emotion_averages = {
            emotion: total / total if total > 0 else 0
            for emotion, total in emotion_totals.items()
        }
        
        # Aspect sentiment distribution
        aspect_sentiments = defaultdict(lambda: defaultdict(int))
        for result in results:
            for aspect, sentiment in result.aspects.items():
                aspect_sentiments[aspect][sentiment] += 1
        
        return {
            'total_analyzed': total,
            'sentiment_distribution': dict(sentiment_counts),
            'average_sentiment_score': avg_score,
            'average_confidence': avg_confidence,
            'emotion_distribution': emotion_averages,
            'aspect_sentiments': dict(aspect_sentiments)
        }
