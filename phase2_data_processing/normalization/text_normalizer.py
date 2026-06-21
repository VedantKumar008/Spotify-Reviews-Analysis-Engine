"""
Text Normalization Module
Handles tokenization, stopword removal, lemmatization, and emoji handling
"""

from typing import Dict, Any, List, Optional
import logging
import re
from dataclasses import dataclass

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import emoji

logger = logging.getLogger(__name__)


@dataclass
class NormalizedText:
    """Result of text normalization"""
    original: str
    normalized: str
    tokens: List[str]
    lemmas: List[str]
    emoji_count: int
    emoji_descriptions: List[str]


class TextNormalizer:
    """
    Normalizes text for NLP processing
    Handles tokenization, stopword removal, lemmatization, and emoji handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize text normalizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.remove_stopwords = config.get('remove_stopwords', True)
        self.lemmatize = config.get('lemmatize', True)
        self.handle_emojis = config.get('handle_emojis', True)
        self.lowercase = config.get('lowercase', True)
        
        self.nlp = None
        self.lemmatizer = None
        self.stop_words = None
        
        self._initialize_nlp()
        self._initialize_nltk()
    
    def _initialize_nlp(self) -> None:
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}")
            logger.info("SpaCy features will be disabled")
    
    def _initialize_nltk(self) -> None:
        """Initialize NLTK resources"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            
            # Initialize lemmatizer
            self.lemmatizer = WordNetLemmatizer()
            
            # Load stopwords
            self.stop_words = set(stopwords.words('english'))
            
            logger.info("NLTK resources loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load NLTK resources: {str(e)}")
            logger.info("NLTK features will be disabled")
    
    def normalize(self, text: str) -> NormalizedText:
        """
        Normalize text
        
        Args:
            text: Text to normalize
            
        Returns:
            NormalizedText object with normalized content
        """
        original = text
        emoji_descriptions = []
        emoji_count = 0
        
        # Handle emojis
        if self.handle_emojis:
            text, emoji_descriptions, emoji_count = self._handle_emojis(text)
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove special characters (keep letters, numbers, and basic punctuation)
        text = self._remove_special_characters(text)
        
        # Tokenize
        tokens = self._tokenize(text)
        
        # Remove stopwords
        if self.remove_stopwords and self.stop_words:
            tokens = [t for t in tokens if t not in self.stop_words]
        
        # Lemmatize
        lemmas = tokens
        if self.lemmatize and self.lemmatizer:
            lemmas = [self.lemmatizer.lemmatize(t) for t in tokens]
        
        # Reconstruct normalized text
        normalized = ' '.join(lemmas)
        
        return NormalizedText(
            original=original,
            normalized=normalized,
            tokens=tokens,
            lemmas=lemmas,
            emoji_count=emoji_count,
            emoji_descriptions=emoji_descriptions
        )
    
    def _handle_emojis(self, text: str) -> tuple[str, List[str], int]:
        """
        Handle emojis in text
        
        Args:
            text: Text with emojis
            
        Returns:
            Tuple of (text without emojis, emoji descriptions, emoji count)
        """
        emoji_count = 0
        emoji_descriptions = []
        
        # Find all emojis
        emojis = emoji.emoji_list(text)
        
        for emoji_char, start, end in emojis:
            emoji_count += 1
            # Get emoji description
            description = emoji.demojize(emoji_char).strip(':')
            emoji_descriptions.append(description)
        
        # Remove emojis from text
        text_without_emojis = emoji.replace_emoji(text, '')
        
        # Add emoji descriptions as text
        if emoji_descriptions:
            text_without_emojis += ' ' + ' '.join(emoji_descriptions)
        
        return text_without_emojis, emoji_descriptions, emoji_count
    
    def _remove_special_characters(self, text: str) -> str:
        """
        Remove special characters from text
        
        Args:
            text: Text to clean
            
        Returns:
            Text with special characters removed
        """
        # Keep letters, numbers, spaces, and basic punctuation
        pattern = r'[^a-zA-Z0-9\s.,!?;:\'"-]'
        text = re.sub(pattern, '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if self.nlp:
            # Use spaCy for tokenization
            doc = self.nlp(text)
            tokens = [token.text for token in doc if not token.is_space]
        else:
            # Use NLTK as fallback
            tokens = word_tokenize(text)
        
        return tokens
    
    def normalize_batch(self, texts: List[str]) -> List[NormalizedText]:
        """
        Normalize multiple texts
        
        Args:
            texts: List of texts to normalize
            
        Returns:
            List of NormalizedText objects
        """
        results = []
        for text in texts:
            result = self.normalize(text)
            results.append(result)
        
        return results
    
    def get_statistics(
        self,
        results: List[NormalizedText]
    ) -> Dict[str, Any]:
        """
        Get statistics from normalization results
        
        Args:
            results: List of NormalizedText objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(results)
        total_emojis = sum(r.emoji_count for r in results)
        avg_tokens = sum(len(r.tokens) for r in results) / total if total > 0 else 0
        avg_lemmas = sum(len(r.lemmas) for r in results) / total if total > 0 else 0
        
        return {
            'total_texts': total,
            'total_emojis': total_emojis,
            'avg_tokens_per_text': avg_tokens,
            'avg_lemmas_per_text': avg_lemmas,
            'avg_emoji_per_text': total_emojis / total if total > 0 else 0
        }
