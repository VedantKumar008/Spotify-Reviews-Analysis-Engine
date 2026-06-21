# Phase 5: Dashboard Development

This phase implements the interactive dashboard for the Spotify Reviews Analysis Engine. It provides real-time visualization of insights, user segments, and analysis results from previous phases.

## Overview

Phase 5 focuses on:
- **Frontend Framework**: React-based dashboard with modern UI components
- **Data Visualization**: Interactive charts, graphs, and visual representations
- **Interactive Components**: Filters, drill-down capabilities, and time-series analysis
- **Data Ingestion**: On-demand review ingestion with background processing
- **User Interface**: Responsive design with accessibility features

## Project Structure

```
phase5_dashboard/
├── src/
│   ├── components/
│   │   └── Layout.jsx              # Main layout with sidebar navigation
│   ├── pages/
│   │   ├── Dashboard.jsx           # Main dashboard overview
│   │   ├── UserSegments.jsx        # User segment visualization
│   │   └── Insights.jsx            # Insights and opportunities
│   ├── api/                        # API client utilities
│   ├── utils/                      # Utility functions
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── backend/
│   ├── app.py                      # Flask API server
│   ├── config.py                   # Backend configuration
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment variables template
├── package.json                    # Node.js dependencies
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS configuration
├── postcss.config.js               # PostCSS configuration
├── index.html                      # HTML entry point
├── .env.example                    # Frontend environment variables
└── README.md                       # This file
```

## Installation

### Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB 4.4+ (with data from Phase 4)

### Frontend Setup

1. **Navigate to the dashboard directory:**
   ```bash
   cd phase5_dashboard
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The dashboard will be available at `http://localhost:3000`

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string
   ```

5. **Start the Flask server:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## Configuration

### Frontend Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://localhost:5000/api
```

### Backend Environment Variables

Create a `.env` file based on `backend/.env.example`:

```env
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=spotify_reviews
MONGODB_COLLECTION=ml_analyzed_reviews

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Usage

### Running the Dashboard

1. **Start the backend API:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend:**
   ```bash
   cd phase5_dashboard
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Dashboard Pages

#### Dashboard
- Overview of key metrics (total reviews, average sentiment, active users)
- Sentiment trend visualization (derived from review ratings)
- Topic distribution pie chart (derived from review content)
- Recent alerts and notifications
- Ingestion button for on-demand data ingestion

#### User Segments
- Segment distribution pie chart
- Segment growth trends
- Segment behavior analysis
- Detailed segment profiles

#### Insights
- Pain points analysis
- Product opportunities with impact/feasibility scoring
- Research hypotheses with multi-criteria scoring
- Recommended action items

## API Reference

### Backend Endpoints

#### Health Check
```
GET /
```
Returns API information and available endpoints.

#### Health Check
```
GET /api/health
```
Returns the API health status.

#### Statistics
```
GET /api/stats
```
Returns dashboard statistics (total reviews, average sentiment, active users, recent activity).

#### Sentiment Data
```
GET /api/sentiment?range=7d&source=all
```
Returns sentiment analysis data derived from review ratings (fallback when ML analysis unavailable).

#### Topic Data
```
GET /api/topics
```
Returns topic modeling data derived from review content (fallback when ML analysis unavailable).

#### Segment Data
```
GET /api/segments
```
Returns user segmentation data and behavior analysis.

#### Insights Data
```
GET /api/insights
```
Returns opportunities, hypotheses, and pain points.

#### Ingest Reviews
```
POST /api/ingest
```
Triggers background data ingestion process to fetch new reviews from sources.

## Data Visualization

### Chart Library

The dashboard uses **Recharts** for data visualization:
- Bar charts for comparisons
- Line charts for trends
- Pie charts for distributions
- Scatter plots for relationships
- Area charts for time-series data

### Custom Components

- **StatCard**: Display key metrics with trends
- **FilterBar**: Interactive filtering controls
- **Modal**: Detailed information popups
- **AlertPanel**: Real-time alert notifications

## Real-time Updates

### Implementation

The dashboard uses polling for data updates to ensure compatibility and simplicity.

### Data Features

- On-demand data ingestion via ingestion button
- Background processing for ingestion tasks
- Metric updates on page refresh
- System status monitoring

## Performance Considerations

### Frontend Optimization

- Code splitting with React Router
- Lazy loading of components
- Responsive images
- Debounced search inputs

### Backend Optimization

- MongoDB connection pooling
- Response caching
- Pagination for large datasets
- Async processing for heavy operations

## Troubleshooting

### Frontend Issues

**Problem**: Dashboard not loading
- Ensure backend API is running
- Check API URL in `.env` file
- Verify CORS configuration

**Problem**: Charts not rendering
- Check browser console for errors
- Verify Recharts installation
- Ensure data format is correct

### Backend Issues

**Problem**: API not responding
- Check Flask server logs
- Verify MongoDB connection
- Check port availability

**Problem**: MongoDB connection failed
- Verify MongoDB is running
- Check connection string in `.env`
- Ensure database and collection exist

## Integration with Phase 4

Phase 5 reads insights from MongoDB collection populated by Phase 4:

```python
# Phase 4 writes to: spotify_reviews.insights
# Phase 5 reads from: spotify_reviews.ml_analyzed_reviews
```

To integrate:
1. Ensure Phase 4 has generated insights
2. Configure Phase 5 backend with same MongoDB connection
3. Start Phase 5 backend API
4. Start Phase 5 frontend dashboard
5. Dashboard displays insights from Phase 4

## Future Enhancements

- [ ] Add WebSocket support for true real-time updates
- [ ] Implement user authentication and authorization
- [ ] Add data export functionality (CSV, PDF)
- [ ] Implement custom dashboard builder
- [ ] Add mobile app version
- [ ] Implement advanced filtering and drill-down
- [ ] Add collaborative features (comments, annotations)
- [ ] Implement alert configuration and notifications
- [ ] Add A/B test integration
- [ ] Implement dashboard sharing and embedding
- [ ] Add more sophisticated ML analysis integration
- [ ] Implement automated sentiment and topic analysis

## Development

### Adding a New Page

1. Create a new page component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation item in `src/components/Layout.jsx`
4. Create corresponding API endpoint in `backend/app.py`

### Adding a New Chart

1. Import chart components from Recharts
2. Prepare data in the required format
3. Configure chart properties (axes, tooltips, legends)
4. Add responsive container for mobile compatibility

### Testing

Run tests (when implemented):

```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest
```

## Contributing

When contributing to Phase 5:

1. Follow the existing code style
2. Add appropriate error handling
3. Update documentation
4. Test on different screen sizes
5. Ensure accessibility compliance
6. Add configuration options for new features

## License

This project is part of the Spotify Reviews Analysis Engine.

## Contact

For questions or issues related to Phase 5, please refer to the main project documentation.
