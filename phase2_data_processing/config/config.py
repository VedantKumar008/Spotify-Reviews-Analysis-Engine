"""
Configuration Management
Handles configuration loading and validation for Phase 2
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SpamDetectionConfig(BaseModel):
    """Spam detection configuration"""
    threshold: float = Field(default=0.7)
    num_permutations: int = Field(default=128)


class DeduplicationConfig(BaseModel):
    """Deduplication configuration"""
    near_duplicate_threshold: float = Field(default=0.8)
    num_permutations: int = Field(default=128)
    lsh_threshold: float = Field(default=0.7)


class QualityFilterConfig(BaseModel):
    """Quality filter configuration"""
    min_length: int = Field(default=20)
    max_length: int = Field(default=10000)
    min_words: int = Field(default=3)
    language_threshold: float = Field(default=0.7)
    relevance_threshold: float = Field(default=0.5)


class TextNormalizationConfig(BaseModel):
    """Text normalization configuration"""
    remove_stopwords: bool = Field(default=True)
    lemmatize: bool = Field(default=True)
    handle_emojis: bool = Field(default=True)
    lowercase: bool = Field(default=True)


class EntityRecognitionConfig(BaseModel):
    """Entity recognition configuration"""
    use_spacy: bool = Field(default=True)
    extract_genres: bool = Field(default=True)
    extract_artists: bool = Field(default=True)
    extract_moods: bool = Field(default=True)


class MetadataEnrichmentConfig(BaseModel):
    """Metadata enrichment configuration"""
    min_reviews_for_profile: int = Field(default=3)
    enable_user_profiling: bool = Field(default=True)


class DataValidationConfig(BaseModel):
    """Data validation configuration"""
    required_fields: list = Field(default_factory=lambda: ['source', 'review_id', 'content'])
    optional_fields: list = Field(default_factory=lambda: ['rating', 'author', 'timestamp', 'url', 'metadata'])
    quality_threshold: float = Field(default=0.7)


class Config(BaseSettings):
    """Main configuration class for Phase 2"""
    
    # MongoDB Configuration (for reading from Phase 1)
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "spotify_reviews"
    mongodb_collection: str = "reviews"
    
    # Spam Detection
    spam_threshold: float = 0.7
    spam_num_permutations: int = 128
    
    # Deduplication
    dedup_near_duplicate_threshold: float = 0.8
    dedup_num_permutations: int = 128
    dedup_lsh_threshold: float = 0.7
    
    # Quality Filter
    quality_min_length: int = 20
    quality_max_length: int = 10000
    quality_min_words: int = 3
    quality_language_threshold: float = 0.7
    quality_relevance_threshold: float = 0.5
    
    # Text Normalization
    norm_remove_stopwords: bool = True
    norm_lemmatize: bool = True
    norm_handle_emojis: bool = True
    norm_lowercase: bool = True
    
    # Entity Recognition
    entity_use_spacy: bool = True
    entity_extract_genres: bool = True
    entity_extract_artists: bool = True
    entity_extract_moods: bool = True
    
    # Metadata Enrichment
    enrich_min_reviews_for_profile: int = 3
    enrich_enable_user_profiling: bool = True
    
    # Data Validation
    validation_required_fields: list = Field(default_factory=lambda: ['source', 'review_id', 'content'])
    validation_optional_fields: list = Field(default_factory=lambda: ['rating', 'author', 'timestamp', 'url', 'metadata'])
    validation_quality_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """
        Load configuration from YAML file
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    def to_pipeline_config(self) -> Dict[str, Any]:
        """Convert to pipeline configuration dictionary"""
        return {
            'spam_detection': {
                'spam_threshold': self.spam_threshold,
                'num_permutations': self.spam_num_permutations
            },
            'deduplication': {
                'near_duplicate_threshold': self.dedup_near_duplicate_threshold,
                'num_permutations': self.dedup_num_permutations,
                'lsh_threshold': self.dedup_lsh_threshold
            },
            'quality_filter': {
                'min_length': self.quality_min_length,
                'max_length': self.quality_max_length,
                'min_words': self.quality_min_words,
                'language_threshold': self.quality_language_threshold,
                'relevance_threshold': self.quality_relevance_threshold
            },
            'text_normalization': {
                'remove_stopwords': self.norm_remove_stopwords,
                'lemmatize': self.norm_lemmatize,
                'handle_emojis': self.norm_handle_emojis,
                'lowercase': self.norm_lowercase
            },
            'entity_recognition': {
                'use_spacy': self.entity_use_spacy,
                'extract_genres': self.entity_extract_genres,
                'extract_artists': self.entity_extract_artists,
                'extract_moods': self.entity_extract_moods
            },
            'metadata_enrichment': {
                'min_reviews_for_profile': self.enrich_min_reviews_for_profile,
                'enable_user_profiling': self.enrich_enable_user_profiling
            },
            'data_validation': {
                'required_fields': self.validation_required_fields,
                'optional_fields': self.validation_optional_fields,
                'quality_threshold': self.validation_quality_threshold
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.model_dump()


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment variables
    
    Args:
        config_path: Optional path to YAML configuration file
        
    Returns:
        Config instance
    """
    if config_path and Path(config_path).exists():
        return Config.from_yaml(config_path)
    else:
        return Config()
