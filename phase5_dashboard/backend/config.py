"""
Backend Configuration
Handles configuration loading and validation for Phase 5 Dashboard
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MongoDBConfig(BaseModel):
    """MongoDB configuration"""
    connection_string: str = "mongodb://localhost:27017"
    database: str = "spotify_reviews"
    collection: str = "ml_analyzed_reviews"


class FlaskConfig(BaseModel):
    """Flask configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True


class CORSConfig(BaseModel):
    """CORS configuration"""
    origins: list = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])


class Config(BaseSettings):
    """Main configuration class for Phase 5 Backend"""
    
    # MongoDB
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "spotify_reviews"
    mongodb_collection: str = "ml_analyzed_reviews"
    
    # Flask
    flask_host: str = "0.0.0.0"
    flask_port: int = 5000
    flask_debug: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def mongodb(self) -> MongoDBConfig:
        """Get MongoDB configuration"""
        return MongoDBConfig(
            connection_string=self.mongodb_connection_string,
            database=self.mongodb_database,
            collection=self.mongodb_collection
        )
    
    @property
    def flask(self) -> FlaskConfig:
        """Get Flask configuration"""
        return FlaskConfig(
            host=self.flask_host,
            port=self.flask_port,
            debug=self.flask_debug
        )
    
    @property
    def cors(self) -> CORSConfig:
        """Get CORS configuration"""
        return CORSConfig(
            origins=self.cors_origins.split(",")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'mongodb': self.mongodb.model_dump(),
            'flask': self.flask.model_dump(),
            'cors': self.cors.model_dump()
        }


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment variables
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config instance
    """
    return Config()
