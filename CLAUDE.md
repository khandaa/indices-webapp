# CLAUDE.md - AI Assistant Context

> This document provides essential context for AI assistants working with the Indices Web Application codebase.

## Project Overview

**Indices Web Application** is a full-stack financial indices tracking system that provides real-time monitoring, momentum analysis, and investment recommendations based on market indices performance.

### Tech Stack
- **Backend**: FastAPI (Python 3.8+) with SQLite database
- **Frontend**: React 19 with TypeScript, Tailwind CSS
- **Data**: Yahoo Finance API (yfinance) for market data
- **Database**: SQLite with SQLAlchemy ORM

### Project Structure
```
indices-webapp/
├── backend/
│   ├── api/                         # FastAPI application
│   │   ├── main.py                 # API endpoints and server
│   │   └── requirements.txt        # API-specific dependencies
│   ├── data_calculator.py          # Daily/weekly/monthly performance calculations
│   ├── momentum_calculator.py      # 3W/3M cumulative return calculations
│   ├── data_loader.py              # Yahoo Finance data fetching
│   ├── setup_database.py           # Database initialization
│   ├── weekly_change_calculator.py # Weekly metrics computation
│   ├── monthly_change_calculator.py # Monthly metrics computation
│   ├── yearly_change_calculator.py # Yearly metrics computation
│   └── advanced_operations.py      # Advanced data operations
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable React components
│   │   ├── pages/                  # Page-level components
│   │   │   ├── IndicesPage.tsx    # Main indices table
│   │   │   ├── InstrumentDetail.tsx # Detailed index view
│   │   │   ├── WeeklyDashboard.tsx # Weekly performance dashboard
│   │   │   ├── MonthlyDashboard.tsx # Monthly performance dashboard
│   │   │   └── Recommendations.tsx  # Investment recommendations
│   │   ├── services/               # API service layer
│   │   └── types/                  # TypeScript type definitions
│   ├── public/                     # Static assets
│   └── package.json                # Frontend dependencies
├── database/                        # SQLite database files
├── docs/                           # Documentation
├── logs/                           # Application logs
├── venv/                           # Python virtual environment
├── run.sh                          # Application runner script
└── requirements.txt                # Root-level Python dependencies
```

## Quick Start Commands

### Run the Entire Application
```bash
./run.sh                # Start both backend and frontend
./run.sh setup          # Run setup only
./run.sh status         # Check service status
./run.sh stop           # Stop all services
```

### Backend (Port 5050)
```bash
source venv/bin/activate
cd backend/api
python main.py
```

### Frontend (Port 3050)
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
cd backend
python setup_database.py
```

## Database Schema

### Key Tables
1. **indices_master**: Index metadata (id, symbol, name, exchange)
2. **index_data**: Daily OHLCV data
3. **index_calculated_data**: Performance metrics (1D/1W/1M/1Y returns)
4. **index_momentum_data**: Momentum metrics (3W/3M cumulative returns)
5. **user_settings**: User preferences and column configurations

## API Endpoints

### Core Endpoints
- `GET /api/indices` - All indices with performance data
- `GET /api/indices/{id}` - Specific index details
- `GET /api/indices/{id}/daily-prices` - Daily price history
- `GET /api/performance/weekly` - Top weekly performers
- `GET /api/performance/monthly` - Top monthly performers
- `GET /api/recommendations/weekly` - Weekly investment recommendations
- `GET /api/recommendations/monthly` - Monthly investment recommendations
- `GET /api/momentum/{id}` - Momentum metrics for specific index
- `POST /api/momentum/calculate` - Calculate momentum for all indices
- `GET /api/health` - Health check
- `GET /docs` - Swagger API documentation

### CORS Configuration
Backend allows requests from `http://localhost:3050` (frontend)

## Key Features

### 1. Real-time Index Tracking
- Fetches current prices and performance metrics
- Sortable, configurable columns
- Click-through to detailed views

### 2. Momentum Analysis
- **3-Week Momentum**: Cumulative return over 3 weeks
- **3-Month Momentum**: Cumulative return over 3 months
- Used for investment recommendations

### 3. Performance Dashboards
- **Weekly Dashboard**: Top 3 weekly performers
- **Monthly Dashboard**: Top 3 monthly performers
- Visual cards with metrics

### 4. Recommendations Engine
- Sorted by momentum metrics
- Weekly and monthly tabs
- Shows 1W, 1M returns alongside 3W, 3M cumulative returns

### 5. Instrument Details
- Daily price history table
- OHLCV data
- Performance metrics
- Volume analysis

## Important Code Patterns

### Backend
- **FastAPI with SQLAlchemy**: Standard ORM patterns
- **CORS enabled**: Required for frontend communication
- **Logging**: Uses Python logging module
- **Error Handling**: Try-except blocks with appropriate HTTP status codes

### Frontend
- **TypeScript**: Strict typing enabled
- **React Router**: For navigation between pages
- **Axios**: For API calls
- **Local Storage**: Saves column preferences
- **Error Boundaries**: Comprehensive error handling
- **Loading States**: User feedback during data fetches
- **Tailwind CSS**: Utility-first styling

## Data Flow

1. **Data Loading**: `data_loader.py` fetches from Yahoo Finance
2. **Calculation**: Performance calculators process raw data
3. **Storage**: SQLite database stores all metrics
4. **API**: FastAPI serves data to frontend
5. **Display**: React components render interactive UI

## Common Tasks

### Adding a New Index
1. Add entry to `indices_master` table
2. Run data loader to fetch historical data
3. Run calculators to compute metrics
4. Frontend automatically displays new index

### Adding a New Column
1. Backend: Add field to database schema
2. Backend: Update API response models
3. Frontend: Update TypeScript types
4. Frontend: Add column to table configuration

### Adding a New Endpoint
1. Add route in `backend/api/main.py`
2. Create service function if needed
3. Frontend: Add API call in services
4. Frontend: Update components to use new endpoint

## Configuration

### Backend
- **Port**: 5050 (configurable in `main.py`)
- **Database**: `backend/database/indices.db`
- **CORS Origin**: `http://localhost:3050`

### Frontend
- **Port**: 3050 (default React port configuration)
- **API URL**: `http://localhost:5050` (hardcoded in services)
- **Column Preferences**: Saved in browser localStorage

## Dependencies

### Backend (Python)
- fastapi>=0.68.0
- uvicorn>=0.15.0
- pandas>=1.5.0
- yfinance>=0.2.0
- sqlalchemy
- pydantic>=1.8.0

### Frontend (Node.js)
- react: ^19.2.4
- react-router-dom: ^7.13.2
- axios: ^1.14.0
- typescript: ^4.9.5
- tailwindcss: ^3.4.19

## Troubleshooting

### Backend Issues
- **Port conflict**: Use `lsof -i :5050` and kill process
- **Database errors**: Re-run `setup_database.py`
- **Import errors**: Ensure venv is activated and dependencies installed

### Frontend Issues
- **Port conflict**: Use `lsof -i :3050` and kill process
- **API errors**: Verify backend is running and URL is correct
- **Build errors**: Clear `node_modules` and reinstall

## Testing

### Backend
```bash
# No automated tests currently implemented
# Manual testing via Swagger UI at /docs
```

### Frontend
```bash
cd frontend
npm test
```

## Git Information

### Current Branch
- Main branch: `main`

### Recent Commits
- `b9456c0`: working version of the application
- `a1dbbe4`: frontend created
- `21ce29a`: backend created
- `773f56c`: created db scripts to get indices data

## Modified Files (Current Session)
- frontend/src/pages/IndicesPage.tsx
- frontend/src/pages/InstrumentDetail.tsx
- frontend/src/pages/MonthlyDashboard.tsx
- frontend/src/pages/Recommendations.tsx
- frontend/src/pages/WeeklyDashboard.tsx
- logs/data_calculation.log

## Best Practices

### When Making Changes
1. **Backend changes**: Always restart the server
2. **Frontend changes**: Hot reload should work automatically
3. **Database changes**: Re-run setup script or migration
4. **Dependencies**: Update requirements.txt or package.json

### Code Style
- **Python**: Follow PEP 8
- **TypeScript/React**: Follow React best practices
- **Comments**: Add docstrings for functions
- **Error Handling**: Always handle exceptions gracefully

### Performance Considerations
- **Large datasets**: Use pagination for API responses
- **Caching**: Consider caching frequently accessed data
- **Database queries**: Use appropriate indexes
- **Frontend rendering**: Use React memoization where needed

## Known Issues/Limitations
- No automated tests implemented yet
- No authentication/authorization system
- Single-user application (no multi-user support)
- Limited error recovery mechanisms
- No data validation on frontend inputs
- No real-time WebSocket updates (manual refresh required)

## Future Enhancements
- Add automated testing suite
- Implement WebSocket for real-time updates
- Add user authentication
- Enhanced charting capabilities
- Export data to CSV/Excel
- Alerts and notifications
- Portfolio tracking
- Multi-currency support

## Contact & Support
- Check `README.md` for detailed setup instructions
- API documentation: `http://localhost:5050/docs`
- See `docs/` folder for additional documentation

---

**Last Updated**: 2026-03-29
**Version**: 1.0.0
