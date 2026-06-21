"""
Airflow DAG for Spotify Reviews Ingestion Pipeline
Defines the scheduled workflow for data collection
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.ingestion_pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'spotify-reviews',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'spotify_reviews_ingestion',
    default_args=default_args,
    description='Ingest Spotify reviews from multiple sources',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    catchup=False,
    max_active_runs=1,
    tags=['spotify', 'reviews', 'ingestion'],
)


def run_ingestion_task(**context):
    """
    Task function to run the ingestion pipeline
    """
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Configuration from environment variables
    config = {
        # MongoDB Configuration
        'mongodb_connection_string': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017'),
        'mongodb_database': os.getenv('MONGODB_DATABASE', 'spotify_reviews'),
        'mongodb_collection': os.getenv('MONGODB_COLLECTION', 'reviews'),
        
        # S3 Configuration (optional)
        's3_enabled': os.getenv('S3_ENABLED', 'false').lower() == 'true',
        's3_bucket_name': os.getenv('S3_BUCKET_NAME'),
        's3_region': os.getenv('S3_REGION', 'us-east-1'),
        's3_access_key': os.getenv('S3_ACCESS_KEY'),
        's3_secret_key': os.getenv('S3_SECRET_KEY'),
        's3_endpoint_url': os.getenv('S3_ENDPOINT_URL'),
        's3_prefix': os.getenv('S3_PREFIX', 'spotify-reviews/raw'),
        
        # Source Configuration
        'app_store_enabled': os.getenv('APP_STORE_ENABLED', 'true').lower() == 'true',
        'google_play_enabled': os.getenv('GOOGLE_PLAY_ENABLED', 'true').lower() == 'true',
        'reddit_enabled': os.getenv('REDDIT_ENABLED', 'false').lower() == 'true',
        'twitter_enabled': os.getenv('TWITTER_ENABLED', 'false').lower() == 'true',
        'forum_enabled': os.getenv('FORUM_ENABLED', 'true').lower() == 'true',
        
        # Reddit Credentials
        'reddit_client_id': os.getenv('REDDIT_CLIENT_ID'),
        'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
        'reddit_user_agent': os.getenv('REDDIT_USER_AGENT', 'SpotifyReviewAnalysis/1.0'),
        
        # Twitter Credentials
        'twitter_bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
        'twitter_api_key': os.getenv('TWITTER_API_KEY'),
        'twitter_api_secret': os.getenv('TWITTER_API_SECRET'),
        'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
        'twitter_access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
        
        # Rate Limiting
        'app_store_rate_limit': float(os.getenv('APP_STORE_RATE_LIMIT', '2.0')),
        'google_play_rate_limit': float(os.getenv('GOOGLE_PLAY_RATE_LIMIT', '1.0')),
        'reddit_rate_limit': float(os.getenv('REDDIT_RATE_LIMIT', '1.0')),
        'twitter_rate_limit': float(os.getenv('TWITTER_RATE_LIMIT', '1.0')),
        'forum_rate_limit': float(os.getenv('FORUM_RATE_LIMIT', '2.0')),
        
        # General Settings
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'timeout': int(os.getenv('TIMEOUT', '30')),
    }
    
    # Get parameters from Airflow context (if any)
    limit_per_source = context.get('params', {}).get('limit_per_source')
    days_back = context.get('params', {}).get('days_back', 7)
    
    # Calculate date range
    since = datetime.utcnow() - timedelta(days=days_back)
    until = datetime.utcnow()
    
    logger.info(f"Running ingestion pipeline with limit: {limit_per_source}, days_back: {days_back}")
    
    # Initialize and run pipeline
    pipeline = IngestionPipeline(config)
    
    try:
        results = pipeline.run_ingestion(
            limit_per_source=limit_per_source,
            since=since,
            until=until
        )
        
        logger.info(f"Ingestion completed: {results}")
        
        # Push results to XCom
        context['task_instance'].xcom_push(key='ingestion_results', value=results)
        
        return results
        
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise
    
    finally:
        pipeline.disconnect()


# Define tasks
start_task = EmptyOperator(
    task_id='start_ingestion',
    dag=dag
)

ingestion_task = PythonOperator(
    task_id='run_ingestion',
    python_callable=run_ingestion_task,
    dag=dag,
    provide_context=True
)

end_task = EmptyOperator(
    task_id='end_ingestion',
    dag=dag
)

# Define task dependencies
start_task >> ingestion_task >> end_task
