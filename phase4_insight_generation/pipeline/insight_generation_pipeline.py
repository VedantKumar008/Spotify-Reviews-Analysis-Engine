"""
Insight Generation Pipeline Orchestrator
Coordinates all insight generation steps from summarization to hypothesis generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from summarization import Summarizer
from segmentation import UserSegmenter
from taxonomy import ThemeTaxonomy
from opportunity_mapping import OpportunityMapper
from hypothesis_generation import HypothesisGenerator

logger = logging.getLogger(__name__)


class InsightGenerationPipeline:
    """
    Main insight generation pipeline that coordinates all steps
    Performs summarization, segmentation, taxonomy, opportunity mapping, and hypothesis generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize insight generation pipeline
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.summarizer = Summarizer(config.get('summarization', {}))
        self.user_segmenter = UserSegmenter(config.get('segmentation', {}))
        self.theme_taxonomy = ThemeTaxonomy(config.get('taxonomy', {}))
        self.opportunity_mapper = OpportunityMapper(config.get('opportunity_mapping', {}))
        self.hypothesis_generator = HypothesisGenerator(config.get('hypothesis_generation', {}))
        
        # Pipeline statistics
        self.statistics = {
            'start_time': None,
            'end_time': None,
            'total_reviews': 0,
            'step_results': {}
        }
    
    def generate_insights(
        self,
        reviews: List[Dict[str, Any]],
        ml_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run complete insight generation pipeline on reviews
        
        Args:
            reviews: List of review dictionaries
            ml_results: Optional ML analysis results from Phase 3
            
        Returns:
            Dictionary with all insight generation results and statistics
        """
        self.statistics['start_time'] = datetime.utcnow()
        self.statistics['total_reviews'] = len(reviews)
        
        logger.info(f"Starting insight generation pipeline for {len(reviews)} reviews")
        
        # Step 1: Automated Summarization
        summary_results, summary_stats = self._summarization_step(reviews, ml_results)
        self.statistics['step_results']['summarization'] = summary_stats
        
        # Step 2: User Segmentation
        segmentation_results, segmentation_stats = self._segmentation_step(reviews)
        self.statistics['step_results']['segmentation'] = segmentation_stats
        
        # Step 3: Theme Taxonomy
        taxonomy_results, taxonomy_stats = self._taxonomy_step(reviews)
        self.statistics['step_results']['taxonomy'] = taxonomy_stats
        
        # Step 4: Opportunity Mapping
        opportunity_results, opportunity_stats = self._opportunity_mapping_step(
            reviews,
            ml_results
        )
        self.statistics['step_results']['opportunity_mapping'] = opportunity_stats
        
        # Step 5: Hypothesis Generation
        hypothesis_results, hypothesis_stats = self._hypothesis_generation_step(
            reviews,
            segmentation_results,
            opportunity_results
        )
        self.statistics['step_results']['hypothesis_generation'] = hypothesis_stats
        
        self.statistics['end_time'] = datetime.utcnow()
        self.statistics['duration'] = (
            self.statistics['end_time'] - self.statistics['start_time']
        ).total_seconds()
        
        logger.info(
            f"Insight generation pipeline completed in {self.statistics['duration']:.2f}s"
        )
        
        return {
            'summary_results': summary_results,
            'segmentation_results': segmentation_results,
            'taxonomy_results': taxonomy_results,
            'opportunity_results': opportunity_results,
            'hypothesis_results': hypothesis_results,
            'statistics': self.statistics
        }
    
    def _summarization_step(
        self,
        reviews: List[Dict[str, Any]],
        ml_results: Optional[Dict[str, Any]] = None
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Step 1: Automated Summarization"""
        logger.info("Step 1: Automated Summarization")
        
        # Extract texts
        texts = [review.get('content', '') for review in reviews]
        
        # Generate summaries
        summary = self.summarizer.summarize_extractive(texts)
        
        # Summarize insights from ML results if available
        insight_summaries = {}
        if ml_results:
            pain_points = []
            opportunities = []
            patterns = []
            
            if 'pattern_results' in ml_results:
                for pattern in ml_results['pattern_results'].complaints:
                    pain_points.append(pattern.pattern)
                for pattern in ml_results['pattern_results'].recommendation_patterns:
                    opportunities.append(pattern.pattern)
            
            insight_summaries = self.summarizer.summarize_insights(
                pain_points,
                opportunities,
                patterns
            )
        
        stats = {
            'summary_length': summary.length,
            'coverage_score': summary.coverage_score,
            'method': summary.method
        }
        
        logger.info(f"Summarization completed: {stats['summary_length']} sentences")
        
        return {
            'main_summary': summary.summary_text,
            'insight_summaries': insight_summaries
        }, stats
    
    def _segmentation_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 2: User Segmentation"""
        logger.info("Step 2: User Segmentation")
        
        result = self.user_segmenter.segment_users(reviews)
        stats = self.user_segmenter.get_segment_statistics(result)
        
        logger.info(f"Segmentation completed: {stats['total_segments']} segments")
        
        return result, stats
    
    def _taxonomy_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Step 3: Theme Taxonomy"""
        logger.info("Step 3: Theme Taxonomy")
        
        themes = self.theme_taxonomy.build_taxonomy(reviews)
        hierarchy = self.theme_taxonomy.get_theme_hierarchy()
        stats = self.theme_taxonomy.get_theme_statistics()
        
        logger.info(f"Taxonomy completed: {stats['total_themes']} themes")
        
        return {
            'themes': themes,
            'hierarchy': hierarchy
        }, stats
    
    def _opportunity_mapping_step(
        self,
        reviews: List[Dict[str, Any]],
        ml_results: Optional[Dict[str, Any]] = None
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 4: Opportunity Mapping"""
        logger.info("Step 4: Opportunity Mapping")
        
        # Extract pain points and opportunities from ML results
        pain_points = []
        opportunities = []
        patterns = []
        
        if ml_results and 'pattern_results' in ml_results:
            for pattern in ml_results['pattern_results'].complaints:
                pain_points.append(pattern.pattern)
            for pattern in ml_results['pattern_results'].recommendation_patterns:
                opportunities.append(pattern.pattern)
            for pattern in ml_results['pattern_results'].listening_patterns:
                patterns.append(pattern.pattern)
        
        # Also extract from reviews directly
        for review in reviews:
            content = review.get('content', '')
            if content:
                patterns.append(content[:100])
        
        result = self.opportunity_mapper.map_opportunities(
            pain_points,
            opportunities,
            patterns
        )
        stats = self.opportunity_mapper.get_statistics(result)
        
        logger.info(
            f"Opportunity mapping completed: {stats['total_opportunities']} opportunities"
        )
        
        return result, stats
    
    def _hypothesis_generation_step(
        self,
        reviews: List[Dict[str, Any]],
        segmentation_results: Any,
        opportunity_results: Any
    ) -> tuple[Any, Dict[str, Any]]:
        """Step 5: Hypothesis Generation"""
        logger.info("Step 5: Hypothesis Generation")
        
        # Extract data for hypothesis generation
        pain_points = []
        opportunities = []
        segments = []
        patterns = []
        
        # From opportunity results
        for opp in opportunity_results.opportunities:
            opportunities.append(opp.description)
            pain_points.append(opp.description)
        
        # From segmentation results
        for segment in segmentation_results.segments:
            segments.append(segment.segment_name)
        
        # From reviews
        for review in reviews:
            content = review.get('content', '')
            if content:
                patterns.append(content[:100])
        
        result = self.hypothesis_generator.generate_hypotheses(
            pain_points,
            opportunities,
            segments,
            patterns
        )
        stats = self.hypothesis_generator.get_statistics(result)
        
        logger.info(
            f"Hypothesis generation completed: {stats['total_hypotheses']} hypotheses"
        )
        
        return result, stats
    
    def get_insight_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive report of the insight generation
        
        Returns:
            Dictionary with insight report
        """
        return {
            'summary': {
                'total_reviews': self.statistics['total_reviews'],
                'duration': self.statistics.get('duration', 0),
                'steps_completed': len(self.statistics['step_results'])
            },
            'step_results': self.statistics['step_results']
        }
    
    def get_prioritized_insights(
        self,
        opportunity_results: Any,
        hypothesis_results: Any
    ) -> Dict[str, List]:
        """
        Get prioritized insights
        
        Args:
            opportunity_results: OpportunityMappingResult object
            hypothesis_results: HypothesisGenerationResult object
            
        Returns:
            Dictionary with prioritized insights
        """
        prioritized_hypotheses = self.hypothesis_generator.prioritize_hypotheses(
            hypothesis_results
        )
        
        high_priority_opportunities = [
            opp for opp in opportunity_results.opportunities
            if opp.priority_score >= 0.7
        ]
        
        return {
            'high_priority_opportunities': high_priority_opportunities,
            'prioritized_hypotheses': prioritized_hypotheses
        }
