# Phase 1: Data Collection & Ingestion

This phase implements the data collection and ingestion pipeline for the Spotify Reviews Analysis Engine. It collects user feedback from multiple sources and stores it in MongoDB and optionally in S3 for archival.

## Overview

Phase 1 focuses on:
- **Data Source Connectors**: Collecting reviews from App Store, Google Play, Reddit, Twitter, and Spotify Community Forums
- **Data Storage Layer**: Storing processed data in MongoDB with proper indexing and schema
- **Ingestion Pipeline**: Orchestrating data collection with Airflow for scheduled runs
- **Queue System**: Managing async processing with Redis (optional)

## Project Structure

```
phase1_data_ingestion/
├── connectors/
│   ├── __init__.py
│   ├── base_connector.py          # Base class for all connectors
│   ├── app_store_connector.py     # Apple App Store reviews
│   ├── google_play_connector.py   # Google Play Store reviews
│   ├── reddit_connector.py        # Reddit discussions
│   ├── twitter_connector.py       # Twitter/X conversations
│   └── forum_scraper.py           # Spotify Community Forums
├── storage/
│   ├── __init__.py
│   ├── mongodb_schema.py          # MongoDB storage and schema
│   └── s3_storage.py              # S3 data lake storage
├── orchestration/
│   ├── __init__.py
│   ├── ingestion_pipeline.py      # Main ingestion orchestrator
│   └── airflow_dag.py             # Airflow DAG for scheduling
├── config/
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   └── config.yaml                # YAML configuration file
├── utils/
│   └── __init__.py
├── main.py                        # Entry point for manual execution
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Installation

### Prerequisites

- Python 3.11+
- MongoDB 4.4+ (local or remote)
- (Optional) AWS S3 or Google Cloud Storage account
- (Optional) Apache Airflow for orchestration
- (Optional) Redis for queue management

### Setup

1. **Clone the repository and navigate to Phase 1 directory:**
   ```bash
   cd phase1_data_ingestion
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up MongoDB:**
   - For local development: Install MongoDB and start the service
   - For production: Use MongoDB Atlas or a managed MongoDB instance

6. **(Optional) Set up Airflow:**
   - Install Apache Airflow: `pip install apache-airflow`
   - Initialize the database: `airflow db init`
   - Copy the DAG file to your Airflow DAGs folder

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=reviews

# S3 Configuration (Optional)
S3_ENABLED=false
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key

# Source Configuration
APP_STORE_ENABLED=true
GOOGLE_PLAY_ENABLED=true
REDDIT_ENABLED=false
TWITTER_ENABLED=false
FORUM_ENABLED=true

# Reddit Credentials (if enabled)
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret

# Twitter Credentials (if enabled)
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret

# Rate Limiting
APP_STORE_RATE_LIMIT=2.0
GOOGLE_PLAY_RATE_LIMIT=1.0
REDDIT_RATE_LIMIT=1.0
TWITTER_RATE_LIMIT=1.0
FORUM_RATE_LIMIT=2.0
```

### YAML Configuration

Alternatively, use `config/config.yaml` for configuration:

```yaml
mongodb:
  connection_string: mongodb://localhost:27017
  database: spotify_reviews
  collection: reviews

s3:
  enabled: false
  bucket_name: your-bucket-name
  region: us-east-1

sources:
  app_store:
    enabled: true
    rate_limit_delay: 2.0
  google_play:
    enabled: true
    rate_limit_delay: 1.0
```

## Usage

### Manual Execution

Run the ingestion pipeline manually:

```bash
python main.py
```

This will:
1. Load configuration from environment variables or YAML
2. Initialize all enabled connectors
3. Fetch reviews from each source
4. Store reviews in MongoDB
5. Archive raw data to S3 (if enabled)
6. Display statistics

### Airflow Orchestration

For scheduled execution using Airflow:

1. **Copy the DAG file:**
   ```bash
   cp orchestration/airflow_dag.py $AIRFLOW_HOME/dags/
   ```

2. **Enable the DAG in the Airflow UI:**
   - Navigate to Airflow web interface
   - Find the `spotify_reviews_ingestion` DAG
   - Enable it

3. **Configure DAG parameters (optional):**
   - `limit_per_source`: Maximum reviews per source
   - `days_back`: Number of days to look back for reviews

The DAG is scheduled to run daily at 2 AM UTC by default.

### Programmatic Usage

Use the ingestion pipeline in your Python code:

```python
from config import load_config
from orchestration import IngestionPipeline
from datetime import datetime, timedelta

# Load configuration
config = load_config()

# Initialize pipeline
pipeline = IngestionPipeline(config.to_dict())

# Run ingestion
results = pipeline.run_ingestion(
    limit_per_source=100,
    since=datetime.utcnow() - timedelta(days=7),
    until=datetime.utcnow()
)

# Get statistics
stats = pipeline.get_ingestion_stats()
print(f"Total reviews: {stats['total_reviews']}")

# Disconnect
pipeline.disconnect()
```

## Data Sources

### App Store Reviews
- **Connector**: `AppStoreConnector`
- **Source**: Apple App Store RSS feed
- **Data**: Reviews, ratings, versions, timestamps
- **Rate Limit**: 2 seconds between requests

### Google Play Store Reviews
- **Connector**: `GooglePlayConnector`
- **Source**: Google Play Store API (via google-play-scraper)
- **Data**: Reviews, ratings, versions, device info
- **Rate Limit**: 1 second between requests

### Reddit Discussions
- **Connector**: `RedditConnector`
- **Source**: Reddit API (PRAW)
- **Subreddits**: r/spotify, r/music, r/listentothis, etc.
- **Data**: Posts, comments, upvotes
- **Rate Limit**: 1 second between requests
- **Requires**: Reddit API credentials

### Twitter/X Conversations
- **Connector**: `TwitterConnector`
- **Source**: Twitter API v2
- **Queries**: "spotify discovery", "spotify recommendations", etc.
- **Data**: Tweets, engagement metrics
- **Rate Limit**: 1 second between requests
- **Requires**: Twitter API credentials

### Spotify Community Forums
- **Connector**: ForumScraper
- **Source**: Web scraping
- **Categories**: Discover Weekly, Music for Every Moment, etc.
- **Data**: Forum threads, replies, kudos
- **Rate Limit**: 2 seconds between requests

## Data Storage

### MongoDB Schema

Reviews are stored in MongoDB with the following structure:

```python
{
    "source": "app_store",           # Data source type
    "review_id": "unique_id",       # Unique review identifier
    "content": "Review text",       # Review content
    "rating": 4.5,                  # Rating (if available)
    "author": "username",           # Author (if available)
    "timestamp": "2024-01-01T00:00:00Z",  # Review timestamp
    "url": "https://...",           # Source URL
    "metadata": {                   # Source-specific metadata
        "app_version": "8.8.0",
        "country": "us"
    },
    "created_at": "2024-01-01T00:00:00Z",  # Ingestion timestamp
    "updated_at": "2024-01-01T00:00:00Z"   # Last update timestamp
}
```

### Indexes

The following indexes are created for efficient querying:
- Compound index on `(source, review_id)` for uniqueness
- Index on `timestamp` for time-based queries
- Index on `source` for filtering
- Index on `rating` for analysis
- Index on `created_at` for tracking

### S3 Archival

Raw data is archived to S3 with the following structure:
```
s3://bucket-name/spotify-reviews/raw/
├── app_store/
│   ├── app_store_20240101_120000.json
│   └── app_store_20240102_120000.json
├── google_play/
│   └── ...
└── ...
```

## API Reference

### BaseConnector

Abstract base class for all data source connectors.

**Methods:**
- `connect()`: Establish connection to data source
- `fetch_reviews(limit, since, until)`: Fetch reviews
- `disconnect()`: Close connection
- `validate_review(review)`: Validate review data

### IngestionPipeline

Main orchestrator for data collection.

**Methods:**
- `run_ingestion(limit_per_source, since, until, sources)`: Run ingestion
- `get_ingestion_stats()`: Get statistics
- `disconnect()`: Disconnect from storage

### MongoDBStorage

MongoDB storage layer.

**Methods:**
- `insert_review(review_data)`: Insert single review
- `insert_reviews_batch(reviews)`: Batch insert
- `get_reviews_by_source(source, limit, since, until)`: Query by source
- `get_review_count(source)`: Get count
- `get_source_distribution()`: Get distribution by source

## Error Handling

The pipeline includes comprehensive error handling:

- **Retry Logic**: Automatic retry with exponential backoff (configurable)
- **Validation**: Review validation before storage
- **Logging**: Detailed logging to file and console
- **Graceful Degradation**: Continues with other sources if one fails

## Monitoring

### Logs

Logs are written to:
- Console (stdout)
- `ingestion.log` file

### Statistics

After each run, the pipeline outputs:
- Total reviews fetched
- Reviews per source
- Success/failure status
- Duration
- Database statistics

## Troubleshooting

### MongoDB Connection Issues

**Problem**: Cannot connect to MongoDB

**Solution**:
- Verify MongoDB is running: `mongod`
- Check connection string in `.env`
- Ensure MongoDB is accessible from your network

### Rate Limiting

**Problem**: API rate limit errors

**Solution**:
- Increase rate limit delay in configuration
- Use official API credentials when possible
- Implement proper authentication

### Reddit/Twitter Authentication

**Problem**: Authentication failures

**Solution**:
- Verify API credentials are correct
- Check that your app has necessary permissions
- Ensure credentials are not expired

### Memory Issues

**Problem**: Out of memory with large datasets

**Solution**:
- Reduce `limit_per_source`
- Process sources sequentially instead of in parallel
- Increase system memory

## Development

### Adding a New Connector

1. Create a new connector class inheriting from `BaseConnector`
2. Implement required abstract methods:
   - `_get_source_type()`
   - `connect()`
   - `fetch_reviews()`
   - `disconnect()`
3. Add configuration options to `config.py`
4. Register in `IngestionPipeline._initialize_components()`
5. Add to `connectors/__init__.py`

### Testing

Run tests (when implemented):

```bash
pytest tests/
```

## Future Enhancements

- [ ] Add Redis queue for async processing
- [ ] Implement incremental updates (only fetch new reviews)
- [ ] Add data validation and quality checks
- [ ] Implement backpressure handling
- [ ] Add support for additional data sources
- [ ] Implement real-time streaming
- [ ] Add data deduplication across sources
- [ ] Implement retry queue for failed fetches

## Contributing

When contributing to Phase 1:

1. Follow the existing code style
2. Add appropriate logging
3. Update documentation
4. Test with multiple sources
5. Ensure backward compatibility

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues related to Phase 1, please refer to the main project documentation.
