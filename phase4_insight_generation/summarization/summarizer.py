"""
Automated Summarization Module
Performs abstractive and extractive summarization of review data
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Summary:
    """Generated summary"""
    summary_text: str
    method: str
    length: int
    coverage_score: float


class Summarizer:
    """
    Automated summarization for review data
    Supports extractive and abstractive summarization approaches
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize summarizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.max_sentences = config.get('max_sentences', 5)
        self.min_sentence_length = config.get('min_sentence_length', 10)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))
    
    def summarize_extractive(self, texts: List[str]) -> Summary:
        """
        Perform extractive summarization using TF-IDF
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            Summary object
        """
        logger.info(f"Performing extractive summarization on {len(texts)} texts")
        
        # Combine texts
        combined_text = ' '.join(texts)
        
        # Split into sentences
        sentences = sent_tokenize(combined_text)
        
        # Filter short sentences
        sentences = [s for s in sentences if len(s.split()) >= self.min_sentence_length]
        
        if not sentences:
            return Summary(
                summary_text="No content to summarize",
                method="extractive",
                length=0,
                coverage_score=0.0
            )
        
        # Calculate sentence scores using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        sentence_vectors = vectorizer.fit_transform(sentences)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(sentence_vectors)
        
        # Calculate sentence scores
        sentence_scores = similarity_matrix.sum(axis=1)
        
        # Select top sentences
        top_indices = sentence_scores.argsort()[-self.max_sentences:][::-1]
        top_indices = sorted(top_indices)
        
        # Build summary
        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = ' '.join(summary_sentences)
        
        # Calculate coverage score
        coverage_score = len(summary_sentences) / len(sentences)
        
        return Summary(
            summary_text=summary_text,
            method="extractive",
            length=len(summary_sentences),
            coverage_score=coverage_score
        )
    
    def summarize_abstractive(self, texts: List[str]) -> Summary:
        """
        Perform abstractive summarization (simplified)
        Note: For production, use transformer models like BART, T5, or GPT
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            Summary object
        """
        logger.info(f"Performing abstractive summarization on {len(texts)} texts")
        
        # For now, use a simplified approach combining key phrases
        # In production, this would use transformer models
        combined_text = ' '.join(texts)
        
        # Extract key phrases (simplified)
        words = combined_text.lower().split()
        word_freq = defaultdict(int)
        
        for word in words:
            if word not in self.stop_words and len(word) > 3:
                word_freq[word] += 1
        
        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Generate summary from top words (simplified)
        summary_text = f"Key themes include: {', '.join([w for w, _ in top_words])}"
        
        return Summary(
            summary_text=summary_text,
            method="abstractive_simplified",
            length=len(summary_text.split('.')),
            coverage_score=0.5
        )
    
    def summarize_multi_document(self, documents: List[Dict[str, Any]]) -> Dict[str, Summary]:
        """
        Summarize multiple documents by category
        
        Args:
            documents: List of document dictionaries with 'content' and 'category' keys
            
        Returns:
            Dictionary mapping category to Summary
        """
        logger.info(f"Performing multi-document summarization on {len(documents)} documents")
        
        # Group by category
        documents_by_category = defaultdict(list)
        for doc in documents:
            category = doc.get('category', 'general')
            content = doc.get('content', '')
            if content:
                documents_by_category[category].append(content)
        
        # Summarize each category
        summaries = {}
        for category, texts in documents_by_category.items():
            if texts:
                summary = self.summarize_extractive(texts)
                summaries[category] = summary
        
        return summaries
    
    def summarize_insights(
        self,
        pain_points: List[str],
        opportunities: List[str],
        patterns: List[str]
    ) -> Dict[str, str]:
        """
        Summarize insights from analysis results
        
        Args:
            pain_points: List of pain point descriptions
            opportunities: List of opportunity descriptions
            patterns: List of pattern descriptions
            
        Returns:
            Dictionary with summary for each category
        """
        summaries = {}
        
        if pain_points:
            summary = self.summarize_extractive(pain_points)
            summaries['pain_points'] = summary.summary_text
        
        if opportunities:
            summary = self.summarize_extractive(opportunities)
            summaries['opportunities'] = summary.summary_text
        
        if patterns:
            summary = self.summarize_extractive(patterns)
            summaries['patterns'] = summary.summary_text
        
        return summaries
    
    def get_summary_statistics(self, summaries: List[Summary]) -> Dict[str, Any]:
        """
        Get statistics from summaries
        
        Args:
            summaries: List of Summary objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(summaries)
        avg_length = sum(s.length for s in summaries) / total if total > 0 else 0
        avg_coverage = sum(s.coverage_score for s in summaries) / total if total > 0 else 0
        
        method_counts = defaultdict(int)
        for summary in summaries:
            method_counts[summary.method] += 1
        
        return {
            'total_summaries': total,
            'average_length': avg_length,
            'average_coverage': avg_coverage,
            'method_distribution': dict(method_counts)
        }
