"""
Hypothesis Generation Module
Generates research hypotheses from insights and data
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Hypothesis:
    """Research hypothesis"""
    hypothesis_id: str
    statement: str
    target_segment: Optional[str]
    problem_statement: str
    validation_approach: str
    data_support_score: float
    strategic_alignment_score: float
    testability_score: float
    overall_score: float


@dataclass
class HypothesisGenerationResult:
    """Result of hypothesis generation"""
    hypotheses: List[Hypothesis]
    total_hypotheses: int
    high_priority_count: int


class HypothesisGenerator:
    """
    Generates research hypotheses from insights
    Creates testable hypotheses for product validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize hypothesis generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_support_score = config.get('min_support_score', 0.5)
        
        # Hypothesis templates
        self.hypothesis_templates = {
            'discovery_problem': {
                'template': "Users who struggle with {problem} are more likely to {behavior}",
                'validation': "A/B test comparing discovery features"
            },
            'segment_specific': {
                'template': "{segment} users experience {problem} more than other segments",
                'validation': "Segment-based analysis and interviews"
            },
            'feature_opportunity': {
                'template': "Improving {feature} would increase {metric} for {segment}",
                'validation': "Feature rollout and metric tracking"
            },
            'behavioral_pattern': {
                'template': "Users who exhibit {pattern} are less likely to {desired_behavior}",
                'validation': "Behavioral analysis and cohort study"
            }
        }
    
    def generate_hypotheses(
        self,
        pain_points: List[str],
        opportunities: List[str],
        segments: List[str],
        patterns: List[str]
    ) -> HypothesisGenerationResult:
        """
        Generate research hypotheses from insights
        
        Args:
            pain_points: List of pain point descriptions
            opportunities: List of opportunity descriptions
            segments: List of user segment names
            patterns: List of pattern descriptions
            
        Returns:
            HypothesisGenerationResult with generated hypotheses
        """
        logger.info("Generating research hypotheses from insights")
        
        hypotheses = []
        
        # Generate hypotheses from pain points
        for pain_point in pain_points[:5]:  # Top 5 pain points
            hypothesis = self._generate_from_pain_point(pain_point, segments)
            if hypothesis:
                hypotheses.append(hypothesis)
        
        # Generate hypotheses from opportunities
        for opportunity in opportunities[:5]:  # Top 5 opportunities
            hypothesis = self._generate_from_opportunity(opportunity, segments)
            if hypothesis:
                hypotheses.append(hypothesis)
        
        # Generate hypotheses from segments
        for segment in segments[:3]:  # Top 3 segments
            hypothesis = self._generate_from_segment(segment, pain_points)
            if hypothesis:
                hypotheses.append(hypothesis)
        
        # Generate hypotheses from patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            hypothesis = self._generate_from_pattern(pattern)
            if hypothesis:
                hypotheses.append(hypothesis)
        
        # Score hypotheses
        hypotheses = self._score_hypotheses(hypotheses)
        
        # Sort by overall score
        hypotheses.sort(key=lambda h: h.overall_score, reverse=True)
        
        # Count high priority hypotheses
        high_priority_count = sum(
            1 for h in hypotheses
            if h.overall_score >= 0.7
        )
        
        logger.info(
            f"Hypothesis generation complete: {len(hypotheses)} hypotheses, "
            f"{high_priority_count} high priority"
        )
        
        return HypothesisGenerationResult(
            hypotheses=hypotheses,
            total_hypotheses=len(hypotheses),
            high_priority_count=high_priority_count
        )
    
    def _generate_from_pain_point(
        self,
        pain_point: str,
        segments: List[str]
    ) -> Optional[Hypothesis]:
        """Generate hypothesis from pain point"""
        pain_point_lower = pain_point.lower()
        
        # Extract key problem
        if 'discover' in pain_point_lower:
            problem = "music discovery"
            behavior = "engage with new content"
        elif 'recommend' in pain_point_lower:
            problem = "recommendation quality"
            behavior = "trust recommendations"
        elif 'ui' in pain_point_lower or 'interface' in pain_point_lower:
            problem = "interface usability"
            behavior = "use the app effectively"
        else:
            problem = pain_point_lower
            behavior = "achieve their goals"
        
        # Create hypothesis statement
        statement = f"Users who struggle with {problem} are less likely to {behavior}"
        
        # Select target segment
        target_segment = segments[0] if segments else None
        
        return Hypothesis(
            hypothesis_id=f"hyp_pain_{hash(pain_point) % 1000}",
            statement=statement,
            target_segment=target_segment,
            problem_statement=pain_point,
            validation_approach="User interviews and A/B testing",
            data_support_score=0.7,
            strategic_alignment_score=0.8,
            testability_score=0.9,
            overall_score=0.0  # Will be calculated
        )
    
    def _generate_from_opportunity(
        self,
        opportunity: str,
        segments: List[str]
    ) -> Optional[Hypothesis]:
        """Generate hypothesis from opportunity"""
        opportunity_lower = opportunity.lower()
        
        # Extract key feature
        if 'discover' in opportunity_lower:
            feature = "discovery features"
            metric = "discovery rate"
        elif 'personal' in opportunity_lower:
            feature = "personalization"
            metric = "user satisfaction"
        elif 'context' in opportunity_lower or 'mood' in opportunity_lower:
            feature = "context-aware recommendations"
            metric = "engagement"
        else:
            feature = opportunity_lower
            metric = "user satisfaction"
        
        # Select target segment
        target_segment = segments[0] if segments else "all users"
        
        statement = f"Improving {feature} would increase {metric} for {target_segment}"
        
        return Hypothesis(
            hypothesis_id=f"hyp_opp_{hash(opportunity) % 1000}",
            statement=statement,
            target_segment=target_segment,
            problem_statement=opportunity,
            validation_approach="Feature rollout and metric tracking",
            data_support_score=0.6,
            strategic_alignment_score=0.9,
            testability_score=0.7,
            overall_score=0.0
        )
    
    def _generate_from_segment(
        self,
        segment: str,
        pain_points: List[str]
    ) -> Optional[Hypothesis]:
        """Generate hypothesis from user segment"""
        segment_lower = segment.lower()
        
        # Map segment to typical problem
        segment_problems = {
            'discovery_focused': 'limited variety in recommendations',
            'habitual_listener': 'resistance to new content',
            'mood_based': 'inaccurate mood detection',
            'activity_based': 'context mismatch',
            'genre_explorer': 'limited cross-genre discovery',
            'casual_listener': 'low engagement'
        }
        
        problem = segment_problems.get(segment, 'generic challenges')
        
        statement = f"{segment.replace('_', ' ').title()} users experience {problem} more than other segments"
        
        return Hypothesis(
            hypothesis_id=f"hyp_seg_{hash(segment) % 1000}",
            statement=statement,
            target_segment=segment,
            problem_statement=problem,
            validation_approach="Segment-based analysis and interviews",
            data_support_score=0.8,
            strategic_alignment_score=0.7,
            testability_score=0.8,
            overall_score=0.0
        )
    
    def _generate_from_pattern(self, pattern: str) -> Optional[Hypothesis]:
        """Generate hypothesis from behavioral pattern"""
        pattern_lower = pattern.lower()
        
        if 'habit' in pattern_lower or 'routine' in pattern_lower:
            statement = "Users with habitual listening patterns are less likely to discover new music"
            desired_behavior = "discover new content"
        elif 'mood' in pattern_lower:
            statement = "Users who select music based on mood are more sensitive to context-aware recommendations"
            desired_behavior = "engage with recommendations"
        else:
            statement = f"Users who exhibit {pattern} patterns show different discovery behaviors"
            desired_behavior = "achieve their listening goals"
        
        return Hypothesis(
            hypothesis_id=f"hyp_pat_{hash(pattern) % 1000}",
            statement=statement,
            target_segment=None,
            problem_statement=pattern,
            validation_approach="Behavioral analysis and cohort study",
            data_support_score=0.6,
            strategic_alignment_score=0.6,
            testability_score=0.8,
            overall_score=0.0
        )
    
    def _score_hypotheses(self, hypotheses: List[Hypothesis]) -> List[Hypothesis]:
        """Score hypotheses by multiple criteria"""
        for hypothesis in hypotheses:
            # Calculate overall score
            hypothesis.overall_score = (
                hypothesis.data_support_score * 0.3 +
                hypothesis.strategic_alignment_score * 0.4 +
                hypothesis.testability_score * 0.3
            )
        
        return hypotheses
    
    def prioritize_hypotheses(
        self,
        result: HypothesisGenerationResult
    ) -> List[Hypothesis]:
        """
        Prioritize hypotheses for validation
        
        Args:
            result: HypothesisGenerationResult object
            
        Returns:
            List of prioritized Hypothesis objects
        """
        # Filter by minimum support score
        valid_hypotheses = [
            h for h in result.hypotheses
            if h.data_support_score >= self.min_support_score
        ]
        
        # Sort by overall score
        valid_hypotheses.sort(key=lambda h: h.overall_score, reverse=True)
        
        return valid_hypotheses
    
    def get_statistics(self, result: HypothesisGenerationResult) -> Dict[str, Any]:
        """
        Get statistics from hypothesis generation result
        
        Args:
            result: HypothesisGenerationResult object
            
        Returns:
            Dictionary with statistics
        """
        target_segments = defaultdict(int)
        validation_approaches = defaultdict(int)
        
        for hypothesis in result.hypotheses:
            if hypothesis.target_segment:
                target_segments[hypothesis.target_segment] += 1
            validation_approaches[hypothesis.validation_approach] += 1
        
        avg_score = sum(
            h.overall_score for h in result.hypotheses
        ) / len(result.hypotheses) if result.hypotheses else 0
        
        return {
            'total_hypotheses': result.total_hypotheses,
            'high_priority_count': result.high_priority_count,
            'target_segment_distribution': dict(target_segments),
            'validation_approach_distribution': dict(validation_approaches),
            'average_overall_score': avg_score
        }
