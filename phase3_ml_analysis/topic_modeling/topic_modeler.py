"""
Topic Modeling Module
Performs topic modeling and clustering using BERTopic and traditional methods
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import LatentDirichletAllocation

logger = logging.getLogger(__name__)


@dataclass
class Topic:
    """Topic representation"""
    topic_id: int
    words: List[str]
    weights: List[float]
    description: str


@dataclass
class TopicModelingResult:
    """Result of topic modeling"""
    topics: List[Topic]
    document_topics: List[int]
    coherence_score: float


class TopicModeler:
    """
    Topic modeling using multiple approaches
    Supports LDA, K-means clustering, and BERTopic-style approaches
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize topic modeler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.method = config.get('method', 'lda')  # lda, kmeans, dbscan
        self.n_topics = config.get('n_topics', 10)
        self.max_features = config.get('max_features', 1000)
        self.min_df = config.get('min_df', 2)
        self.max_df = config.get('max_df', 0.8)
        
        self.vectorizer = None
        self.model = None
        self.feature_names = None
    
    def fit(self, documents: List[str]) -> TopicModelingResult:
        """
        Fit topic model on documents
        
        Args:
            documents: List of document texts
            
        Returns:
            TopicModelingResult with topics and assignments
        """
        logger.info(f"Fitting topic model on {len(documents)} documents using {self.method}")
        
        # Vectorize documents
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            min_df=self.min_df,
            max_df=self.max_df,
            stop_words='english'
        )
        
        X = self.vectorizer.fit_transform(documents)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        # Fit model based on method
        if self.method == 'lda':
            result = self._fit_lda(X, documents)
        elif self.method == 'kmeans':
            result = self._fit_kmeans(X, documents)
        elif self.method == 'dbscan':
            result = self._fit_dbscan(X, documents)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        logger.info(f"Topic modeling complete: {len(result.topics)} topics found")
        
        return result
    
    def _fit_lda(self, X, documents: List[str]) -> TopicModelingResult:
        """Fit LDA model"""
        self.model = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42,
            max_iter=10
        )
        
        self.model.fit(X)
        
        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(self.model.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [self.feature_names[i] for i in top_words_idx]
            weights = [topic[i] for i in top_words_idx]
            
            topic_obj = Topic(
                topic_id=topic_idx,
                words=top_words,
                weights=weights,
                description=self._generate_topic_description(top_words)
            )
            topics.append(topic_obj)
        
        # Get document-topic assignments
        document_topics = self.model.transform(X).argmax(axis=1)
        
        # Calculate coherence (simplified)
        coherence_score = self._calculate_coherence(topics)
        
        return TopicModelingResult(
            topics=topics,
            document_topics=document_topics.tolist(),
            coherence_score=coherence_score
        )
    
    def _fit_kmeans(self, X, documents: List[str]) -> TopicModelingResult:
        """Fit K-means clustering"""
        self.model = KMeans(
            n_clusters=self.n_topics,
            random_state=42,
            n_init=10
        )
        
        clusters = self.model.fit_predict(X)
        
        # Extract topics from cluster centers
        topics = []
        for cluster_idx in range(self.n_topics):
            center = self.model.cluster_centers_[cluster_idx]
            top_words_idx = center.argsort()[-10:][::-1]
            top_words = [self.feature_names[i] for i in top_words_idx]
            weights = [center[i] for i in top_words_idx]
            
            topic_obj = Topic(
                topic_id=cluster_idx,
                words=top_words,
                weights=weights,
                description=self._generate_topic_description(top_words)
            )
            topics.append(topic_obj)
        
        # Calculate coherence
        coherence_score = self._calculate_coherence(topics)
        
        return TopicModelingResult(
            topics=topics,
            document_topics=clusters.tolist(),
            coherence_score=coherence_score
        )
    
    def _fit_dbscan(self, X, documents: List[str]) -> TopicModelingResult:
        """Fit DBSCAN clustering"""
        self.model = DBSCAN(
            eps=0.5,
            min_samples=5,
            metric='cosine'
        )
        
        clusters = self.model.fit_predict(X)
        
        # Get unique clusters (excluding noise labeled as -1)
        unique_clusters = set(clusters)
        unique_clusters.discard(-1)
        
        # Extract topics from clusters
        topics = []
        cluster_to_topic_id = {}
        topic_id = 0
        
        for cluster_idx in unique_clusters:
            # Get documents in this cluster
            cluster_docs_idx = [i for i, c in enumerate(clusters) if c == cluster_idx]
            cluster_X = X[cluster_docs_idx]
            
            # Get centroid
            centroid = cluster_X.mean(axis=0).A1 if hasattr(cluster_X, 'toarray') else cluster_X.mean(axis=0)
            top_words_idx = centroid.argsort()[-10:][::-1]
            top_words = [self.feature_names[i] for i in top_words_idx]
            weights = [centroid[i] for i in top_words_idx]
            
            topic_obj = Topic(
                topic_id=topic_id,
                words=top_words,
                weights=weights,
                description=self._generate_topic_description(top_words)
            )
            topics.append(topic_obj)
            cluster_to_topic_id[cluster_idx] = topic_id
            topic_id += 1
        
        # Map cluster assignments to topic IDs
        document_topics = [
            cluster_to_topic_id.get(c, -1) for c in clusters
        ]
        
        # Calculate coherence
        coherence_score = self._calculate_coherence(topics)
        
        return TopicModelingResult(
            topics=topics,
            document_topics=document_topics,
            coherence_score=coherence_score
        )
    
    def _generate_topic_description(self, words: List[str]) -> str:
        """Generate a human-readable topic description"""
        return ", ".join(words[:5])
    
    def _calculate_coherence(self, topics: List[Topic]) -> float:
        """Calculate simplified coherence score"""
        # Simplified coherence based on word uniqueness
        all_words = []
        for topic in topics:
            all_words.extend(topic.words)
        
        unique_ratio = len(set(all_words)) / len(all_words) if all_words else 0
        return unique_ratio
    
    def predict(self, documents: List[str]) -> List[int]:
        """
        Predict topics for new documents
        
        Args:
            documents: List of document texts
            
        Returns:
            List of topic IDs
        """
        if not self.vectorizer or not self.model:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        X = self.vectorizer.transform(documents)
        
        if self.method == 'lda':
            topics = self.model.transform(X).argmax(axis=1)
        elif self.method in ['kmeans', 'dbscan']:
            topics = self.model.predict(X)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        return topics.tolist()
    
    def get_topic_words(self, topic_id: int, n_words: int = 10) -> List[str]:
        """
        Get top words for a specific topic
        
        Args:
            topic_id: Topic ID
            n_words: Number of words to return
            
        Returns:
            List of top words
        """
        if not self.model:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        if self.method == 'lda':
            topic = self.model.components_[topic_id]
            top_words_idx = topic.argsort()[-n_words:][::-1]
            return [self.feature_names[i] for i in top_words_idx]
        elif self.method == 'kmeans':
            center = self.model.cluster_centers_[topic_id]
            top_words_idx = center.argsort()[-n_words:][::-1]
            return [self.feature_names[i] for i in top_words_idx]
        else:
            raise ValueError(f"Word extraction not implemented for {self.method}")
    
    def get_statistics(self, result: TopicModelingResult) -> Dict[str, Any]:
        """
        Get statistics from topic modeling result
        
        Args:
            result: TopicModelingResult object
            
        Returns:
            Dictionary with statistics
        """
        topic_distribution = defaultdict(int)
        for topic_id in result.document_topics:
            if topic_id >= 0:  # Exclude noise
                topic_distribution[topic_id] += 1
        
        return {
            'num_topics': len(result.topics),
            'coherence_score': result.coherence_score,
            'topic_distribution': dict(topic_distribution),
            'num_documents': len(result.document_topics)
        }
