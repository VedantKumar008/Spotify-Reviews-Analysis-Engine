# Phase 2: Data Processing & Preprocessing

This phase implements the data processing and preprocessing pipeline for the Spotify Reviews Analysis Engine. It cleans, normalizes, enriches, and validates the raw data collected in Phase 1.

## Overview

Phase 2 focuses on:
- **Data Cleaning**: Spam detection, deduplication, and quality filtering
- **Text Normalization**: Tokenization, stopword removal, lemmatization, and emoji handling
- **Entity Recognition**: Named entity extraction and Spotify-specific feature identification
- **Metadata Enrichment**: User profiling and content classification
- **Data Validation**: Schema validation and quality metrics

## Project Structure

```
phase2_data_processing/
├── cleaning/
│   ├── __init__.py
│   ├── spam_detector.py          # ML-based spam detection
│   ├── deduplicator.py           # Duplicate and near-duplicate removal
│   └── quality_filter.py         # Quality-based filtering
├── normalization/
│   ├── __init__.py
│   ├── text_normalizer.py        # Text normalization and preprocessing
│   └── entity_recognizer.py      # Entity and feature extraction
├── enrichment/
│   ├── __init__.py
│   └── metadata_enricher.py      # User profiling and content classification
├── validation/
│   ├── __init__.py
│   └── data_validator.py         # Schema validation and quality checks
├── pipeline/
│   ├── __init__.py
│   └── processing_pipeline.py    # Main processing orchestrator
├── config/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   └── config.yaml               # YAML configuration file
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
- MongoDB 4.4+ (with data from Phase 1)
- spaCy English model: `python -m spacy download en_core_web_sm`

### Setup

1. **Clone the repository and navigate to Phase 2 directory:**
   ```bash
   cd phase2_data_processing
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

4. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Download NLTK data:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
   ```

6. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=reviews

# Spam Detection
SPAM_THRESHOLD=0.7
SPAM_NUM_PERMUTATIONS=128

# Deduplication
DEDUP_NEAR_DUPLICATE_THRESHOLD=0.8
DEDUP_NUM_PERMUTATIONS=128
DEDUP_LSH_THRESHOLD=0.7

# Quality Filter
QUALITY_MIN_LENGTH=20
QUALITY_MAX_LENGTH=10000
QUALITY_MIN_WORDS=3
QUALITY_LANGUAGE_THRESHOLD=0.7
QUALITY_RELEVANCE_THRESHOLD=0.5

# Text Normalization
NORM_REMOVE_STOPWORDS=true
NORM_LEMMATIZE=true
NORM_HANDLE_EMOJIS=true
NORM_LOWERCASE=true

# Entity Recognition
ENTITY_USE_SPACY=true
ENTITY_EXTRACT_GENRES=true
ENTITY_EXTRACT_ARTISTS=true
ENTITY_EXTRACT_MOODS=true

# Metadata Enrichment
ENRICH_MIN_REVIEWS_FOR_PROFILE=3
ENRICH_ENABLE_USER_PROFILING=true

# Data Validation
VALIDATION_QUALITY_THRESHOLD=0.7
```

### YAML Configuration

Alternatively, use `config/config.yaml` for configuration:

```yaml
mongodb:
  connection_string: mongodb://localhost:27017
  database: spotify_reviews
  collection: reviews

spam_detection:
  threshold: 0.7
  num_permutations: 128

deduplication:
  near_duplicate_threshold: 0.8
  num_permutations: 128
  lsh_threshold: 0.7

quality_filter:
  min_length: 20
  max_length: 10000
  min_words: 3
  language_threshold: 0.7
  relevance_threshold: 0.5
```

## Usage

### Manual Execution

Run the processing pipeline manually:

```bash
python main.py
```

This will:
1. Load configuration from environment variables or YAML
2. Connect to MongoDB to fetch raw reviews from Phase 1
3. Run the complete processing pipeline
4. Display statistics and results

### Programmatic Usage

Use the processing pipeline in your Python code:

```python
from config import load_config
from pipeline import ProcessingPipeline
from storage.mongodb_schema import MongoDBStorage

# Load configuration
config = load_config()

# Connect to MongoDB
mongodb = MongoDBStorage({
    'mongodb_connection_string': config.mongodb_connection_string,
    'mongodb_database': config.mongodb_database,
    'mongodb_collection': config.mongodb_collection
})
mongodb.connect()

# Fetch raw reviews
raw_reviews = mongodb.get_all_reviews(limit=1000)

# Initialize pipeline
pipeline_config = config.to_pipeline_config()
pipeline = ProcessingPipeline(pipeline_config)

# Run processing
result = pipeline.process(raw_reviews)

# Get report
report = pipeline.get_pipeline_report()
print(f"Original: {report['summary']['original_count']}")
print(f"Final: {report['summary']['final_count']}")
print(f"Removed: {report['summary']['total_removed']}")

# Disconnect
mongodb.disconnect()
```

## Processing Pipeline

The processing pipeline consists of 7 sequential steps:

### Step 1: Spam Detection

**Module**: `SpamDetector`

Detects and removes spam and bot-generated content using:
- Pattern-based detection (spam keywords, URLs)
- Length-based detection
- Repetition detection
- ML-based classification (if trained)

**Configuration**:
- `spam_threshold`: Confidence threshold for spam classification (default: 0.7)
- `num_permutations`: Number of permutations for MinHash (default: 128)

### Step 2: Deduplication

**Module**: `Deduplicator`

Removes exact and near-duplicate content using:
- Exact duplicate detection via content hashing
- Near-duplicate detection via MinHash and LSH
- Cross-source deduplication support

**Configuration**:
- `near_duplicate_threshold`: Jaccard similarity threshold (default: 0.8)
- `num_permutations`: Number of MinHash permutations (default: 128)
- `lsh_threshold`: LSH similarity threshold (default: 0.7)

### Step 3: Quality Filtering

**Module**: `QualityFilter`

Filters reviews based on quality metrics:
- Content length validation
- Word count validation
- Meaningful content detection
- Spotify relevance checking
- Special character analysis
- Gibberish detection

**Configuration**:
- `min_length`: Minimum content length (default: 20)
- `max_length`: Maximum content length (default: 10000)
- `min_words`: Minimum word count (default: 3)
- `relevance_threshold`: Minimum relevance score (default: 0.5)

### Step 4: Text Normalization

**Module**: `TextNormalizer`

Normalizes text for NLP processing:
- Emoji handling (conversion to text descriptions)
- Lowercase conversion
- Special character removal
- Tokenization
- Stopword removal
- Lemmatization

**Configuration**:
- `remove_stopwords`: Enable stopword removal (default: true)
- `lemmatize`: Enable lemmatization (default: true)
- `handle_emojis`: Enable emoji handling (default: true)
- `lowercase`: Enable lowercase conversion (default: true)

### Step 5: Entity Recognition

**Module**: `EntityRecognizer`

Extracts entities and features from text:
- Named entity recognition (PERSON, ORG, etc.)
- Spotify feature detection (Discover Weekly, AI DJ, etc.)
- Genre extraction
- Artist extraction
- Mood extraction

**Configuration**:
- `use_spacy`: Use spaCy for NER (default: true)
- `extract_genres`: Enable genre extraction (default: true)
- `extract_artists`: Enable artist extraction (default: true)
- `extract_moods`: Enable mood extraction (default: true)

### Step 6: Metadata Enrichment

**Module**: `MetadataEnricher`

Enriches reviews with additional metadata:
- Content classification (topic, intent, sentiment)
- Discovery relevance detection
- User profiling (activity level, credibility, patterns)

**Configuration**:
- `min_reviews_for_profile`: Minimum reviews for user profile (default: 3)
- `enable_user_profiling`: Enable user profiling (default: true)

### Step 7: Data Validation

**Module**: `DataValidator`

Validates processed data for quality and integrity:
- Schema validation (required/optional fields)
- Field type validation
- Content quality validation
- Timestamp validation
- URL validation
- Metadata structure validation

**Configuration**:
- `required_fields`: List of required fields
- `optional_fields`: List of optional fields
- `quality_threshold`: Minimum quality score (default: 0.7)

## Data Schema

### Input Schema (from Phase 1)

```python
{
    "source": "app_store",
    "review_id": "unique_id",
    "content": "Review text",
    "rating": 4.5,
    "author": "username",
    "timestamp": "2024-01-01T00:00:00Z",
    "url": "https://...",
    "metadata": {...}
}
```

### Output Schema (after Phase 2)

```python
{
    # Original fields
    "source": "app_store",
    "review_id": "unique_id",
    "content": "Review text",
    "rating": 4.5,
    "author": "username",
    "timestamp": "2024-01-01T00:00:00Z",
    "url": "https://...",
    "metadata": {...},
    
    # Normalization
    "normalized_content": "normalized text",
    "tokens": ["token1", "token2"],
    "lemmas": ["lemma1", "lemma2"],
    "emoji_count": 2,
    "emoji_descriptions": ["smiling face", "thumbs up"],
    
    # Entities
    "entities": [{"text": "Spotify", "label": "ORG"}],
    "spotify_features": [{"feature_name": "discover_weekly", "feature_type": "playlist"}],
    "genres": ["pop", "rock"],
    "artists": ["Artist Name"],
    "moods": ["happy", "energetic"],
    
    # Enrichment
    "content_classification": {
        "topic": "discovery",
        "intent": "suggestion",
        "sentiment_proxy": "positive",
        "discovery_related": true
    },
    "user_profile": {
        "activity_level": "medium",
        "source_credibility": 0.7,
        "listening_patterns": {...},
        "preferences": [...]
    }
}
```

## API Reference

### ProcessingPipeline

Main orchestrator for data processing.

**Methods:**
- `process(reviews)`: Run complete processing pipeline
- `get_pipeline_report()`: Get comprehensive pipeline report

### SpamDetector

ML-based spam detection.

**Methods:**
- `detect_spam(content)`: Detect if content is spam
- `train(labeled_data)`: Train spam detection model
- `detect_batch(contents)`: Detect spam for multiple contents

### Deduplicator

Duplicate and near-duplicate removal.

**Methods:**
- `deduplicate(reviews)`: Remove duplicates from reviews
- `cross_source_deduplication(reviews_by_source)`: Deduplicate across sources

### QualityFilter

Quality-based filtering.

**Methods:**
- `filter_review(review)`: Filter a single review
- `filter_batch(reviews)`: Filter a batch of reviews

### TextNormalizer

Text normalization and preprocessing.

**Methods:**
- `normalize(text)`: Normalize text
- `normalize_batch(texts)`: Normalize multiple texts

### EntityRecognizer

Entity and feature extraction.

**Methods:**
- `extract_entities(text)`: Extract named entities
- `extract_spotify_features(text)`: Extract Spotify features
- `extract_genres(text)`: Extract music genres
- `extract_all(text)`: Extract all entities and features

### MetadataEnricher

Metadata enrichment and user profiling.

**Methods:**
- `enrich_review(review)`: Enrich a single review
- `enrich_batch(reviews)`: Enrich a batch of reviews
- `get_user_profiles()`: Get all user profiles

### DataValidator

Schema validation and quality checks.

**Methods:**
- `validate_review(review)`: Validate a single review
- `validate_batch(reviews)`: Validate a batch of reviews
- `check_data_freshness(reviews)`: Check data freshness
- `check_data_completeness(reviews)`: Check data completeness

## Performance Considerations

### Memory Usage

- Large datasets may require significant memory for deduplication
- Process in batches if memory is limited
- Adjust `num_permutations` to balance accuracy and memory

### Processing Speed

- spaCy NER can be slow for large datasets
- Consider disabling entity recognition for faster processing
- Use multiprocessing for batch processing (future enhancement)

### Database Load

- Processing reads from MongoDB Phase 1 collection
- Consider indexing on frequently queried fields
- Use connection pooling for concurrent access

## Troubleshooting

### spaCy Model Not Found

**Problem**: `OSError: [E050] Can't find model 'en_core_web_sm'`

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### NLTK Data Missing

**Problem**: NLTK resource not found errors

**Solution**:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### Memory Issues

**Problem**: Out of memory during processing

**Solution**:
- Reduce batch size
- Decrease `num_permutations` in deduplication
- Disable spaCy NER if not needed
- Process data in smaller chunks

### Slow Processing

**Problem**: Pipeline takes too long

**Solution**:
- Disable optional steps (entity recognition, user profiling)
- Use smaller dataset for testing
- Consider parallel processing (future enhancement)

## Integration with Phase 1

Phase 2 reads raw reviews from MongoDB collection populated by Phase 1:

```python
# Phase 1 writes to: spotify_reviews.reviews
# Phase 2 reads from: spotify_reviews.reviews
```

To integrate:
1. Ensure Phase 1 has populated MongoDB with raw reviews
2. Configure Phase 2 with same MongoDB connection
3. Run Phase 2 processing pipeline
4. Processed reviews are ready for Phase 3 (AI/ML Analysis)

## Future Enhancements

- [ ] Add multiprocessing support for faster processing
- [ ] Implement incremental processing (only process new reviews)
- [ ] Add support for streaming data processing
- [ ] Implement advanced spam detection with deep learning
- [ ] Add support for multiple languages
- [ ] Implement custom entity recognition models
- [ ] Add real-time quality monitoring
- [ ] Implement data versioning and rollback

## Development

### Adding a New Processing Step

1. Create a new module in the appropriate package
2. Implement the processing logic
3. Add configuration options to `config.py`
4. Integrate into `ProcessingPipeline.process()`
5. Add statistics tracking
6. Update documentation

### Testing

Run tests (when implemented):

```bash
pytest tests/
```

## Contributing

When contributing to Phase 2:

1. Follow the existing code style
2. Add appropriate logging
3. Update documentation
4. Test with various data quality levels
5. Ensure backward compatibility
6. Add configuration options for new features

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues related to Phase 2, please refer to the main project documentation.
