"""
Opportunity Mapping Module
Maps unmet needs and product opportunities
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Opportunity:
    """Product opportunity"""
    opportunity_id: str
    category: str
    description: str
    need_type: str  # functional, emotional, social
    impact_score: float
    feasibility_score: float
    priority_score: float
    evidence: List[str]


@dataclass
class OpportunityMappingResult:
    """Result of opportunity mapping"""
    opportunities: List[Opportunity]
    total_opportunities: int
    high_priority_count: int


class OpportunityMapper:
    """
    Maps unmet needs to product opportunities
    Categorizes opportunities and scores them by impact and feasibility
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize opportunity mapper
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.impact_threshold = config.get('impact_threshold', 0.6)
        self.feasibility_threshold = config.get('feasibility_threshold', 0.5)
        
        # Opportunity categories
        self.opportunity_categories = {
            'improve_discovery': {
                'description': 'Enhance music discovery capabilities',
                'need_type': 'functional'
            },
            'personalization_enhancement': {
                'description': 'Improve recommendation personalization',
                'need_type': 'functional'
            },
            'context_awareness': {
                'description': 'Add context-aware recommendations',
                'need_type': 'functional'
            },
            'social_features': {
                'description': 'Add or improve social features',
                'need_type': 'social'
            },
            'ui_improvements': {
                'description': 'Improve user interface and experience',
                'need_type': 'functional'
            },
            'content_variety': {
                'description': 'Increase content variety and diversity',
                'need_type': 'functional'
            },
            'emotional_connection': {
                'description': 'Create deeper emotional connections with music',
                'need_type': 'emotional'
            },
            'reduction_friction': {
                'description': 'Reduce friction in music discovery',
                'need_type': 'functional'
            }
        }
    
    def map_opportunities(
        self,
        pain_points: List[str],
        user_goals: List[str],
        patterns: List[str]
    ) -> OpportunityMappingResult:
        """
        Map unmet needs to product opportunities
        
        Args:
            pain_points: List of pain point descriptions
            user_goals: List of user goal descriptions
            patterns: List of pattern descriptions
            
        Returns:
            OpportunityMappingResult with mapped opportunities
        """
        logger.info("Mapping opportunities from unmet needs")
        
        opportunities = []
        
        # Analyze pain points for opportunities
        for pain_point in pain_points:
            opportunity = self._analyze_pain_point(pain_point)
            if opportunity:
                opportunities.append(opportunity)
        
        # Analyze user goals for opportunities
        for goal in user_goals:
            opportunity = self._analyze_user_goal(goal)
            if opportunity:
                opportunities.append(opportunity)
        
        # Analyze patterns for opportunities
        for pattern in patterns:
            opportunity = self._analyze_pattern(pattern)
            if opportunity:
                opportunities.append(opportunity)
        
        # Calculate priority scores
        for opportunity in opportunities:
            opportunity.priority_score = (
                opportunity.impact_score * 0.6 +
                opportunity.feasibility_score * 0.4
            )
        
        # Sort by priority
        opportunities.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Count high priority opportunities
        high_priority_count = sum(
            1 for opp in opportunities
            if opp.priority_score >= 0.7
        )
        
        logger.info(
            f"Opportunity mapping complete: {len(opportunities)} opportunities, "
            f"{high_priority_count} high priority"
        )
        
        return OpportunityMappingResult(
            opportunities=opportunities,
            total_opportunities=len(opportunities),
            high_priority_count=high_priority_count
        )
    
    def _analyze_pain_point(self, pain_point: str) -> Optional[Opportunity]:
        """Analyze a pain point to extract opportunity"""
        pain_point_lower = pain_point.lower()
        
        # Map pain points to opportunities
        if 'discover' in pain_point_lower or 'find' in pain_point_lower:
            return Opportunity(
                opportunity_id=f"opp_discovery_{hash(pain_point) % 1000}",
                category='improve_discovery',
                description=f"Address: {pain_point}",
                need_type='functional',
                impact_score=0.8,
                feasibility_score=0.7,
                priority_score=0.0,  # Will be calculated
                evidence=[pain_point]
            )
        
        elif 'personal' in pain_point_lower or 'recommend' in pain_point_lower:
            return Opportunity(
                opportunity_id=f"opp_personal_{hash(pain_point) % 1000}",
                category='personalization_enhancement',
                description=f"Address: {pain_point}",
                need_type='functional',
                impact_score=0.8,
                feasibility_score=0.6,
                priority_score=0.0,
                evidence=[pain_point]
            )
        
        elif 'ui' in pain_point_lower or 'interface' in pain_point_lower or 'crash' in pain_point_lower:
            return Opportunity(
                opportunity_id=f"opp_ui_{hash(pain_point) % 1000}",
                category='ui_improvements',
                description=f"Address: {pain_point}",
                need_type='functional',
                impact_score=0.7,
                feasibility_score=0.8,
                priority_score=0.0,
                evidence=[pain_point]
            )
        
        return None
    
    def _analyze_user_goal(self, goal: str) -> Optional[Opportunity]:
        """Analyze a user goal to extract opportunity"""
        goal_lower = goal.lower()
        
        if 'mood' in goal_lower or 'feeling' in goal_lower:
            return Opportunity(
                opportunity_id=f"opp_mood_{hash(goal) % 1000}",
                category='context_awareness',
                description=f"Support: {goal}",
                need_type='emotional',
                impact_score=0.7,
                feasibility_score=0.5,
                priority_score=0.0,
                evidence=[goal]
            )
        
        elif 'social' in goal_lower or 'share' in goal_lower or 'friend' in goal_lower:
            return Opportunity(
                opportunity_id=f"opp_social_{hash(goal) % 1000}",
                category='social_features',
                description=f"Support: {goal}",
                need_type='social',
                impact_score=0.6,
                feasibility_score=0.6,
                priority_score=0.0,
                evidence=[goal]
            )
        
        elif 'variety' in goal_lower or 'different' in goal_lower:
            return Opportunity(
                opportunity_id=f"opp_variety_{hash(goal) % 1000}",
                category='content_variety',
                description=f"Support: {goal}",
                need_type='functional',
                impact_score=0.7,
                feasibility_score=0.7,
                priority_score=0.0,
                evidence=[goal]
            )
        
        return None
    
    def _analyze_pattern(self, pattern: str) -> Optional[Opportunity]:
        """Analyze a pattern to extract opportunity"""
        pattern_lower = pattern.lower()
        
        if 'habit' in pattern_lower or 'routine' in pattern_lower:
            return Opportunity(
                opportunity_id=f"opp_habit_{hash(pattern) % 1000}",
                category='reduction_friction',
                description=f"Address: {pattern}",
                need_type='functional',
                impact_score=0.6,
                feasibility_score=0.8,
                priority_score=0.0,
                evidence=[pattern]
            )
        
        return None
    
    def categorize_needs(self, reviews: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Categorize unmet needs by type
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary mapping need type to list of needs
        """
        needs_by_type = defaultdict(list)
        
        for review in reviews:
            content = review.get('content', '').lower()
            
            # Functional needs
            if any(word in content for word in ['find', 'discover', 'search', 'recommend']):
                needs_by_type['functional'].append(content[:100])
            
            # Emotional needs
            elif any(word in content for word in ['mood', 'feeling', 'emotional', 'happy', 'sad']):
                needs_by_type['emotional'].append(content[:100])
            
            # Social needs
            elif any(word in content for word in ['social', 'share', 'friend', 'together']):
                needs_by_type['social'].append(content[:100])
        
        return dict(needs_by_type)
    
    def score_opportunities(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """
        Score opportunities by impact and feasibility
        
        Args:
            opportunities: List of Opportunity objects
            
        Returns:
            List of scored Opportunity objects
        """
        for opportunity in opportunities:
            # Impact score based on category
            category_impact = {
                'improve_discovery': 0.9,
                'personalization_enhancement': 0.85,
                'context_awareness': 0.8,
                'social_features': 0.6,
                'ui_improvements': 0.7,
                'content_variety': 0.75,
                'emotional_connection': 0.7,
                'reduction_friction': 0.8
            }
            
            opportunity.impact_score = category_impact.get(
                opportunity.category,
                0.5
            )
            
            # Feasibility score based on complexity
            category_feasibility = {
                'improve_discovery': 0.6,
                'personalization_enhancement': 0.5,
                'context_awareness': 0.4,
                'social_features': 0.7,
                'ui_improvements': 0.8,
                'content_variety': 0.7,
                'emotional_connection': 0.5,
                'reduction_friction': 0.7
            }
            
            opportunity.feasibility_score = category_feasibility.get(
                opportunity.category,
                0.5
            )
            
            # Calculate priority
            opportunity.priority_score = (
                opportunity.impact_score * 0.6 +
                opportunity.feasibility_score * 0.4
            )
        
        return opportunities
    
    def get_statistics(self, result: OpportunityMappingResult) -> Dict[str, Any]:
        """
        Get statistics from opportunity mapping result
        
        Args:
            result: OpportunityMappingResult object
            
        Returns:
            Dictionary with statistics
        """
        category_counts = defaultdict(int)
        need_type_counts = defaultdict(int)
        
        for opportunity in result.opportunities:
            category_counts[opportunity.category] += 1
            need_type_counts[opportunity.need_type] += 1
        
        avg_priority = sum(
            opp.priority_score for opp in result.opportunities
        ) / len(result.opportunities) if result.opportunities else 0
        
        return {
            'total_opportunities': result.total_opportunities,
            'high_priority_count': result.high_priority_count,
            'category_distribution': dict(category_counts),
            'need_type_distribution': dict(need_type_counts),
            'average_priority_score': avg_priority
        }
