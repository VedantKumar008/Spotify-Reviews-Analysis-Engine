"""
Data Processing Pipeline Orchestrator
Coordinates all data processing steps from cleaning to validation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from cleaning.spam_detector import SpamDetector
from cleaning.deduplicator import Deduplicator
from cleaning.quality_filter import QualityFilter
from normalization.text_normalizer import TextNormalizer
from normalization.entity_recognizer import EntityRecognizer
from enrichment.metadata_enricher import MetadataEnricher
from validation.data_validator import DataValidator

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """
    Main processing pipeline that coordinates all data processing steps
    Performs cleaning, normalization, enrichment, and validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize processing pipeline
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize components
        self.spam_detector = SpamDetector(config.get('spam_detection', {}))
        self.deduplicator = Deduplicator(config.get('deduplication', {}))
        self.quality_filter = QualityFilter(config.get('quality_filter', {}))
        self.text_normalizer = TextNormalizer(config.get('text_normalization', {}))
        self.entity_recognizer = EntityRecognizer(config.get('entity_recognition', {}))
        self.metadata_enricher = MetadataEnricher(config.get('metadata_enrichment', {}))
        self.data_validator = DataValidator(config.get('data_validation', {}))
        
        # Pipeline statistics
        self.statistics = {
            'start_time': None,
            'end_time': None,
            'original_count': 0,
            'spam_removed': 0,
            'duplicates_removed': 0,
            'quality_filtered': 0,
            'final_count': 0,
            'step_results': {}
        }
    
    def process(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process reviews through the complete pipeline
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary with processed reviews and statistics
        """
        self.statistics['start_time'] = datetime.utcnow()
        self.statistics['original_count'] = len(reviews)
        
        logger.info(f"Starting processing pipeline for {len(reviews)} reviews")
        
        processed_reviews = reviews.copy()
        
        # Step 1: Spam Detection
        processed_reviews, spam_result = self._spam_detection_step(processed_reviews)
        self.statistics['spam_removed'] = spam_result['removed_count']
        self.statistics['step_results']['spam_detection'] = spam_result
        
        # Step 2: Deduplication
        processed_reviews, dedup_result = self._deduplication_step(processed_reviews)
        self.statistics['duplicates_removed'] = dedup_result['removed_count']
        self.statistics['step_results']['deduplication'] = dedup_result
        
        # Step 3: Quality Filtering
        processed_reviews, quality_result = self._quality_filtering_step(processed_reviews)
        self.statistics['quality_filtered'] = quality_result['removed_count']
        self.statistics['step_results']['quality_filtering'] = quality_result
        
        # Step 4: Text Normalization
        processed_reviews, norm_result = self._normalization_step(processed_reviews)
        self.statistics['step_results']['normalization'] = norm_result
        
        # Step 5: Entity Recognition
        processed_reviews, entity_result = self._entity_recognition_step(processed_reviews)
        self.statistics['step_results']['entity_recognition'] = entity_result
        
        # Step 6: Metadata Enrichment
        processed_reviews, enrichment_result = self._enrichment_step(processed_reviews)
        self.statistics['step_results']['metadata_enrichment'] = enrichment_result
        
        # Step 7: Data Validation
        processed_reviews, validation_result = self._validation_step(processed_reviews)
        self.statistics['step_results']['validation'] = validation_result
        
        self.statistics['final_count'] = len(processed_reviews)
        self.statistics['end_time'] = datetime.utcnow()
        self.statistics['duration'] = (
            self.statistics['end_time'] - self.statistics['start_time']
        ).total_seconds()
        
        logger.info(
            f"Pipeline completed: {self.statistics['final_count']}/{self.statistics['original_count']} "
            f"reviews processed in {self.statistics['duration']:.2f}s"
        )
        
        return {
            'processed_reviews': processed_reviews,
            'statistics': self.statistics
        }
    
    def _spam_detection_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 1: Detect and remove spam"""
        logger.info("Step 1: Spam Detection")
        
        non_spam_reviews = []
        spam_count = 0
        
        for review in reviews:
            content = review.get('content', '')
            result = self.spam_detector.detect_spam(content)
            
            if not result.is_spam:
                non_spam_reviews.append(review)
            else:
                spam_count += 1
                logger.debug(f"Removed spam: {result.reasons}")
        
        logger.info(f"Spam detection: removed {spam_count} spam reviews")
        
        return non_spam_reviews, {
            'removed_count': spam_count,
            'remaining_count': len(non_spam_reviews)
        }
    
    def _deduplication_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 2: Remove duplicates"""
        logger.info("Step 2: Deduplication")
        
        deduplicated, result = self.deduplicator.deduplicate(reviews)
        
        logger.info(
            f"Deduplication: removed {result.duplicate_count} duplicates, "
            f"{result.unique_count} unique reviews"
        )
        
        return deduplicated, {
            'removed_count': result.duplicate_count,
            'remaining_count': result.unique_count,
            'duplicate_pairs': len(result.duplicate_pairs),
            'near_duplicate_pairs': len(result.near_duplicate_pairs)
        }
    
    def _quality_filtering_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 3: Filter by quality"""
        logger.info("Step 3: Quality Filtering")
        
        passed, failed = self.quality_filter.filter_batch(reviews)
        
        logger.info(
            f"Quality filtering: {len(passed)} passed, {len(failed)} failed"
        )
        
        return passed, {
            'removed_count': len(failed),
            'remaining_count': len(passed),
            'failed_reviews': failed
        }
    
    def _normalization_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 4: Normalize text"""
        logger.info("Step 4: Text Normalization")
        
        normalized_reviews = []
        emoji_count = 0
        
        for review in reviews:
            content = review.get('content', '')
            normalized = self.text_normalizer.normalize(content)
            
            # Add normalized content to review
            review['normalized_content'] = normalized.normalized
            review['tokens'] = normalized.tokens
            review['lemmas'] = normalized.lemmas
            review['emoji_count'] = normalized.emoji_count
            review['emoji_descriptions'] = normalized.emoji_descriptions
            
            normalized_reviews.append(review)
            emoji_count += normalized.emoji_count
        
        logger.info(
            f"Text normalization: processed {len(normalized_reviews)} reviews, "
            f"{emoji_count} emojis found"
        )
        
        return normalized_reviews, {
            'processed_count': len(normalized_reviews),
            'total_emojis': emoji_count
        }
    
    def _entity_recognition_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 5: Extract entities"""
        logger.info("Step 5: Entity Recognition")
        
        enriched_reviews = []
        total_entities = 0
        total_features = 0
        total_genres = 0
        
        for review in reviews:
            content = review.get('content', '')
            entities = self.entity_recognizer.extract_entities(content)
            features = self.entity_recognizer.extract_spotify_features(content)
            genres = self.entity_recognizer.extract_genres(content)
            artists = self.entity_recognizer.extract_artists(content)
            moods = self.entity_recognizer.extract_moods(content)
            
            # Add extracted entities to review
            review['entities'] = [
                {'text': e.text, 'label': e.label}
                for e in entities
            ]
            review['spotify_features'] = [
                {'feature_name': f.feature_name, 'feature_type': f.feature_type}
                for f in features
            ]
            review['genres'] = genres
            review['artists'] = artists
            review['moods'] = moods
            
            enriched_reviews.append(review)
            
            total_entities += len(entities)
            total_features += len(features)
            total_genres += len(genres)
        
        logger.info(
            f"Entity recognition: extracted {total_entities} entities, "
            f"{total_features} Spotify features, {total_genres} genres"
        )
        
        return enriched_reviews, {
            'processed_count': len(enriched_reviews),
            'total_entities': total_entities,
            'total_spotify_features': total_features,
            'total_genres': total_genres
        }
    
    def _enrichment_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 6: Enrich with metadata"""
        logger.info("Step 6: Metadata Enrichment")
        
        enriched_reviews = self.metadata_enricher.enrich_batch(reviews)
        
        logger.info(f"Metadata enrichment: processed {len(enriched_reviews)} reviews")
        
        return enriched_reviews, {
            'processed_count': len(enriched_reviews),
            'user_profiles': len(self.metadata_enricher.get_user_profiles())
        }
    
    def _validation_step(
        self,
        reviews: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Step 7: Validate data"""
        logger.info("Step 7: Data Validation")
        
        validation_result = self.data_validator.validate_batch(reviews)
        
        valid_reviews = validation_result['valid_reviews']
        invalid_reviews = validation_result['invalid_reviews']
        
        logger.info(
            f"Data validation: {len(valid_reviews)} valid, {len(invalid_reviews)} invalid"
        )
        
        return valid_reviews, {
            'valid_count': len(valid_reviews),
            'invalid_count': len(invalid_reviews),
            'statistics': validation_result['statistics']
        }
    
    def get_pipeline_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive report of the pipeline execution
        
        Returns:
            Dictionary with pipeline report
        """
        return {
            'summary': {
                'original_count': self.statistics['original_count'],
                'final_count': self.statistics['final_count'],
                'total_removed': self.statistics['original_count'] - self.statistics['final_count'],
                'removal_rate': (
                    (self.statistics['original_count'] - self.statistics['final_count']) /
                    self.statistics['original_count']
                    if self.statistics['original_count'] > 0 else 0
                ),
                'duration': self.statistics.get('duration', 0)
            },
            'removal_breakdown': {
                'spam': self.statistics['spam_removed'],
                'duplicates': self.statistics['duplicates_removed'],
                'quality': self.statistics['quality_filtered']
            },
            'step_results': self.statistics['step_results']
        }
