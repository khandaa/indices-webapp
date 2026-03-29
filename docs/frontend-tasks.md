# Frontend Development Tasks

## Overview
This document outlines all tasks needed to build the frontend for the Indices Web Application using React and FastAPI backend.

## Backend API Development

### Database Connection & Setup
- [x] Set up FastAPI backend structure
- [x] Create database connection utilities for SQLite
- [x] Configure CORS for React frontend communication
- [x] Set up API server to run on port 5050

### Core API Endpoints
- [x] Create `/api/indices` endpoint to fetch all indices with current data
- [x] Create `/api/indices/{index_id}` endpoint for individual index details
- [x] Create `/api/performance/weekly` endpoint for weekly top performers
- [x] Create `/api/performance/monthly` endpoint for monthly top performers
- [ ] Create `/api/momentum/{index_id}` endpoint for momentum metrics

### Data Processing APIs
- [ ] Implement calculation logic for 3W cumulative return
- [ ] Implement calculation logic for 3M cumulative return
- [ ] Create API endpoints for momentum metrics
- [ ] Add pagination support for large datasets

## Frontend React Application

### Project Setup & Configuration
- [x] Initialize React project with TypeScript
- [x] Set up project structure (components, pages, services, utils)
- [x] Configure routing with React Router
- [x] Set up Axios or Fetch API for backend communication
- [x] Configure environment variables for API endpoints

### Core Components Development
- [x] Create reusable DataTable component with sorting functionality
- [x] Create ColumnToggle component for show/hide columns
- [x] Create IndexCard component for displaying individual index data
- [x] Create LoadingSpinner component for async operations
- [x] Create ErrorMessage component for error handling

### Main Indices Page
- [x] Build main indices list page with data table
- [x] Implement sorting on all columns (price, daily, weekly, monthly, yearly changes)
- [x] Add column configuration panel at the top
- [x] Implement enable/disable functionality for each column
- [x] Add real-time data refresh capability
- [x] Add manual refresh button

### Column Configuration System
- [x] Create column configuration state management
- [x] Implement local storage for user preferences
- [x] Add checkboxes for each column toggle
- [x] Create preset column configurations (basic, detailed, momentum)
- [x] Add "Reset to Default" option

### Momentum Metrics Integration
- [x] Add 3W (3-week) cumulative return column
- [x] Add 3M (3-month) cumulative return column
- [x] Implement momentum calculation logic
- [x] Add visual indicators for momentum (up/down arrows, colors)
- [ ] Create momentum trend visualization

### Dashboard Pages

#### Weekly Dashboard
- [x] Create weekly performance dashboard page
- [x] Implement top 3 weekly indices display
- [x] Add sorting by 3W cumulative return
- [ ] Create visual charts for weekly performance
- [x] Add weekly performance summary statistics

#### Monthly Dashboard
- [x] Create monthly performance dashboard page
- [x] Implement top 3 monthly indices display
- [x] Add sorting by 3M cumulative return
- [ ] Create visual charts for monthly performance
- [x] Add monthly performance summary statistics


### Performance & Optimization
- [x] Add error boundaries for better error handling

### Configuration & Settings
- [ ] Create settings page for user preferences
- [ ] Add auto-refresh interval configuration
- [ ] Add export functionality (CSV, Excel)

### Deployment & Documentation
- [ ] Configure production build process
- [ ] Set up environment-specific configurations

## Technical Specifications

### API Response Format
```json
{
  "indices": [
    {
      "id": 1,
      "name": "Nifty 50 BeES",
      "symbol": "NIFTYBEES",
      "current_price": 245.67,
      "daily_change": 2.34,
      "weekly_change": 5.67,
      "monthly_change": 12.45,
      "yearly_change": 18.92,
      "3w_cumulative_return": 8.45,
      "3m_cumulative_return": 15.23
    }
  ]
}
```

### Column Configuration Object
```json
{
  "columns": {
    "name": true,
    "symbol": true,
    "current_price": true,
    "daily_change": true,
    "weekly_change": true,
    "monthly_change": true,
    "yearly_change": true,
    "3w_cumulative_return": false,
    "3m_cumulative_return": false
  }
}
```


## Priority Levels

### High Priority (MVP)
1. Basic React setup and routing
2. Core API endpoints implementation
3. Main indices table with sorting
4. Column configuration functionality
5. Basic dashboard pages

### Medium Priority
1. Momentum metrics integration
2. Advanced visualizations
3. Performance optimizations
4. Settings and configuration


## Dependencies & Technologies

### Frontend
- React 18+ with TypeScript
- React Router for navigation
- Axios for API calls
- Chart.js or Recharts for visualizations
- Tailwind CSS for styling
- React Query for data fetching

### Backend
- FastAPI for REST APIs
- SQLAlchemy for database ORM
- SQLite for database
- Pydantic for data validation
- Uvicorn for server

### Development Tools
- ESLint and Prettier for code formatting
- Jest for testing
- Webpack/Vite for bundling


## Success Criteria
- [x] All indices displayed with accurate data
- [x] Sorting works on all columns
- [x] Column configuration persists across sessions
- [x] Dashboard shows correct top performers
- [x] Application loads quickly and is responsive
- [x] APIs are well-documented and reliable
- [x] Code is maintainable and well-tested
- [x] Momentum metrics are calculated and displayed
- [x] Error boundaries provide better error handling
- [x] Navigation between pages works correctly
