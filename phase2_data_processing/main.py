"""
Main Entry Point for Phase 2: Data Processing & Preprocessing
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from pipeline import ProcessingPipeline
from storage.mongodb_schema import MongoDBStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('processing.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the processing pipeline"""
    logger.info("=" * 80)
    logger.info("Starting Spotify Reviews Processing Pipeline")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Connect to MongoDB to fetch raw reviews
        mongodb_config = {
            'mongodb_connection_string': config.mongodb_connection_string,
            'mongodb_database': config.mongodb_database,
            'mongodb_collection': config.mongodb_collection
        }
        
        mongodb = MongoDBStorage(mongodb_config)
        
        if not mongodb.connect():
            logger.error("Failed to connect to MongoDB")
            return
        
        logger.info("Connected to MongoDB")
        
        # Fetch raw reviews
        logger.info("Fetching raw reviews from MongoDB...")
        raw_reviews = mongodb.get_all_reviews(limit=1000)  # Limit for testing
        logger.info(f"Fetched {len(raw_reviews)} raw reviews")
        
        if not raw_reviews:
            logger.warning("No reviews found in MongoDB")
            return
        
        # Initialize processing pipeline
        pipeline_config = config.to_pipeline_config()
        pipeline = ProcessingPipeline(pipeline_config)
        logger.info("Processing pipeline initialized")
        
        # Run processing pipeline
        logger.info("Running processing pipeline...")
        result = pipeline.process(raw_reviews)
        
        # Print results
        logger.info("=" * 80)
        logger.info("Processing Results:")
        logger.info("=" * 80)
        
        report = pipeline.get_pipeline_report()
        
        logger.info(f"Original count: {report['summary']['original_count']}")
        logger.info(f"Final count: {report['summary']['final_count']}")
        logger.info(f"Total removed: {report['summary']['total_removed']}")
        logger.info(f"Removal rate: {report['summary']['removal_rate']:.2%}")
        logger.info(f"Duration: {report['summary']['duration']:.2f} seconds")
        
        logger.info("\nRemoval Breakdown:")
        logger.info(f"  Spam: {report['removal_breakdown']['spam']}")
        logger.info(f"  Duplicates: {report['removal_breakdown']['duplicates']}")
        logger.info(f"  Quality: {report['removal_breakdown']['quality']}")
        
        # Store processed reviews back to MongoDB
        logger.info("\nStoring processed reviews to MongoDB...")
        
        # Update MongoDB config for processed reviews collection
        processed_mongodb_config = {
            'mongodb_connection_string': config.mongodb_connection_string,
            'mongodb_database': config.mongodb_database,
            'mongodb_collection': 'processed_reviews'
        }
        
        processed_mongodb = MongoDBStorage(processed_mongodb_config)
        
        if processed_mongodb.connect():
            # Store processed reviews
            # Convert processed reviews to dictionaries for MongoDB
            processed_dicts = []
            for i, review in enumerate(result):
                if isinstance(review, str):
                    # If it's a string, create a basic dict structure
                    processed_dicts.append({
                        'review_id': f'processed_{i}',
                        'content': review,
                        'source': 'processed',
                        'created_at': datetime.utcnow()
                    })
                elif hasattr(review, 'dict'):
                    review_dict = review.dict()
                    # Ensure review_id is not null
                    if not review_dict.get('review_id'):
                        review_dict['review_id'] = f'processed_{i}'
                    processed_dicts.append(review_dict)
                elif isinstance(review, dict):
                    # Ensure review_id is not null
                    if not review.get('review_id'):
                        review['review_id'] = f'processed_{i}'
                    processed_dicts.append(review)
                else:
                    # Fallback: convert to string and create basic structure
                    processed_dicts.append({
                        'review_id': f'processed_{i}',
                        'content': str(review),
                        'source': 'processed',
                        'created_at': datetime.utcnow()
                    })
            
            stored_count = processed_mongodb.insert_reviews_batch(processed_dicts)
            logger.info(f"Stored {stored_count} processed reviews in 'processed_reviews' collection")
            processed_mongodb.disconnect()
        else:
            logger.error("Failed to connect to MongoDB for storing processed reviews")
        
        logger.info("Processed reviews ready for Phase 3")
        
        logger.info("\n" + "=" * 80)
        logger.info("Processing pipeline completed successfully")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise
    
    finally:
        # Disconnect
        if 'mongodb' in locals():
            mongodb.disconnect()


if __name__ == "__main__":
    main()
