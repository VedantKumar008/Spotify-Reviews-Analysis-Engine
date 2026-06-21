"""
Insight Extraction Module
Extracts pain points, opportunities, and actionable insights from analyzed data
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)


@dataclass
class PainPoint:
    """Extracted pain point"""
    category: str
    description: str
    severity: float
    frequency: int
    examples: List[str]


@dataclass
class Opportunity:
    """Extracted opportunity"""
    category: str
    description: str
    impact_score: float
    feasibility: float
    examples: List[str]


@dataclass
class InsightExtractionResult:
    """Result of insight extraction"""
    pain_points: List[PainPoint]
    opportunities: List[Opportunity]
    hypotheses: List[str]
    summary: Dict[str, Any]


class InsightExtractor:
    """
    Extracts actionable insights from analyzed data
    Identifies pain points, opportunities, and research hypotheses
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize insight extractor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_frequency = config.get('min_frequency', 5)
        self.severity_threshold = config.get('severity_threshold', 0.5)
        
        # Pain point categories
        self.pain_point_categories = {
            'discovery_difficulty': [
                r'hard to find', r'difficult to discover', r'can.*t find new',
                r'discovery.*bad', r'not.*discover', r'browse.*difficult'
            ],
            'repetitive_content': [
                r'repetitive', r'same songs', r'always the same',
                r'looping', r'over and over', r'boring'
            ],
            'poor_recommendations': [
                r'bad recommendations', r'poor suggestions', r'wrong recommendations',
                r'algorithm.*bad', r'recommend.*not.*work'
            ],
            'limited_variety': [
                r'limited variety', r'not enough variety', r'lack of variety',
                r'same artists', r'same genre'
            ],
            'ui_issues': [
                r'crash', r'bug', r'slow', r'lag', r'freeze',
                r'interface.*bad', r'design.*poor'
            ]
        }
        
        # Opportunity categories
        self.opportunity_categories = {
            'improve_discovery': [
                r'better discovery', r'improve.*find', r'better.*search',
                r'want.*discover', r'need.*explore'
            ],
            'personalization': [
                r'personalize', r'more.*personal', r'better.*for me',
                r'my.*taste', r'custom.*for me'
            ],
            'context_aware': [
                r'mood', r'situation', r'activity', r'time.*day',
                r'context', r'when.*listening'
            ],
            'social_features': [
                r'social', r'friends', r'share', r'collaborative',
                r'community', r'together'
            ],
            'content_variety': [
                r'more variety', r'different', r'new.*artists',
                r'explore.*genres', r'diverse'
            ]
        }
    
    def extract_insights(
        self,
        reviews: List[Dict[str, Any]],
        sentiment_results: Optional[List] = None,
        pattern_results: Optional[Any] = None
    ) -> InsightExtractionResult:
        """
        Extract insights from analyzed data
        
        Args:
            reviews: List of review dictionaries
            sentiment_results: Optional sentiment analysis results
            pattern_results: Optional pattern recognition results
            
        Returns:
            InsightExtractionResult with extracted insights
        """
        logger.info(f"Extracting insights from {len(reviews)} reviews")
        
        # Extract texts
        texts = [review.get('content', '') for review in reviews]
        
        # Extract pain points
        pain_points = self._extract_pain_points(texts, reviews)
        
        # Extract opportunities
        opportunities = self._extract_opportunities(texts, reviews)
        
        # Generate hypotheses
        hypotheses = self._generate_hypotheses(pain_points, opportunities)
        
        # Generate summary
        summary = {
            'total_reviews': len(reviews),
            'pain_points_found': len(pain_points),
            'opportunities_found': len(opportunities),
            'hypotheses_generated': len(hypotheses)
        }
        
        logger.info(
            f"Insight extraction complete: {len(pain_points)} pain points, "
            f"{len(opportunities)} opportunities, {len(hypotheses)} hypotheses"
        )
        
        return InsightExtractionResult(
            pain_points=pain_points,
            opportunities=opportunities,
            hypotheses=hypotheses,
            summary=summary
        )
    
    def _extract_pain_points(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[PainPoint]:
        """Extract pain points from texts"""
        pain_points = []
        
        for category, patterns in self.pain_point_categories.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        matches.append(text)
                        break
            
            if len(matches) >= self.min_frequency:
                # Calculate severity based on frequency and sentiment
                frequency = len(matches)
                severity = min(frequency / len(texts), 1.0)
                
                if severity >= self.severity_threshold:
                    pain_point = PainPoint(
                        category=category,
                        description=self._generate_pain_point_description(category),
                        severity=severity,
                        frequency=frequency,
                        examples=matches[:3]
                    )
                    pain_points.append(pain_point)
        
        # Sort by severity
        pain_points.sort(key=lambda x: x.severity, reverse=True)
        
        return pain_points
    
    def _extract_opportunities(
        self,
        texts: List[str],
        reviews: List[Dict[str, Any]]
    ) -> List[Opportunity]:
        """Extract opportunities from texts"""
        opportunities = []
        
        for category, patterns in self.opportunity_categories.items():
            matches = []
            for i, text in enumerate(texts):
                text_lower = text.lower()
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        matches.append(text)
                        break
            
            if len(matches) >= self.min_frequency:
                # Calculate impact and feasibility
                frequency = len(matches)
                impact_score = min(frequency / len(texts), 1.0)
                feasibility = 0.7  # Default feasibility
                
                opportunity = Opportunity(
                    category=category,
                    description=self._generate_opportunity_description(category),
                    impact_score=impact_score,
                    feasibility=feasibility,
                    examples=matches[:3]
                )
                opportunities.append(opportunity)
        
        # Sort by impact score
        opportunities.sort(key=lambda x: x.impact_score, reverse=True)
        
        return opportunities
    
    def _generate_hypotheses(
        self,
        pain_points: List[PainPoint],
        opportunities: List[Opportunity]
    ) -> List[str]:
        """Generate research hypotheses"""
        hypotheses = []
        
        # Generate hypotheses from pain points
        for pain_point in pain_points[:3]:  # Top 3 pain points
            hypothesis = f"Users struggle with {pain_point.category} which negatively impacts their music discovery experience"
            hypotheses.append(hypothesis)
        
        # Generate hypotheses from opportunities
        for opportunity in opportunities[:3]:  # Top 3 opportunities
            hypothesis = f"Improving {opportunity.category} would significantly enhance user satisfaction and engagement"
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _generate_pain_point_description(self, category: str) -> str:
        """Generate human-readable pain point description"""
        descriptions = {
            'discovery_difficulty': 'Users find it difficult to discover new music',
            'repetitive_content': 'Users experience repetitive content across recommendations',
            'poor_recommendations': 'Recommendation algorithm provides poor suggestions',
            'limited_variety': 'Limited variety in recommended content',
            'ui_issues': 'User interface issues negatively impact experience'
        }
        return descriptions.get(category, category)
    
    def _generate_opportunity_description(self, category: str) -> str:
        """Generate human-readable opportunity description"""
        descriptions = {
            'improve_discovery': 'Opportunity to improve music discovery features',
            'personalization': 'Opportunity to enhance personalization',
            'context_aware': 'Opportunity to implement context-aware recommendations',
            'social_features': 'Opportunity to add social features',
            'content_variety': 'Opportunity to increase content variety'
        }
        return descriptions.get(category, category)
    
    def prioritize_insights(
        self,
        result: InsightExtractionResult
    ) -> Dict[str, List]:
        """
        Prioritize insights by impact and severity
        
        Args:
            result: InsightExtractionResult object
            
        Returns:
            Dictionary with prioritized insights
        """
        # Prioritize pain points by severity
        high_severity_pain_points = [
            pp for pp in result.pain_points
            if pp.severity >= 0.7
        ]
        
        # Prioritize opportunities by impact
        high_impact_opportunities = [
            opp for opp in result.opportunities
            if opp.impact_score >= 0.7
        ]
        
        return {
            'high_priority_pain_points': high_severity_pain_points,
            'high_priority_opportunities': high_impact_opportunities,
            'top_hypotheses': result.hypotheses[:5]
        }
    
    def get_statistics(self, result: InsightExtractionResult) -> Dict[str, Any]:
        """
        Get statistics from insight extraction result
        
        Args:
            result: InsightExtractionResult object
            
        Returns:
            Dictionary with statistics
        """
        pain_point_categories = defaultdict(int)
        for pp in result.pain_points:
            pain_point_categories[pp.category] += 1
        
        opportunity_categories = defaultdict(int)
        for opp in result.opportunities:
            opportunity_categories[opp.category] += 1
        
        avg_severity = sum(pp.severity for pp in result.pain_points) / len(result.pain_points) if result.pain_points else 0
        avg_impact = sum(opp.impact_score for opp in result.opportunities) / len(result.opportunities) if result.opportunities else 0
        
        return {
            'summary': result.summary,
            'pain_point_categories': dict(pain_point_categories),
            'opportunity_categories': dict(opportunity_categories),
            'average_severity': avg_severity,
            'average_impact': avg_impact
        }
