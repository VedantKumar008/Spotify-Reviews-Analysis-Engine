# Spotify Reviews Analysis Engine

A comprehensive system for collecting, processing, analyzing, and visualizing Spotify app reviews to extract actionable insights and improve user experience.

## Overview

This project implements a complete data pipeline for Spotify reviews analysis across five phases:

- **Phase 1**: Data Collection & Ingestion
- **Phase 2**: Data Processing & Cleaning  
- **Phase 3**: ML Analysis & Feature Extraction
- **Phase 4**: Insight Generation & Recommendations
- **Phase 5**: Interactive Dashboard

## Project Structure

```
Spotify Reviews Analysis Engine/
├── phase1_data_ingestion/          # Data collection from multiple sources
├── phase2_data_processing/         # Data cleaning and preprocessing
├── phase3_ml_analysis/             # Machine learning analysis
├── phase4_insight_generation/      # Insight generation and recommendations
├── phase5_dashboard/               # Interactive dashboard
│   ├── src/                        # Frontend React application
│   └── backend/                    # Flask API server
├── storage/                        # Shared storage utilities
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 4.4+
- Spotify Developer API credentials (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Spotify Reviews Analysis Engine
   ```

2. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Create database: `spotify_reviews`
   - Configure connection string in environment variables

3. **Run Phase 1 (Data Ingestion)**
   ```bash
   cd phase1_data_ingestion
   pip install -r requirements.txt
   python main.py
   ```

4. **Run Phase 2 (Data Processing)**
   ```bash
   cd phase2_data_processing
   pip install -r requirements.txt
   python main.py
   ```

5. **Run Phase 3 (ML Analysis)**
   ```bash
   cd phase3_ml_analysis
   pip install -r requirements.txt
   python main.py
   ```

6. **Run Phase 4 (Insight Generation)**
   ```bash
   cd phase4_insight_generation
   pip install -r requirements.txt
   python main.py
   ```

7. **Run Phase 5 (Dashboard)**
   ```bash
   cd phase5_dashboard
   
   # Backend
   cd backend
   pip install -r requirements.txt
   python app.py
   
   # Frontend (in new terminal)
   cd ..
   npm install
   npm run dev
   ```

The dashboard will be available at `http://localhost:3001`

## Phase Details

### Phase 1: Data Collection & Ingestion

Collects reviews from multiple sources:
- Google Play Store
- Apple App Store
- Spotify Community Forums
- Reddit (optional)
- Twitter (optional)

**Features**:
- Configurable data sources
- Rate limiting and error handling
- Deduplication logic
- MongoDB storage
- Background processing

**Configuration**: See `phase1_data_ingestion/config.py`

### Phase 2: Data Processing & Cleaning

Cleans and preprocesses collected reviews:
- Text normalization
- Language detection
- Spam filtering
- Data validation
- Quality scoring

**Features**:
- Automated quality checks
- Multi-language support
- Custom cleaning rules
- Batch processing

### Phase 3: ML Analysis & Feature Extraction

Applies machine learning to extract insights:
- Sentiment analysis
- Topic modeling
- Named entity recognition
- Emotion detection
- Aspect-based analysis

**Features**:
- Pre-trained models
- Custom model training
- Feature extraction
- ML pipeline orchestration

### Phase 4: Insight Generation & Recommendations

Generates actionable insights from analyzed data:
- User segmentation
- Pain point identification
- Opportunity detection
- Trend analysis
- Recommendation generation

**Features**:
- Automated insight generation
- Multi-criteria scoring
- Hypothesis generation
- Action recommendations

### Phase 5: Interactive Dashboard

Visualizes insights and provides real-time monitoring:
- **Dashboard**: Overview with key metrics, sentiment trends, topic distribution
- **User Segments**: Segment analysis and behavior patterns
- **Insights**: Opportunities, hypotheses, and pain points
- **Data Ingestion**: On-demand review ingestion button

**Features**:
- Responsive design
- Interactive charts
- Real-time data updates
- Background ingestion processing
- Fallback data generation (when ML analysis unavailable)

**Dashboard Access**: `http://localhost:3001`
**Backend API**: `http://127.0.0.1:5000`

## Configuration

### Environment Variables

Create `.env` files in each phase directory as needed:

**Phase 1 (Ingestion)**:
```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=reviews
```

**Phase 5 (Dashboard Backend)**:
```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=reviews
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

## API Reference (Phase 5)

### Backend Endpoints

- `GET /` - API information and available endpoints
- `GET /api/health` - Health check
- `GET /api/stats` - Dashboard statistics
- `GET /api/sentiment` - Sentiment analysis data
- `GET /api/topics` - Topic modeling data
- `GET /api/segments` - User segmentation data
- `GET /api/insights` - Insights and opportunities
- `POST /api/ingest` - Trigger data ingestion

## Data Flow

```
Phase 1: Data Sources → MongoDB (raw reviews)
    ↓
Phase 2: Raw Reviews → Processed Reviews
    ↓
Phase 3: Processed Reviews → ML Analysis Results
    ↓
Phase 4: ML Results → Insights & Recommendations
    ↓
Phase 5: Insights → Dashboard Visualization
```

## Current Status

**Implemented Features**:
- ✅ Multi-source data ingestion
- ✅ Data processing and cleaning
- ✅ ML analysis pipeline
- ✅ Insight generation
- ✅ Interactive dashboard with 3 main components
- ✅ On-demand data ingestion
- ✅ Fallback data generation (sentiment from ratings, topics from content)
- ✅ MongoDB integration
- ✅ Responsive design

**Removed Components** (for simplicity):
- ❌ Sentiment Analysis page (integrated into dashboard)
- ❌ Topic Modeling page (integrated into dashboard)
- ❌ Real-time Updates page (simplified to polling)

## Troubleshooting

### Common Issues

**MongoDB Connection Failed**
- Verify MongoDB is running
- Check connection string in `.env`
- Ensure database exists

**Dashboard Not Loading**
- Ensure backend API is running (`http://127.0.0.1:5000`)
- Check frontend console for errors
- Verify CORS configuration

**Ingestion Not Working**
- Check API credentials in configuration
- Verify source APIs are accessible
- Check backend logs for errors

## Future Enhancements

- [ ] Add WebSocket support for real-time updates
- [ ] Implement user authentication
- [ ] Add data export functionality
- [ ] Implement custom dashboard builder
- [ ] Add mobile app version
- [ ] Integrate more sophisticated ML models
- [ ] Add automated alert system
- [ ] Implement A/B testing integration

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Update documentation
4. Test changes thoroughly
5. Ensure compatibility with existing phases

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues, please refer to the phase-specific README files:
- Phase 1: `phase1_data_ingestion/README.md`
- Phase 2: `phase2_data_processing/README.md`
- Phase 3: `phase3_ml_analysis/README.md`
- Phase 4: `phase4_insight_generation/README.md`
- Phase 5: `phase5_dashboard/README.md`
