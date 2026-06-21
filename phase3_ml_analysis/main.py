"""
Main Entry Point for Phase 3: AI/ML Analysis Engine
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from pipeline import MLAnalysisPipeline
from storage.mongodb_schema import MongoDBStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ml_analysis.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the ML analysis pipeline"""
    logger.info("=" * 80)
    logger.info("Starting Spotify Reviews ML Analysis Pipeline")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Connect to MongoDB to fetch processed reviews from Phase 2
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
        
        # Fetch processed reviews
        logger.info("Fetching processed reviews from MongoDB...")
        processed_reviews = mongodb.get_all_reviews(limit=1000)  # Limit for testing
        logger.info(f"Fetched {len(processed_reviews)} processed reviews")
        
        if not processed_reviews:
            logger.warning("No processed reviews found in MongoDB")
            logger.info("Please run Phase 2 processing pipeline first")
            return
        
        # Initialize ML analysis pipeline
        pipeline_config = config.to_pipeline_config()
        pipeline = MLAnalysisPipeline(pipeline_config)
        logger.info("ML analysis pipeline initialized")
        
        # Run ML analysis pipeline
        logger.info("Running ML analysis pipeline...")
        result = pipeline.analyze(processed_reviews)
        
        # Print results
        logger.info("=" * 80)
        logger.info("ML Analysis Results:")
        logger.info("=" * 80)
        
        report = pipeline.get_analysis_report()
        
        logger.info(f"Total reviews analyzed: {report['summary']['total_reviews']}")
        logger.info(f"Duration: {report['summary']['duration']:.2f} seconds")
        logger.info(f"Steps completed: {report['summary']['steps_completed']}")
        
        # Sentiment Analysis Results
        sentiment_stats = result['statistics']['step_results']['sentiment_analysis']
        logger.info("\nSentiment Analysis:")
        logger.info(f"  Sentiment distribution: {sentiment_stats['sentiment_distribution']}")
        logger.info(f"  Average sentiment score: {sentiment_stats['average_sentiment_score']:.3f}")
        
        # Topic Modeling Results
        topic_stats = result['statistics']['step_results']['topic_modeling']
        logger.info("\nTopic Modeling:")
        logger.info(f"  Number of topics: {topic_stats['num_topics']}")
        logger.info(f"  Coherence score: {topic_stats['coherence_score']:.3f}")
        
        # Pattern Recognition Results
        pattern_stats = result['statistics']['step_results']['pattern_recognition']
        logger.info("\nPattern Recognition:")
        logger.info(f"  Total patterns: {pattern_stats['total_patterns']}")
        logger.info(f"  Complaints found: {pattern_stats['summary']['complaints_found']}")
        logger.info(f"  Recommendation patterns: {pattern_stats['summary']['recommendation_patterns_found']}")
        
        # Behavior Analysis Results
        behavior_stats = result['statistics']['step_results']['behavior_analysis']
        logger.info("\nBehavior Analysis:")
        logger.info(f"  Goals extracted: {behavior_stats['summary']['goals_extracted']}")
        logger.info(f"  Patterns detected: {behavior_stats['summary']['patterns_detected']}")
        
        # Insight Extraction Results
        insight_stats = result['statistics']['step_results']['insight_extraction']
        logger.info("\nInsight Extraction:")
        logger.info(f"  Pain points found: {insight_stats['summary']['pain_points_found']}")
        logger.info(f"  Opportunities found: {insight_stats['summary']['opportunities_found']}")
        logger.info(f"  Hypotheses generated: {insight_stats['summary']['hypotheses_generated']}")
        
        # Get prioritized insights
        prioritized = pipeline.get_prioritized_insights(result['insight_results'])
        logger.info("\nPrioritized Insights:")
        logger.info(f"  High priority pain points: {len(prioritized['high_priority_pain_points'])}")
        logger.info(f"  High priority opportunities: {len(prioritized['high_priority_opportunities'])}")
        
        # Store ML-analyzed reviews back to MongoDB
        logger.info("\nStoring ML-analyzed reviews to MongoDB...")
        
        # Update MongoDB config for ML-analyzed reviews collection
        ml_analyzed_mongodb_config = {
            'mongodb_connection_string': config.mongodb_connection_string,
            'mongodb_database': config.mongodb_database,
            'mongodb_collection': 'ml_analyzed_reviews'
        }
        
        ml_analyzed_mongodb = MongoDBStorage(ml_analyzed_mongodb_config)
        
        if ml_analyzed_mongodb.connect():
            # Store ML-analyzed reviews by merging original reviews with ML results
            ml_analyzed_dicts = []
            for i, original_review in enumerate(processed_reviews):
                # Create ML-analyzed review by merging original with ML results
                ml_analyzed_review = original_review.copy()
                
                # Add ML analysis results to the review (simplified approach)
                ml_analyzed_review['ml_analysis'] = {
                    'analyzed': True,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
                
                # Ensure review_id is not null
                if not ml_analyzed_review.get('review_id'):
                    ml_analyzed_review['review_id'] = f'ml_analyzed_{i}'
                
                ml_analyzed_dicts.append(ml_analyzed_review)
            
            stored_count = ml_analyzed_mongodb.insert_reviews_batch(ml_analyzed_dicts)
            logger.info(f"Stored {stored_count} ML-analyzed reviews in 'ml_analyzed_reviews' collection")
            ml_analyzed_mongodb.disconnect()
        else:
            logger.error("Failed to connect to MongoDB for storing ML-analyzed reviews")
        
        logger.info("\n" + "=" * 80)
        logger.info("ML analysis pipeline completed successfully")
        logger.info("Analysis results ready for Phase 4: Insight Generation & User Segmentation")
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
