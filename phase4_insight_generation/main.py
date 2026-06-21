"""
Main Entry Point for Phase 4: Insight Generation & User Segmentation
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from pipeline import InsightGenerationPipeline
from storage.mongodb_schema import MongoDBStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('insight_generation.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the insight generation pipeline"""
    logger.info("=" * 80)
    logger.info("Starting Spotify Reviews Insight Generation Pipeline")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Connect to MongoDB to fetch ML-analyzed reviews from Phase 3
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
        
        # Fetch ML-analyzed reviews
        logger.info("Fetching ML-analyzed reviews from MongoDB...")
        ml_analyzed_reviews = mongodb.get_all_reviews(limit=1000)  # Limit for testing
        logger.info(f"Fetched {len(ml_analyzed_reviews)} ML-analyzed reviews")
        
        if not ml_analyzed_reviews:
            logger.warning("No ML-analyzed reviews found in MongoDB")
            logger.info("Please run Phase 3 ML analysis pipeline first")
            return
        
        # Initialize insight generation pipeline
        pipeline_config = config.to_pipeline_config()
        pipeline = InsightGenerationPipeline(pipeline_config)
        logger.info("Insight generation pipeline initialized")
        
        # Run insight generation pipeline
        logger.info("Running insight generation pipeline...")
        result = pipeline.generate_insights(ml_analyzed_reviews)
        
        # Print results
        logger.info("=" * 80)
        logger.info("Insight Generation Results:")
        logger.info("=" * 80)
        
        report = pipeline.get_insight_report()
        
        logger.info(f"Total reviews analyzed: {report['summary']['total_reviews']}")
        logger.info(f"Duration: {report['summary']['duration']:.2f} seconds")
        logger.info(f"Steps completed: {report['summary']['steps_completed']}")
        
        # Summarization Results
        summary_stats = result['statistics']['step_results']['summarization']
        logger.info("\nSummarization:")
        logger.info(f"  Summary length: {summary_stats['summary_length']} sentences")
        logger.info(f"  Coverage score: {summary_stats['coverage_score']:.3f}")
        logger.info(f"  Method: {summary_stats['method']}")
        
        # Segmentation Results
        segmentation_stats = result['statistics']['step_results']['segmentation']
        logger.info("\nUser Segmentation:")
        logger.info(f"  Total segments: {segmentation_stats['total_segments']}")
        logger.info(f"  Total users: {segmentation_stats['total_users']}")
        logger.info(f"  Average segment size: {segmentation_stats['average_segment_size']:.1f}")
        
        # Taxonomy Results
        taxonomy_stats = result['statistics']['step_results']['taxonomy']
        logger.info("\nTheme Taxonomy:")
        logger.info(f"  Total themes: {taxonomy_stats['total_themes']}")
        logger.info(f"  Total relationships: {taxonomy_stats['total_relationships']}")
        
        # Opportunity Mapping Results
        opportunity_stats = result['statistics']['step_results']['opportunity_mapping']
        logger.info("\nOpportunity Mapping:")
        logger.info(f"  Total opportunities: {opportunity_stats['total_opportunities']}")
        logger.info(f"  High priority: {opportunity_stats['high_priority_count']}")
        logger.info(f"  Average priority: {opportunity_stats['average_priority_score']:.3f}")
        
        # Hypothesis Generation Results
        hypothesis_stats = result['statistics']['step_results']['hypothesis_generation']
        logger.info("\nHypothesis Generation:")
        logger.info(f"  Total hypotheses: {hypothesis_stats['total_hypotheses']}")
        logger.info(f"  High priority: {hypothesis_stats['high_priority_count']}")
        logger.info(f"  Average score: {hypothesis_stats['average_overall_score']:.3f}")
        
        # Get prioritized insights
        prioritized = pipeline.get_prioritized_insights(
            result['opportunity_results'],
            result['hypothesis_results']
        )
        logger.info("\nPrioritized Insights:")
        logger.info(f"  High priority opportunities: {len(prioritized['high_priority_opportunities'])}")
        logger.info(f"  Prioritized hypotheses: {len(prioritized['prioritized_hypotheses'])}")
        
        logger.info("\n" + "=" * 80)
        logger.info("Insight generation pipeline completed successfully")
        logger.info("Insights ready for Phase 5: Dashboard Development")
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
