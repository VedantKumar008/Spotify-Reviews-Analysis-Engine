"""
Configuration Management
Handles configuration loading and validation for Phase 3
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SentimentAnalysisConfig(BaseModel):
    """Sentiment analysis configuration"""
    confidence_threshold: float = Field(default=0.5)


class TopicModelingConfig(BaseModel):
    """Topic modeling configuration"""
    method: str = Field(default="lda")
    n_topics: int = Field(default=10)
    max_features: int = Field(default=1000)
    min_df: int = Field(default=2)
    max_df: float = Field(default=0.8)


class PatternRecognitionConfig(BaseModel):
    """Pattern recognition configuration"""
    min_frequency: int = Field(default=5)
    confidence_threshold: float = Field(default=0.6)


class BehaviorAnalysisConfig(BaseModel):
    """Behavior analysis configuration"""
    min_frequency: int = Field(default=3)


class InsightExtractionConfig(BaseModel):
    """Insight extraction configuration"""
    min_frequency: int = Field(default=5)
    severity_threshold: float = Field(default=0.5)


class Config(BaseSettings):
    """Main configuration class for Phase 3"""
    
    # MongoDB Configuration (for reading from Phase 2)
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "spotify_reviews"
    mongodb_collection: str = "processed_reviews"
    
    # Sentiment Analysis
    sentiment_confidence_threshold: float = 0.5
    
    # Topic Modeling
    topic_method: str = "lda"
    topic_n_topics: int = 10
    topic_max_features: int = 1000
    topic_min_df: int = 2
    topic_max_df: float = 0.8
    
    # Pattern Recognition
    pattern_min_frequency: int = 5
    pattern_confidence_threshold: float = 0.6
    
    # Behavior Analysis
    behavior_min_frequency: int = 3
    
    # Insight Extraction
    insight_min_frequency: int = 5
    insight_severity_threshold: float = 0.5
    
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
            'sentiment_analysis': {
                'confidence_threshold': self.sentiment_confidence_threshold
            },
            'topic_modeling': {
                'method': self.topic_method,
                'n_topics': self.topic_n_topics,
                'max_features': self.topic_max_features,
                'min_df': self.topic_min_df,
                'max_df': self.topic_max_df
            },
            'pattern_recognition': {
                'min_frequency': self.pattern_min_frequency,
                'confidence_threshold': self.pattern_confidence_threshold
            },
            'behavior_analysis': {
                'min_frequency': self.behavior_min_frequency
            },
            'insight_extraction': {
                'min_frequency': self.insight_min_frequency,
                'severity_threshold': self.insight_severity_threshold
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
