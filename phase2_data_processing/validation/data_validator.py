"""
Data Validation Module
Validates data schema, quality metrics, and integrity
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float


class DataValidator:
    """
    Validates review data for schema compliance and quality
    Ensures data integrity before processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data validator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.required_fields = config.get('required_fields', [
            'source', 'review_id', 'content'
        ])
        self.optional_fields = config.get('optional_fields', [
            'rating', 'author', 'timestamp', 'url', 'metadata'
        ])
        self.quality_threshold = config.get('quality_threshold', 0.7)
    
    def validate_review(self, review: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single review
        
        Args:
            review: Review dictionary
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        quality_score = 1.0
        
        # Check required fields
        for field in self.required_fields:
            if field not in review:
                errors.append(f"Missing required field: {field}")
                quality_score -= 0.2
            elif not review[field]:
                errors.append(f"Empty required field: {field}")
                quality_score -= 0.1
        
        # Check field types
        type_errors = self._validate_field_types(review)
        errors.extend(type_errors)
        quality_score -= len(type_errors) * 0.05
        
        # Check content quality
        content = review.get('content', '')
        if content:
            content_quality = self._validate_content(content)
            if content_quality < 0.8:
                warnings.append("Content quality below threshold")
                quality_score -= 0.1
        else:
            errors.append("Content is empty")
            quality_score -= 0.3
        
        # Check rating validity
        rating = review.get('rating')
        if rating is not None:
            if not isinstance(rating, (int, float)):
                errors.append(f"Invalid rating type: {type(rating)}")
                quality_score -= 0.1
            elif rating < 0 or rating > 5:
                warnings.append(f"Rating out of range: {rating}")
                quality_score -= 0.05
        
        # Check timestamp validity
        timestamp = review.get('timestamp')
        if timestamp:
            if not isinstance(timestamp, datetime):
                errors.append(f"Invalid timestamp type: {type(timestamp)}")
                quality_score -= 0.1
            elif timestamp > datetime.utcnow():
                warnings.append("Timestamp is in the future")
                quality_score -= 0.05
        
        # Check URL validity
        url = review.get('url')
        if url and not self._is_valid_url(url):
            warnings.append(f"Invalid URL format: {url}")
            quality_score -= 0.05
        
        # Check metadata structure
        metadata = review.get('metadata')
        if metadata and not isinstance(metadata, dict):
            errors.append("Metadata must be a dictionary")
            quality_score -= 0.1
        
        # Ensure quality score is within bounds
        quality_score = max(0.0, min(1.0, quality_score))
        
        is_valid = (
            len(errors) == 0 and
            quality_score >= self.quality_threshold
        )
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score
        )
    
    def _validate_field_types(self, review: Dict[str, Any]) -> List[str]:
        """Validate field types"""
        errors = []
        
        if 'source' in review and not isinstance(review['source'], str):
            errors.append("source must be a string")
        
        if 'review_id' in review and not isinstance(review['review_id'], str):
            errors.append("review_id must be a string")
        
        if 'content' in review and not isinstance(review['content'], str):
            errors.append("content must be a string")
        
        if 'author' in review and not isinstance(review['author'], str):
            errors.append("author must be a string")
        
        return errors
    
    def _validate_content(self, content: str) -> float:
        """
        Validate content quality
        
        Args:
            content: Content to validate
            
        Returns:
            Quality score between 0 and 1
        """
        score = 1.0
        
        # Check length
        if len(content) < 10:
            score -= 0.3
        elif len(content) < 20:
            score -= 0.1
        
        # Check for meaningful content
        if not re.search(r'[a-zA-Z]{3,}', content):
            score -= 0.4
        
        # Check for excessive repetition
        words = content.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                score -= 0.3
        
        return max(0.0, score)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return re.match(url_pattern, url) is not None
    
    def validate_batch(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary with validation results and statistics
        """
        results = []
        valid_reviews = []
        invalid_reviews = []
        
        for review in reviews:
            result = self.validate_review(review)
            results.append(result)
            
            if result.is_valid:
                valid_reviews.append(review)
            else:
                invalid_reviews.append({
                    **review,
                    'validation_result': {
                        'is_valid': result.is_valid,
                        'errors': result.errors,
                        'warnings': result.warnings,
                        'quality_score': result.quality_score
                    }
                })
        
        # Calculate statistics
        total = len(reviews)
        valid_count = len(valid_reviews)
        avg_quality = sum(r.quality_score for r in results) / total if total > 0 else 0
        
        # Common errors
        error_counts = {}
        for result in results:
            for error in result.errors:
                error_counts[error] = error_counts.get(error, 0) + 1
        
        # Common warnings
        warning_counts = {}
        for result in results:
            for warning in result.warnings:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        logger.info(
            f"Validation complete: {valid_count}/{total} valid, "
            f"avg quality: {avg_quality:.2f}"
        )
        
        return {
            'valid_reviews': valid_reviews,
            'invalid_reviews': invalid_reviews,
            'statistics': {
                'total': total,
                'valid': valid_count,
                'invalid': total - valid_count,
                'valid_rate': valid_count / total if total > 0 else 0,
                'average_quality_score': avg_quality,
                'error_counts': error_counts,
                'warning_counts': warning_counts
            }
        }
    
    def check_data_freshness(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check freshness of data based on timestamps
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary with freshness metrics
        """
        timestamps = []
        for review in reviews:
            timestamp = review.get('timestamp')
            if timestamp and isinstance(timestamp, datetime):
                timestamps.append(timestamp)
        
        if not timestamps:
            return {
                'has_timestamps': False,
                'message': 'No timestamps found'
            }
        
        now = datetime.utcnow()
        oldest = min(timestamps)
        newest = max(timestamps)
        avg_age = sum((now - ts).total_seconds() for ts in timestamps) / len(timestamps)
        
        return {
            'has_timestamps': True,
            'oldest_timestamp': oldest,
            'newest_timestamp': newest,
            'data_age_days': (now - oldest).days,
            'average_age_hours': avg_age / 3600,
            'time_span_days': (newest - oldest).days
        }
    
    def check_data_completeness(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check completeness of data fields
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary with completeness metrics
        """
        total = len(reviews)
        if total == 0:
            return {'total': 0}
        
        all_fields = set()
        for review in reviews:
            all_fields.update(review.keys())
        
        completeness = {}
        for field in all_fields:
            count = sum(1 for review in reviews if field in review and review[field])
            completeness[field] = {
                'count': count,
                'percentage': (count / total) * 100
            }
        
        return {
            'total_reviews': total,
            'total_fields': len(all_fields),
            'field_completeness': completeness
        }
