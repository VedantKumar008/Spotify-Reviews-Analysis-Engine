# Phase 3: AI/ML Analysis Engine

This phase implements the AI/ML analysis engine for the Spotify Reviews Analysis Engine. It applies advanced NLP and machine learning techniques to extract insights from processed reviews.

## Overview

Phase 3 focuses on:
- **Sentiment Analysis**: Multi-dimensional sentiment analysis including overall sentiment, aspect-based sentiment, and emotion detection
- **Topic Modeling**: Unsupervised clustering and topic extraction using LDA, K-means, and DBSCAN
- **Pattern Recognition**: Detection of recurring complaints, recommendation quality patterns, and listening behaviors
- **User Behavior Analysis**: Extraction of listening goals, patterns, and habit indicators
- **Insight Extraction**: Identification of pain points, opportunities, and research hypotheses

## Project Structure

```
phase3_ml_analysis/
├── sentiment/
│   ├── __init__.py
│   └── sentiment_analyzer.py        # Multi-dimensional sentiment analysis
├── topic_modeling/
│   ├── __init__.py
│   └── topic_modeler.py             # Topic modeling and clustering
├── pattern_recognition/
│   ├── __init__.py
│   └── pattern_detector.py          # Pattern detection and recognition
├── behavior_analysis/
│   ├── __init__.py
│   └── behavior_analyzer.py         # User behavior analysis
├── insight_extraction/
│   ├── __init__.py
│   └── insight_extractor.py         # Insight and hypothesis generation
├── pipeline/
│   ├── __init__.py
│   └── ml_analysis_pipeline.py      # Main ML analysis orchestrator
├── config/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   └── config.yaml                 # YAML configuration file
├── utils/
│   └── __init__.py
├── main.py                          # Entry point for manual execution
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Installation

### Prerequisites

- Python 3.11+
- MongoDB 4.4+ (with processed data from Phase 2)
- spaCy English model: `python -m spacy download en_core_web_sm`

### Setup

1. **Clone the repository and navigate to Phase 3 directory:**
   ```bash
   cd phase3_ml_analysis
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
# MongoDB Configuration (for reading from Phase 2)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=processed_reviews

# Sentiment Analysis
SENTIMENT_CONFIDENCE_THRESHOLD=0.5

# Topic Modeling
TOPIC_METHOD=lda
TOPIC_N_TOPICS=10
TOPIC_MAX_FEATURES=1000
TOPIC_MIN_DF=2
TOPIC_MAX_DF=0.8

# Pattern Recognition
PATTERN_MIN_FREQUENCY=5
PATTERN_CONFIDENCE_THRESHOLD=0.6

# Behavior Analysis
BEHAVIOR_MIN_FREQUENCY=3

# Insight Extraction
INSIGHT_MIN_FREQUENCY=5
INSIGHT_SEVERITY_THRESHOLD=0.5
```

### YAML Configuration

Alternatively, use `config/config.yaml` for configuration:

```yaml
mongodb:
  connection_string: mongodb://localhost:27017
  database: spotify_reviews
  collection: processed_reviews

sentiment_analysis:
  confidence_threshold: 0.5

topic_modeling:
  method: lda
  n_topics: 10
  max_features: 1000
  min_df: 2
  max_df: 0.8
```

## Usage

### Manual Execution

Run the ML analysis pipeline manually:

```bash
python main.py
```

This will:
1. Load configuration from environment variables or YAML
2. Connect to MongoDB to fetch processed reviews from Phase 2
3. Run the complete ML analysis pipeline
4. Display statistics and results

### Programmatic Usage

Use the ML analysis pipeline in your Python code:

```python
from config import load_config
from pipeline import MLAnalysisPipeline
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

# Fetch processed reviews
processed_reviews = mongodb.get_all_reviews(limit=1000)

# Initialize pipeline
pipeline_config = config.to_pipeline_config()
pipeline = MLAnalysisPipeline(pipeline_config)

# Run analysis
result = pipeline.analyze(processed_reviews)

# Get report
report = pipeline.get_analysis_report()
print(f"Total reviews: {report['summary']['total_reviews']}")
print(f"Duration: {report['summary']['duration']:.2f}s")

# Get prioritized insights
prioritized = pipeline.get_prioritized_insights(result['insight_results'])

# Disconnect
mongodb.disconnect()
```

## ML Analysis Pipeline

The ML analysis pipeline consists of 5 sequential steps:

### Step 1: Sentiment Analysis

**Module**: `SentimentAnalyzer`

Performs multi-dimensional sentiment analysis:
- Overall sentiment (positive, negative, neutral)
- Sentiment score (-1 to 1)
- Confidence score
- Emotion detection (joy, sadness, anger, fear, surprise, disgust)
- Aspect-based sentiment (discovery, recommendations, UI, content, features, performance)

**Configuration**:
- `confidence_threshold`: Minimum confidence for sentiment classification (default: 0.5)

### Step 2: Topic Modeling

**Module**: `TopicModeler`

Performs topic modeling and clustering:
- LDA (Latent Dirichlet Allocation)
- K-means clustering
- DBSCAN clustering
- Topic extraction with top words
- Document-topic assignments
- Coherence scoring

**Configuration**:
- `method`: Clustering method (lda, kmeans, dbscan)
- `n_topics`: Number of topics (default: 10)
- `max_features`: Maximum features for TF-IDF (default: 1000)
- `min_df`: Minimum document frequency (default: 2)
- `max_df`: Maximum document frequency (default: 0.8)

### Step 3: Pattern Recognition

**Module**: `PatternDetector`

Detects patterns in user feedback:
- Recurring complaints (repetitive content, limited variety, algorithm issues, UI problems, discovery difficulties)
- Recommendation quality patterns (predictable, irrelevant, context-aware, variety)
- Listening behavior patterns (habitual, mood-based, activity-based, discovery-focused, nostalgic)

**Configuration**:
- `min_frequency`: Minimum frequency for pattern detection (default: 5)
- `confidence_threshold`: Minimum confidence for pattern classification (default: 0.6)

### Step 4: Behavior Analysis

**Module**: `BehaviorAnalyzer`

Analyzes user listening behavior:
- Listening goal extraction (mood matching, activity matching, discovery, familiarity, variety)
- Behavior pattern detection (discovery-focused, habitual, mood-based, activity-based, social, nostalgic)
- Habit indicator counting (repetitive listening, playlist dependence, artist loyalty, genre preference, time-based)
- User segmentation based on behavior

**Configuration**:
- `min_frequency`: Minimum frequency for pattern detection (default: 3)

### Step 5: Insight Extraction

**Module**: `InsightExtractor`

Extracts actionable insights:
- Pain point identification (discovery difficulty, repetitive content, poor recommendations, limited variety, UI issues)
- Opportunity identification (improve discovery, personalization, context-aware, social features, content variety)
- Research hypothesis generation
- Insight prioritization by impact and severity

**Configuration**:
- `min_frequency`: Minimum frequency for insight extraction (default: 5)
- `severity_threshold`: Minimum severity for pain points (default: 0.5)

## Data Schema

### Input Schema (from Phase 2)

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
    
    # Normalization fields
    "normalized_content": "normalized text",
    "tokens": ["token1", "token2"],
    "lemmas": ["lemma1", "lemma2"],
    
    # Entity fields
    "entities": [{"text": "Spotify", "label": "ORG"}],
    "spotify_features": [{"feature_name": "discover_weekly", "feature_type": "playlist"}],
    "genres": ["pop", "rock"],
    "artists": ["Artist Name"],
    "moods": ["happy", "energetic"],
    
    # Enrichment fields
    "content_classification": {
        "topic": "discovery",
        "intent": "suggestion",
        "sentiment_proxy": "positive",
        "discovery_related": true
    }
}
```

### Output Schema (after Phase 3)

```python
{
    # All Phase 2 fields preserved
    
    # Sentiment Analysis
    "sentiment": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.7,
        "confidence": 0.85,
        "emotions": {"joy": 0.8, "sadness": 0.1},
        "aspects": {"discover_weekly": "positive", "ui_ux": "neutral"}
    },
    
    # Topic Assignment
    "topic_id": 3,
    "topic_confidence": 0.75,
    
    # Pattern Detection
    "patterns": ["discovery_focused", "mood_based"],
    
    # Behavior Analysis
    "listening_goals": ["mood_matching", "discovery"],
    "behavior_pattern": "mood_based",
    
    # Insight Classification
    "pain_points": ["discovery_difficulty"],
    "opportunities": ["improve_discovery"]
}
```

## API Reference

### MLAnalysisPipeline

Main orchestrator for ML analysis.

**Methods:**
- `analyze(reviews)`: Run complete ML analysis pipeline
- `get_analysis_report()`: Get comprehensive analysis report
- `get_prioritized_insights(insight_results)`: Get prioritized insights

### SentimentAnalyzer

Multi-dimensional sentiment analyzer.

**Methods:**
- `analyze(text)`: Analyze sentiment of text
- `analyze_batch(texts)`: Analyze sentiment for multiple texts
- `get_statistics(results)`: Get sentiment analysis statistics

### TopicModeler

Topic modeling and clustering.

**Methods:**
- `fit(documents)`: Fit topic model on documents
- `predict(documents)`: Predict topics for new documents
- `get_topic_words(topic_id, n_words)`: Get top words for a topic
- `get_statistics(result)`: Get topic modeling statistics

### PatternDetector

Pattern detection and recognition.

**Methods:**
- `detect_patterns(reviews)`: Detect all patterns in reviews
- `extract_ngrams(texts, n)`: Extract frequent n-grams
- `get_statistics(result)`: Get pattern recognition statistics

### BehaviorAnalyzer

User behavior analysis.

**Methods:**
- `analyze(reviews)`: Analyze user behavior from reviews
- `analyze_user_segments(reviews)`: Segment users based on behavior
- `get_statistics(result)`: Get behavior analysis statistics

### InsightExtractor

Insight and hypothesis generation.

**Methods:**
- `extract_insights(reviews, sentiment_results, pattern_results)`: Extract insights
- `prioritize_insights(result)`: Prioritize insights by impact
- `get_statistics(result)`: Get insight extraction statistics

## Performance Considerations

### Memory Usage

- Topic modeling with large datasets may require significant memory
- Adjust `max_features` and `n_topics` to balance accuracy and memory
- Process in batches if memory is limited

### Processing Speed

- LDA can be slow for large datasets
- K-means is generally faster than LDA
- DBSCAN can be slow with high-dimensional data
- Consider using smaller datasets for testing

### Model Selection

- LDA: Good for interpretable topics
- K-means: Fast and scalable
- DBSCAN: Good for discovering clusters of arbitrary shape

## Troubleshooting

### Memory Issues

**Problem**: Out of memory during topic modeling

**Solution**:
- Reduce `max_features` in configuration
- Decrease `n_topics`
- Process data in smaller batches
- Use K-means instead of LDA

### Slow Processing

**Problem**: Pipeline takes too long

**Solution**:
- Use K-means instead of LDA for topic modeling
- Reduce dataset size for testing
- Disable optional steps
- Use smaller `n_topics`

### Poor Topic Quality

**Problem**: Topics are not meaningful

**Solution**:
- Adjust `min_df` and `max_df` parameters
- Increase `n_topics`
- Try different clustering methods
- Preprocess text more aggressively

## Integration with Phase 2

Phase 3 reads processed reviews from MongoDB collection populated by Phase 2:

```python
# Phase 2 writes to: spotify_reviews.processed_reviews
# Phase 3 reads from: spotify_reviews.processed_reviews
```

To integrate:
1. Ensure Phase 2 has processed raw reviews
2. Configure Phase 3 with same MongoDB connection
3. Run Phase 3 ML analysis pipeline
4. Analysis results are ready for Phase 4 (Insight Generation & User Segmentation)

## Future Enhancements

- [ ] Add BERT-based sentiment analysis
- [ ] Implement BERTopic for advanced topic modeling
- [ ] Add support for transformer-based models
- [ ] Implement real-time pattern detection
- [ ] Add visualization for topics and patterns
- [ ] Implement cross-source pattern analysis
- [ ] Add time-series analysis for trend detection
- [ ] Implement advanced clustering algorithms

## Development

### Adding a New Analysis Module

1. Create a new module in the appropriate package
2. Implement the analysis logic
3. Add configuration options to `config.py`
4. Integrate into `MLAnalysisPipeline.analyze()`
5. Add statistics tracking
6. Update documentation

### Testing

Run tests (when implemented):

```bash
pytest tests/
```

## Contributing

When contributing to Phase 3:

1. Follow the existing code style
2. Add appropriate logging
3. Update documentation
4. Test with various data quality levels
5. Ensure backward compatibility
6. Add configuration options for new features

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues related to Phase 3, please refer to the main project documentation.
