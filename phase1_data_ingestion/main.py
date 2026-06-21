"""
Main Entry Point for Phase 1: Data Collection & Ingestion
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from orchestration import IngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ingestion.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the ingestion pipeline"""
    logger.info("=" * 80)
    logger.info("Starting Spotify Reviews Ingestion Pipeline")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize pipeline
        pipeline = IngestionPipeline(config.to_dict())
        logger.info("Pipeline initialized")
        
        # Run ingestion
        # Fetch reviews without time constraint to get new reviews
        # since = datetime.utcnow() - timedelta(days=7)
        # until = datetime.utcnow()
        
        logger.info("Fetching reviews from all available sources")
        
        results = pipeline.run_ingestion(
            limit_per_source=1000,  # Fetch up to 1000 reviews per source
            since=None,  # No time constraint to get new reviews
            until=None
        )
        
        # Print results
        logger.info("=" * 80)
        logger.info("Ingestion Results:")
        logger.info("=" * 80)
        logger.info(f"Total reviews fetched: {results['total_reviews']}")
        if 'duration' in results:
            logger.info(f"Duration: {results['duration']:.2f} seconds")
        logger.info(f"Sources processed: {len(results['sources'])}")
        
        for source, source_result in results['sources'].items():
            logger.info(f"\n{source}:")
            logger.info(f"  Success: {source_result['success']}")
            logger.info(f"  Fetched: {source_result['fetched_count']}")
            logger.info(f"  Stored: {source_result['stored_count']}")
            if source_result.get('error'):
                logger.info(f"  Error: {source_result['error']}")
        
        if results['errors']:
            logger.warning(f"\nErrors encountered: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        # Get statistics
        stats = pipeline.get_ingestion_stats()
        logger.info("\n" + "=" * 80)
        logger.info("Database Statistics:")
        logger.info("=" * 80)
        logger.info(f"Total reviews in database: {stats['total_reviews']}")
        logger.info("Source distribution:")
        for source, count in stats['source_distribution'].items():
            logger.info(f"  {source}: {count}")
        
        logger.info("\n" + "=" * 80)
        logger.info("Ingestion pipeline completed successfully")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise
    
    finally:
        # Disconnect
        if 'pipeline' in locals():
            pipeline.disconnect()


if __name__ == "__main__":
    main()
