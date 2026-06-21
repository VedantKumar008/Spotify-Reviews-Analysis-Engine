"""
Spam Detection Module
Uses ML-based classification to detect spam and bot-generated content
"""

from typing import Dict, Any, List, Optional
import logging
import re
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import spacy

logger = logging.getLogger(__name__)


@dataclass
class SpamDetectionResult:
    """Result of spam detection"""
    is_spam: bool
    confidence: float
    reasons: List[str]
    spam_type: Optional[str] = None


class SpamDetector:
    """
    ML-based spam detector for review content
    Uses multiple heuristics and ML classification
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize spam detector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model = None
        self.vectorizer = None
        self.nlp = None
        self.threshold = config.get('spam_threshold', 0.7)
        
        # Spam patterns
        self.spam_patterns = [
            r'buy\s+now',
            r'click\s+here',
            r'free\s+download',
            r'limited\s+time',
            r'act\s+now',
            r'winner',
            r'congratulations',
            r'verify\s+your',
            r'account\s+suspended',
            r'urgent',
            r'crypto',
            r'bitcoin',
            r'investment',
            r'lottery',
            r'prize',
            r'click\s+link',
            r'http[s]?://\S+',
            r'www\.\S+',
        ]
        
        self._initialize_nlp()
    
    def _initialize_nlp(self) -> None:
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}")
            logger.info("SpaCy features will be disabled")
    
    def train(self, labeled_data: List[Dict[str, Any]]) -> None:
        """
        Train the spam detection model
        
        Args:
            labeled_data: List of dictionaries with 'content' and 'is_spam' keys
        """
        try:
            texts = [item['content'] for item in labeled_data]
            labels = [item['is_spam'] for item in labeled_data]
            
            # Create TF-IDF features
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            X = self.vectorizer.fit_transform(texts)
            y = np.array(labels)
            
            # Train Random Forest classifier
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.model.fit(X, y)
            logger.info("Spam detection model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training spam detector: {str(e)}")
            raise
    
    def detect_spam(self, content: str) -> SpamDetectionResult:
        """
        Detect if content is spam
        
        Args:
            content: Text content to analyze
            
        Returns:
            SpamDetectionResult with classification and confidence
        """
        reasons = []
        confidence = 0.0
        spam_type = None
        
        # Pattern-based detection
        pattern_score = self._check_patterns(content)
        if pattern_score > 0:
            reasons.append("Contains spam-like patterns")
            confidence += pattern_score * 0.3
        
        # Length-based detection
        length_score = self._check_length(content)
        if length_score > 0:
            reasons.append("Suspicious length")
            confidence += length_score * 0.2
        
        # Repetition detection
        repetition_score = self._check_repetition(content)
        if repetition_score > 0:
            reasons.append("Excessive repetition")
            confidence += repetition_score * 0.2
        
        # URL detection
        url_score = self._check_urls(content)
        if url_score > 0:
            reasons.append("Contains suspicious URLs")
            confidence += url_score * 0.2
        
        # ML-based detection (if model is trained)
        if self.model and self.vectorizer:
            ml_score = self._ml_detect(content)
            confidence += ml_score * 0.1
            if ml_score > 0.5:
                reasons.append("ML classifier flags as spam")
        
        # Determine spam type
        if confidence > 0.6:
            if pattern_score > 0.5:
                spam_type = "promotional"
            elif url_score > 0.5:
                spam_type = "phishing"
            elif repetition_score > 0.5:
                spam_type = "bot_generated"
            else:
                spam_type = "suspicious"
        
        is_spam = confidence >= self.threshold
        
        return SpamDetectionResult(
            is_spam=is_spam,
            confidence=min(confidence, 1.0),
            reasons=reasons,
            spam_type=spam_type
        )
    
    def _check_patterns(self, content: str) -> float:
        """Check for spam patterns in content"""
        score = 0.0
        content_lower = content.lower()
        
        for pattern in self.spam_patterns:
            if re.search(pattern, content_lower):
                score += 0.2
        
        return min(score, 1.0)
    
    def _check_length(self, content: str) -> float:
        """Check for suspicious content length"""
        length = len(content)
        
        # Very short content might be spam
        if length < 10:
            return 0.8
        elif length < 20:
            return 0.5
        elif length < 30:
            return 0.3
        
        # Very long content might be spam
        if length > 5000:
            return 0.6
        elif length > 3000:
            return 0.4
        
        return 0.0
    
    def _check_repetition(self, content: str) -> float:
        """Check for excessive repetition"""
        words = content.split()
        if len(words) < 5:
            return 0.0
        
        # Calculate ratio of unique words to total words
        unique_words = len(set(words))
        ratio = unique_words / len(words)
        
        if ratio < 0.3:
            return 0.8
        elif ratio < 0.5:
            return 0.5
        elif ratio < 0.7:
            return 0.3
        
        return 0.0
    
    def _check_urls(self, content: str) -> float:
        """Check for suspicious URLs"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        if not urls:
            return 0.0
        
        # Multiple URLs is suspicious
        if len(urls) >= 3:
            return 0.9
        elif len(urls) >= 2:
            return 0.6
        else:
            return 0.3
    
    def _ml_detect(self, content: str) -> float:
        """Use ML model to detect spam"""
        try:
            X = self.vectorizer.transform([content])
            probability = self.model.predict_proba(X)[0][1]
            return probability
        except Exception as e:
            logger.warning(f"ML detection failed: {str(e)}")
            return 0.0
    
    def detect_batch(self, contents: List[str]) -> List[SpamDetectionResult]:
        """
        Detect spam for multiple contents
        
        Args:
            contents: List of text contents
            
        Returns:
            List of SpamDetectionResult objects
        """
        results = []
        for content in contents:
            result = self.detect_spam(content)
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[SpamDetectionResult]) -> Dict[str, Any]:
        """
        Get statistics from spam detection results
        
        Args:
            results: List of SpamDetectionResult objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(results)
        spam_count = sum(1 for r in results if r.is_spam)
        
        spam_types = {}
        for result in results:
            if result.spam_type:
                spam_types[result.spam_type] = spam_types.get(result.spam_type, 0) + 1
        
        return {
            'total': total,
            'spam_count': spam_count,
            'spam_rate': spam_count / total if total > 0 else 0,
            'spam_types': spam_types
        }
