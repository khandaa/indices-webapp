# AGENTS.md - Development Guide for AI Assistants

## Project Overview

**Indices Web Application** is a full-stack financial indices tracking system that provides real-time monitoring, momentum analysis, and investment recommendations based on market indices performance.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with direct sqlite3 connections
- **Data Source**: Yahoo Finance (yfinance library)
- **Dependencies**: pandas, fastapi, uvicorn, pydantic

### Frontend
- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Package Manager**: npm

## Application Architecture

```
indices-webapp/
├── backend/                         # FastAPI backend
│   ├── api/
│   │   ├── main.py                 # API endpoints & server
│   │   └── requirements.txt        # Backend dependencies
│   ├── setup_database.py           # Database initialization
│   ├── data_loader.py              # Yahoo Finance data fetching
│   ├── data_calculator.py         # Performance calculations
│   ├── momentum_calculator.py     # Momentum metrics (3W/3M)
│   ├── weekly_change_calculator.py
│   ├── monthly_change_calculator.py
│   ├── yearly_change_calculator.py
│   └── advanced_operations.py     # Flexible data operations
├── frontend/                        # React frontend
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                # Page-level components
│   │   │   ├── IndicesPage.tsx   # Main indices table
│   │   │   ├── InstrumentDetail.tsx
│   │   │   ├── WeeklyDashboard.tsx
│   │   │   ├── MonthlyDashboard.tsx
│   │   │   └── Recommendations.tsx
│   │   ├── services/              # API service layer
│   │   └── types/                # TypeScript definitions
│   └── package.json
├── database/                       # SQLite database
├── run.sh                          # Application runner script
└── venv/                          # Python virtual environment
```

## Database Schema

### Tables

1. **indices_master** - Index metadata
   - `id` INTEGER PRIMARY KEY
   - `name` TEXT NOT NULL
   - `symbol` TEXT UNIQUE
   - `index_type` TEXT (precious_metal, nifty, sector, thematic, liquid_fund, smallcap, midcap, largecap)
   - `description` TEXT
   - `is_active` BOOLEAN DEFAULT 1

2. **index_data** - Daily OHLCV price data
   - `id` INTEGER PRIMARY KEY
   - `index_id` INTEGER FOREIGN KEY
   - `date` TEXT (YYYY-MM-DD)
   - `open_price`, `close_price`, `high_price`, `low_price` REAL
   - `volume` INTEGER
   - `upload_date` TEXT

3. **index_calculated_data** - Performance metrics
   - `id` INTEGER PRIMARY KEY
   - `index_id` INTEGER FOREIGN KEY
   - `calculation_date` TEXT
   - `daily_change`, `weekly_change`, `monthly_change`, `yearly_change` REAL
   - `daily_change_percent`, `weekly_change_percent`, `monthly_change_percent`, `yearly_change_percent` REAL

4. **index_momentum_data** - Momentum metrics
   - `id` INTEGER PRIMARY KEY
   - `index_id` INTEGER FOREIGN KEY
   - `calculation_date` TEXT
   - `three_week_cumulative_return` REAL
   - `three_month_cumulative_return` REAL

5. **user_settings** - User preferences
   - `id` INTEGER PRIMARY KEY
   - `user_id` TEXT UNIQUE
   - `refresh_interval` INTEGER DEFAULT 300
   - `theme` TEXT DEFAULT 'light'
   - `language` TEXT DEFAULT 'en'

### Supported Indices
- Precious Metals: SILVERBEES, GOLDBEES
- Nifty ETFs: NIFTYBEES, MONIFTY500, MOMENTUM50
- Sector ETFs: ITBEES, BANKBEES, PSUBNKBEES, AUTOBEES, JUNIORBEES, PHARMABEES, FMCGIETF, MID150BEES, OILIETF, ALPHA, INFRABEES, NEXT50IETF, HEALTHIETF, SMALLCAP
- Thematic ETFs: AONETOTAL, MOMOMENTUM, MONQ50, HDFCVALUE, HDFCGROWTH, HDFCMOMENT, MODEFENCE, EVINDIA, CONSUMIETF, GROWWRAIL, SELECTIPO
- Liquid Fund: LIQUIDBEES

## How to Start/Stop the Application

### Using run.sh (Recommended)

```bash
# Start application (both backend and frontend)
./run.sh

# Run setup only (install deps, setup database)
./run.sh setup

# Check service status
./run.sh status

# Stop all services
./run.sh stop
```

### Manual Start

**Backend:**
```bash
source venv/bin/activate
cd backend/api
python main.py
# Runs on http://localhost:5050
```

**Frontend:**
```bash
cd frontend
npm start
# Runs on http://localhost:3050
```

### Ports
- Backend API: 5050
- Frontend: 3050
- API Docs: http://localhost:5050/docs

## API Endpoints

- `GET /api/indices` - All indices with performance data
- `GET /api/indices/{id}` - Specific index details
- `GET /api/indices/{id}/daily-prices` - Daily price history
- `GET /api/performance/weekly` - Top weekly performers
- `GET /api/performance/monthly` - Top monthly performers
- `GET /api/recommendations/weekly` - Weekly recommendations
- `GET /api/recommendations/monthly` - Monthly recommendations
- `GET /api/momentum/{id}` - Momentum metrics
- `POST /api/momentum/calculate` - Calculate momentum
- `GET /api/health` - Health check
- `GET /docs` - Swagger documentation

## Data Pipeline

1. **Data Loading**: `data_loader.py` fetches from Yahoo Finance
2. **Calculation**: `data_calculator.py` computes performance metrics
3. **Momentum**: `momentum_calculator.py` computes 3W/3M cumulative returns
4. **Storage**: SQLite database
5. **API**: FastAPI serves to frontend

## Key Patterns

### Backend
- Uses direct sqlite3 connections (not SQLAlchemy)
- CORS enabled for localhost:3050
- Logging to `logs/` directory

### Frontend
- TypeScript strict typing
- Loading states for all API calls
- LocalStorage for column preferences

## Common Tasks

### Adding a new index
1. Add to `indices_master` in `setup_database.py`
2. Re-run setup_database.py
3. Run data_loader.py to fetch data
4. Run data_calculator.py to compute metrics

### Adding a new API endpoint
1. Add route in `backend/api/main.py`
2. Create service function if needed
3. Update frontend services/api.ts
4. Update TypeScript types if needed