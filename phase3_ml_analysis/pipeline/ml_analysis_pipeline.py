"""
AI/ML Analysis Pipeline Orchestrator
Coordinates all AI/ML analysis steps from sentiment to insight extraction
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sentiment import SentimentAnalyzer
from topic_modeling import TopicModeler
from pattern_recognition import PatternDetector
from behavior_analysis import BehaviorAnalyzer
from insight_extraction import InsightExtractor

logger = logging.getLogger(__name__)


class MLAnalysisPipeline:
    """
    Main AI/ML analysis pipeline that coordinates all analysis steps
    Performs sentiment analysis, topic modeling, pattern recognition, behavior analysis, and insight extraction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ML analysis pipeline
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer(config.get('sentiment_analysis', {}))
        self.topic_modeler = TopicModeler(config.get('topic_modeling', {}))
        self.pattern_detector = PatternDetector(config.get('pattern_recognition', {}))
        self.behavior_analyzer = BehaviorAnalyzer(config.get('behavior_analysis', {}))
        self.insight_extractor = InsightExtractor(config.get('insight_extraction', {}))
        
        # Pipeline statistics
        self.statistics = {
            'start_time': None,
            'end_time': None,
            'total_reviews': 0,
            'step_results': {}
        }
    
    def analyze(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run complete ML analysis pipeline on reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary with all analysis results and statistics
        """
        self.statistics['start_time'] = datetime.utcnow()
        self.statistics['total_reviews'] = len(reviews)
        
        logger.info(f"Starting ML analysis pipeline for {len(reviews)} reviews")
        
        # Extract texts for analysis
        texts = [review.get('content', '') for review in reviews]
        
        # Step 1: Sentiment Analysis
        sentiment_results, sentiment_stats = self._sentiment_analysis_step(texts)
        self.statistics['step_results']['sentiment_analysis'] = sentiment_stats
        
        # Step 2: Topic Modeling
        topic_results, topic_stats = self._topic_modeling_step(texts)
        self.statistics['step_results']['topic_modeling'] = topic_stats
        
        # Step 3: Pattern Recognition
        pattern_results, pattern_stats = self._pattern_recognition_step(reviews)
        self.statistics['step_results']['pattern_recognition'] = pattern_stats
        
        # Step 4: Behavior Analysis
        behavior_results, behavior_stats = self._behavior_analysis_step(reviews)
        self.statistics['step_results']['behavior_analysis'] = behavior_stats
        
        # Step 5: Insight Extraction
        insight_results, insight_stats = self._insight_extraction_step(
            reviews,
            sentiment_results,
            pattern_results
        )
        self.statistics['step_results']['insight_extraction'] = insight_stats
        
        self.statistics['end_time'] = datetime.utcnow()
        self.statistics['duration'] = (
            self.statistics['end_time'] - self.statistics['start_time']
        ).total_seconds()
        
        logger.info(
            f"ML analysis pipeline completed in {self.statistics['duration']:.2f}s"
        )
        
        return {
            'sentiment_results': sentiment_results,
            'topic_results': topic_results,
            'pattern_results': pattern_results,
            'behavior_results': behavior_results,
            'insight_results': insight_results,
            'statistics': self.statistics
        }
    
    def _sentiment_analysis_step(
        self,
        texts: List[str]
    ) -> tuple[List, Dict[str, Any]]:
        """Step 1: Sentiment Analysis"""
        logger.info("Step 1: Sentiment Analysis")
        
        results = self.sentiment_analyzer.analyze_batch(texts)
        stats = self.sentiment_analyzer.get_statistics(results)
        
        logger.info(f"Sentiment analysis completed: {stats['total_analyzed']} reviews analyzed")
        
        return results, stats
    
    def _topic_modeling_step(
        self,
        texts: List[str]
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 2: Topic Modeling"""
        logger.info("Step 2: Topic Modeling")
        
        result = self.topic_modeler.fit(texts)
        stats = self.topic_modeler.get_statistics(result)
        
        logger.info(f"Topic modeling completed: {stats['num_topics']} topics found")
        
        return result, stats
    
    def _pattern_recognition_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 3: Pattern Recognition"""
        logger.info("Step 3: Pattern Recognition")
        
        result = self.pattern_detector.detect_patterns(reviews)
        stats = self.pattern_detector.get_statistics(result)
        
        logger.info(
            f"Pattern recognition completed: {stats['total_patterns']} patterns detected"
        )
        
        return result, stats
    
    def _behavior_analysis_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 4: Behavior Analysis"""
        logger.info("Step 4: Behavior Analysis")
        
        result = self.behavior_analyzer.analyze(reviews)
        stats = self.behavior_analyzer.get_statistics(result)
        
        logger.info(
            f"Behavior analysis completed: {stats['summary']['goals_extracted']} goals, "
            f"{stats['summary']['patterns_detected']} patterns"
        )
        
        return result, stats
    
    def _insight_extraction_step(
        self,
        reviews: List[Dict[str, Any]],
        sentiment_results: Optional[List] = None,
        pattern_results: Optional[Any] = None
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 5: Insight Extraction"""
        logger.info("Step 5: Insight Extraction")
        
        result = self.insight_extractor.extract_insights(
            reviews,
            sentiment_results,
            pattern_results
        )
        stats = self.insight_extractor.get_statistics(result)
        
        logger.info(
            f"Insight extraction completed: {stats['summary']['pain_points_found']} pain points, "
            f"{stats['summary']['opportunities_found']} opportunities"
        )
        
        return result, stats
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive report of the analysis
        
        Returns:
            Dictionary with analysis report
        """
        return {
            'summary': {
                'total_reviews': self.statistics['total_reviews'],
                'duration': self.statistics.get('duration', 0),
                'steps_completed': len(self.statistics['step_results'])
            },
            'step_results': self.statistics['step_results']
        }
    
    def get_prioritized_insights(self, insight_results: Any) -> Dict[str, List]:
        """
        Get prioritized insights from insight extraction results
        
        Args:
            insight_results: InsightExtractionResult object
            
        Returns:
            Dictionary with prioritized insights
        """
        return self.insight_extractor.prioritize_insights(insight_results)
