"""
Configuration Management
Handles configuration loading and validation for Phase 4
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SummarizationConfig(BaseModel):
    """Summarization configuration"""
    max_sentences: int = Field(default=5)
    min_sentence_length: int = Field(default=10)


class SegmentationConfig(BaseModel):
    """Segmentation configuration"""
    method: str = Field(default="hybrid")
    n_clusters: int = Field(default=6)


class TaxonomyConfig(BaseModel):
    """Taxonomy configuration"""
    min_theme_frequency: int = Field(default=5)


class OpportunityMappingConfig(BaseModel):
    """Opportunity mapping configuration"""
    impact_threshold: float = Field(default=0.6)
    feasibility_threshold: float = Field(default=0.5)


class HypothesisGenerationConfig(BaseModel):
    """Hypothesis generation configuration"""
    min_support_score: float = Field(default=0.5)


class Config(BaseSettings):
    """Main configuration class for Phase 4"""
    
    # MongoDB Configuration (for reading from Phase 3)
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "spotify_reviews"
    mongodb_collection: str = "ml_analyzed_reviews"
    
    # Summarization
    summary_max_sentences: int = 5
    summary_min_sentence_length: int = 10
    
    # Segmentation
    segmentation_method: str = "hybrid"
    segmentation_n_clusters: int = 6
    
    # Taxonomy
    taxonomy_min_theme_frequency: int = 5
    
    # Opportunity Mapping
    opportunity_impact_threshold: float = 0.6
    opportunity_feasibility_threshold: float = 0.5
    
    # Hypothesis Generation
    hypothesis_min_support_score: float = 0.5
    
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
            'summarization': {
                'max_sentences': self.summary_max_sentences,
                'min_sentence_length': self.summary_min_sentence_length
            },
            'segmentation': {
                'method': self.segmentation_method,
                'n_clusters': self.segmentation_n_clusters
            },
            'taxonomy': {
                'min_theme_frequency': self.taxonomy_min_theme_frequency
            },
            'opportunity_mapping': {
                'impact_threshold': self.opportunity_impact_threshold,
                'feasibility_threshold': self.opportunity_feasibility_threshold
            },
            'hypothesis_generation': {
                'min_support_score': self.hypothesis_min_support_score
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
