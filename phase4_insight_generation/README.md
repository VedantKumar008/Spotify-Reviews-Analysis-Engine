# Phase 4: Insight Generation & User Segmentation

This phase implements the insight generation and user segmentation pipeline for the Spotify Reviews Analysis Engine. It transforms analyzed data into actionable insights, user segments, and research hypotheses.

## Overview

Phase 4 focuses on:
- **Automated Summarization**: Extractive and abstractive summarization of review data
- **User Segmentation**: Clustering-based and rule-based user segmentation
- **Theme Taxonomy**: Hierarchical theme structure and relationship mapping
- **Opportunity Mapping**: Unmet need categorization and product opportunity scoring
- **Hypothesis Generation**: Research hypothesis templates and automated scoring

## Project Structure

```
phase4_insight_generation/
├── summarization/
│   ├── __init__.py
│   └── summarizer.py              # Automated summarization
├── segmentation/
│   ├── __init__.py
│   └── user_segmenter.py          # User segmentation
├── taxonomy/
│   ├── __init__.py
│   └── theme_taxonomy.py          # Theme taxonomy and relationships
├── opportunity_mapping/
│   ├── __init__.py
│   └── opportunity_mapper.py      # Opportunity mapping and scoring
├── hypothesis_generation/
│   ├── __init__.py
│   └── hypothesis_generator.py   # Research hypothesis generation
├── pipeline/
│   ├── __init__.py
│   └── insight_generation_pipeline.py  # Main orchestrator
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
- MongoDB 4.4+ (with ML-analyzed data from Phase 3)

### Setup

1. **Clone the repository and navigate to Phase 4 directory:**
   ```bash
   cd phase4_insight_generation
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

4. **Download NLTK data:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# MongoDB Configuration (for reading from Phase 3)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=ml_analyzed_reviews

# Summarization
SUMMARY_MAX_SENTENCES=5
SUMMARY_MIN_SENTENCE_LENGTH=10

# Segmentation
SEGMENTATION_METHOD=hybrid
SEGMENTATION_N_CLUSTERS=6

# Taxonomy
TAXONOMY_MIN_THEME_FREQUENCY=5

# Opportunity Mapping
OPPORTUNITY_IMPACT_THRESHOLD=0.6
OPPORTUNITY_FEASIBILITY_THRESHOLD=0.5

# Hypothesis Generation
HYPOTHESIS_MIN_SUPPORT_SCORE=0.5
```

### YAML Configuration

Alternatively, use `config/config.yaml` for configuration:

```yaml
mongodb:
  connection_string: mongodb://localhost:27017
  database: spotify_reviews
  collection: ml_analyzed_reviews

summarization:
  max_sentences: 5
  min_sentence_length: 10

segmentation:
  method: hybrid
  n_clusters: 6
```

## Usage

### Manual Execution

Run the insight generation pipeline manually:

```bash
python main.py
```

This will:
1. Load configuration from environment variables or YAML
2. Connect to MongoDB to fetch ML-analyzed reviews from Phase 3
3. Run the complete insight generation pipeline
4. Display statistics and results

### Programmatic Usage

Use the insight generation pipeline in your Python code:

```python
from config import load_config
from pipeline import InsightGenerationPipeline
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

# Fetch ML-analyzed reviews
ml_analyzed_reviews = mongodb.get_all_reviews(limit=1000)

# Initialize pipeline
pipeline_config = config.to_pipeline_config()
pipeline = InsightGenerationPipeline(pipeline_config)

# Run insight generation
result = pipeline.generate_insights(ml_analyzed_reviews)

# Get report
report = pipeline.get_insight_report()
print(f"Total reviews: {report['summary']['total_reviews']}")
print(f"Duration: {report['summary']['duration']:.2f}s")

# Get prioritized insights
prioritized = pipeline.get_prioritized_insights(
    result['opportunity_results'],
    result['hypothesis_results']
)

# Disconnect
mongodb.disconnect()
```

## Insight Generation Pipeline

The insight generation pipeline consists of 5 sequential steps:

### Step 1: Automated Summarization

**Module**: `Summarizer`

Performs extractive and abstractive summarization:
- Extractive summarization using TF-IDF
- Abstractive summarization (simplified)
- Multi-document summarization by category
- Insight summarization (pain points, opportunities, patterns)

**Configuration**:
- `max_sentences`: Maximum sentences in summary (default: 5)
- `min_sentence_length`: Minimum sentence length (default: 10)

### Step 2: User Segmentation

**Module**: `UserSegmenter`

Segments users based on behavior and preferences:
- Clustering-based segmentation (K-means)
- Rule-based segmentation (keyword matching)
- Hybrid approach (clustering + rules)
- Segment profiles with key behaviors and motivations

**Configuration**:
- `method`: Segmentation method (clustering, rule_based, hybrid)
- `n_clusters`: Number of clusters (default: 6)

**Segments**:
- Discovery Focused
- Habitual Listener
- Mood-Based
- Activity-Based
- Genre Explorer
- Casual Listener

### Step 3: Theme Taxonomy

**Module**: `ThemeTaxonomy`

Creates hierarchical theme structure:
- Base taxonomy with parent themes
- Sub-theme definitions with keywords
- Theme frequency tracking
- Relationship mapping (parent-child, related, co-occurring)
- Theme evolution tracking

**Configuration**:
- `min_theme_frequency`: Minimum frequency for theme inclusion (default: 5)

**Theme Categories**:
- Discovery
- Recommendations
- UI/UX
- Content
- Features

### Step 4: Opportunity Mapping

**Module**: `OpportunityMapper`

Maps unmet needs to product opportunities:
- Pain point analysis
- User goal analysis
- Pattern analysis
- Opportunity categorization (functional, emotional, social)
- Impact and feasibility scoring
- Priority calculation

**Configuration**:
- `impact_threshold`: Minimum impact score (default: 0.6)
- `feasibility_threshold`: Minimum feasibility score (default: 0.5)

**Opportunity Categories**:
- Improve Discovery
- Personalization Enhancement
- Context Awareness
- Social Features
- UI Improvements
- Content Variety
- Emotional Connection
- Reduction Friction

### Step 5: Hypothesis Generation

**Module**: `HypothesisGenerator`

Generates research hypotheses from insights:
- Hypothesis templates for different types
- Pain point-based hypotheses
- Opportunity-based hypotheses
- Segment-specific hypotheses
- Pattern-based hypotheses
- Multi-criteria scoring (data support, strategic alignment, testability)

**Configuration**:
- `min_support_score`: Minimum data support score (default: 0.5)

## Data Schema

### Input Schema (from Phase 3)

```python
{
    # All Phase 2 fields preserved
    
    # Sentiment Analysis
    "sentiment": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.7,
        "confidence": 0.85,
        "emotions": {"joy": 0.8, "sadness": 0.1},
        "aspects": {"discover_weekly": "positive"}
    },
    
    # Topic Assignment
    "topic_id": 3,
    "topic_confidence": 0.75,
    
    # Pattern Detection
    "patterns": ["discovery_focused", "mood_based"],
    
    # Behavior Analysis
    "listening_goals": ["mood_matching", "discovery"],
    "behavior_pattern": "mood_based"
}
```

### Output Schema (after Phase 4)

```python
{
    # All Phase 3 fields preserved
    
    # Summary
    "summary": "Generated summary of key insights...",
    
    # Segment Assignment
    "segment_id": "discovery_focused",
    "segment_confidence": 0.8,
    
    # Theme Assignment
    "theme_id": "discover_weekly",
    "theme_level": 1,
    
    # Opportunity Classification
    "opportunity_id": "opp_discovery_123",
    "opportunity_category": "improve_discovery",
    "priority_score": 0.85,
    
    # Hypothesis Association
    "hypothesis_id": "hyp_pain_456",
    "hypothesis_statement": "Users who struggle with discovery are less likely to engage with new content"
}
```

## API Reference

### InsightGenerationPipeline

Main orchestrator for insight generation.

**Methods:**
- `generate_insights(reviews, ml_results)`: Run complete insight generation pipeline
- `get_insight_report()`: Get comprehensive insight report
- `get_prioritized_insights(opportunity_results, hypothesis_results)`: Get prioritized insights

### Summarizer

Automated summarization.

**Methods:**
- `summarize_extractive(texts)`: Perform extractive summarization
- `summarize_abstractive(texts)`: Perform abstractive summarization
- `summarize_multi_document(documents)`: Summarize multiple documents by category
- `summarize_insights(pain_points, opportunities, patterns)`: Summarize insights
- `get_summary_statistics(summaries)`: Get summarization statistics

### UserSegmenter

User segmentation.

**Methods:**
- `segment_users(reviews)`: Segment users based on reviews
- `get_segment_statistics(result)`: Get segmentation statistics

### ThemeTaxonomy

Theme taxonomy and relationships.

**Methods:**
- `build_taxonomy(reviews)`: Build theme taxonomy from reviews
- `get_theme_hierarchy()`: Get hierarchical structure
- `get_theme_by_level(level)`: Get themes at specific level
- `get_theme_evolution(reviews_by_time)`: Track theme evolution
- `get_theme_statistics()`: Get theme statistics

### OpportunityMapper

Opportunity mapping and scoring.

**Methods:**
- `map_opportunities(pain_points, user_goals, patterns)`: Map unmet needs to opportunities
- `categorize_needs(reviews)`: Categorize unmet needs by type
- `score_opportunities(opportunities)`: Score opportunities by impact and feasibility
- `get_statistics(result)`: Get opportunity mapping statistics

### HypothesisGenerator

Research hypothesis generation.

**Methods:**
- `generate_hypotheses(pain_points, opportunities, segments, patterns)`: Generate hypotheses
- `prioritize_hypotheses(result)`: Prioritize hypotheses for validation
- `get_statistics(result)`: Get hypothesis generation statistics

## Performance Considerations

### Memory Usage

- Segmentation with large datasets may require significant memory
- Adjust `n_clusters` to balance accuracy and memory
- Process in batches if memory is limited

### Processing Speed

- Summarization is generally fast
- Segmentation can be slow with large user bases
- Theme taxonomy building is efficient
- Opportunity mapping is fast
- Hypothesis generation is fast

### Scalability

- Clustering-based segmentation scales well
- Rule-based segmentation is very fast
- Hybrid approach provides balance
- Consider incremental updates for production

## Troubleshooting

### Memory Issues

**Problem**: Out of memory during segmentation

**Solution**:
- Reduce `n_clusters` in configuration
- Process data in smaller batches
- Use rule-based segmentation instead of clustering

### Poor Segmentation

**Problem**: Segments are not meaningful

**Solution**:
- Adjust feature extraction in `_extract_user_features`
- Try different segmentation methods
- Increase `n_clusters` for more granular segments
- Review segment definitions in `segment_profiles`

### Low Quality Summaries

**Problem**: Summaries are not representative

**Solution**:
- Adjust `max_sentences` for longer/shorter summaries
- Increase `min_sentence_length` to filter noise
- Review TF-IDF parameters
- Consider using transformer-based models for production

## Integration with Phase 3

Phase 4 reads ML-analyzed reviews from MongoDB collection populated by Phase 3:

```python
# Phase 3 writes to: spotify_reviews.ml_analyzed_reviews
# Phase 4 reads from: spotify_reviews.ml_analyzed_reviews
```

To integrate:
1. Ensure Phase 3 has analyzed reviews
2. Configure Phase 4 with same MongoDB connection
3. Run Phase 4 insight generation pipeline
4. Insights are ready for Phase 5 (Dashboard Development)

## Future Enhancements

- [ ] Add transformer-based summarization (BART, T5)
- [ ] Implement advanced clustering algorithms (DBSCAN, hierarchical)
- [ ] Add dynamic theme taxonomy learning
- [ ] Implement opportunity scoring with ML
- [ ] Add hypothesis validation framework
- [ ] Implement real-time insight updates
- [ ] Add visualization for segments and themes
- [ ] Implement A/B test integration for hypotheses

## Development

### Adding a New Insight Module

1. Create a new module in the appropriate package
2. Implement the insight generation logic
3. Add configuration options to `config.py`
4. Integrate into `InsightGenerationPipeline.generate_insights()`
5. Add statistics tracking
6. Update documentation

### Testing

Run tests (when implemented):

```bash
pytest tests/
```

## Contributing

When contributing to Phase 4:

1. Follow the existing code style
2. Add appropriate logging
3. Update documentation
4. Test with various data quality levels
5. Ensure backward compatibility
6. Add configuration options for new features

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues related to Phase 4, please refer to the main project documentation.
