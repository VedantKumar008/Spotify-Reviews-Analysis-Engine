"""
Configuration Management
Handles configuration loading and validation
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MongoDBConfig(BaseModel):
    """MongoDB configuration"""
    connection_string: str = Field(default="mongodb://localhost:27017")
    database: str = Field(default="spotify_reviews")
    collection: str = Field(default="reviews")


class S3Config(BaseModel):
    """S3 configuration"""
    enabled: bool = Field(default=False)
    bucket_name: Optional[str] = None
    region: str = Field(default="us-east-1")
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    prefix: str = Field(default="spotify-reviews/raw")


class SourceConfig(BaseModel):
    """Source-specific configuration"""
    enabled: bool = Field(default=True)
    rate_limit_delay: float = Field(default=1.0)


class Config(BaseSettings):
    """Main configuration class"""
    
    # MongoDB
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "spotify_reviews"
    mongodb_collection: str = "reviews"
    
    # S3
    s3_enabled: bool = False
    s3_bucket_name: Optional[str] = None
    s3_region: str = "us-east-1"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    s3_prefix: str = "spotify-reviews/raw"
    
    # Sources
    app_store_enabled: bool = True
    google_play_enabled: bool = True
    reddit_enabled: bool = False
    twitter_enabled: bool = False
    forum_enabled: bool = True
    
    # Rate Limiting
    app_store_rate_limit: float = 2.0
    google_play_rate_limit: float = 1.0
    reddit_rate_limit: float = 1.0
    twitter_rate_limit: float = 1.0
    forum_rate_limit: float = 2.0
    
    # Reddit Credentials
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "SpotifyReviewAnalysis/1.0"
    
    # Twitter Credentials
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    # General Settings
    max_retries: int = 3
    timeout: int = 30
    
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
