# Indices Web Application

A comprehensive web application for tracking and analyzing financial indices performance with momentum-based investment recommendations.

## 🚀 Features

### Core Functionality
- **Real-time Index Tracking**: Monitor multiple financial indices with current prices and performance metrics
- **Momentum Analysis**: 3-week and 3-month cumulative return calculations for trend analysis
- **Interactive Dashboards**: Weekly and monthly performance dashboards with top performers
- **Investment Recommendations**: Data-driven recommendation system with sorting by momentum metrics
- **Detailed Instrument Views**: Daily price history with comprehensive metrics

### Key Features
- 📊 **Main Indices Table**: Sortable, configurable columns with real-time data
- 📈 **Performance Dashboards**: Visual representations of weekly and monthly top performers
- 🎯 **Recommendations Engine**: Weekly and monthly investment recommendations based on momentum
- 🔍 **Instrument Details**: Click any index to view detailed daily price history
- 📱 **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- ⚡ **Real-time Updates**: Manual refresh capabilities with loading states
- 🛡️ **Error Handling**: Comprehensive error boundaries and user feedback

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python
- **Database**: SQLite with SQLAlchemy ORM
- **APIs**: RESTful endpoints for indices, performance data, and recommendations
- **Data Processing**: Automated momentum calculations and performance metrics

### Frontend (React)
- **Framework**: React 18+ with TypeScript
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS for modern UI
- **State Management**: React hooks and local storage
- **HTTP Client**: Axios for API communication

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **npm**: 8.0 or higher (comes with Node.js)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd indices-webapp
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Setup Database
```bash
# Navigate to backend directory
cd backend

# Run database setup script
python setup_database.py
```

#### Start Backend Server
```bash
# Navigate to backend API directory
cd api

# Start the FastAPI server
python main.py
```

The backend will start on `http://localhost:5050`

### 3. Frontend Setup

#### Install Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install
```

#### Environment Configuration
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:5050
```

#### Start Frontend Development Server
```bash
npm start
```

The frontend will start on `http://localhost:3000`

## 📊 Database Schema

### Tables
- **indices_master**: Index information and metadata
- **index_data**: Daily price data (OHLCV)
- **index_calculated_data**: Performance metrics (daily, weekly, monthly, yearly changes)
- **index_momentum_data**: Momentum metrics (3W, 3M cumulative returns)
- **user_settings**: User preferences and configurations

## 🚀 Running the Application

### Method 1: Development Mode (Recommended for Development)

1. **Start Backend**:
   ```bash
   # Activate virtual environment
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   
   # Start backend server
   cd backend/api
   python main.py
   ```

2. **Start Frontend** (in separate terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5050
   - API Documentation: http://localhost:5050/docs

### Method 2: Production Mode

1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Start Backend with Static Files**:
   ```bash
   cd backend/api
   python main.py
   ```

## 📡 API Endpoints

### Indices
- `GET /api/indices` - Get all indices with performance data
- `GET /api/indices/{id}` - Get specific index details
- `GET /api/indices/{id}/daily-prices` - Get daily price history

### Performance
- `GET /api/performance/weekly` - Get weekly top performers
- `GET /api/performance/monthly` - Get monthly top performers

### Recommendations
- `GET /api/recommendations/weekly` - Get weekly recommendations
- `GET /api/recommendations/monthly` - Get monthly recommendations

### Momentum
- `GET /api/momentum/{id}` - Get momentum metrics for specific index
- `POST /api/momentum/calculate` - Calculate momentum for all indices

### System
- `GET /api/health` - Health check
- `GET /docs` - API documentation (Swagger UI)

## 🎯 Usage Guide

### Main Indices Page
1. **View All Indices**: Comprehensive table with all available indices
2. **Configure Columns**: Use the column configuration panel to show/hide columns
3. **Sort Data**: Click any column header to sort ascending/descending
4. **Click Index**: Click any index name to view detailed information

### Performance Dashboards
1. **Weekly Dashboard**: View top 3 weekly performers with detailed metrics
2. **Monthly Dashboard**: View top 3 monthly performers with trend analysis
3. **Refresh Data**: Use the refresh button to update data

### Recommendations
1. **Weekly Tab**: View weekly investment recommendations sorted by 3W momentum
2. **Monthly Tab**: View monthly investment recommendations sorted by 3M momentum
3. **Analyze Metrics**: Review 1W/1M returns alongside 3W/3M cumulative returns

### Instrument Details
1. **Daily Price Table**: View comprehensive daily price history
2. **Performance Metrics**: Analyze daily changes and momentum indicators
3. **Volume Analysis**: Review trading volumes and price movements

## 🔧 Configuration

### Backend Configuration
- **Database Path**: Configured in `backend/api/main.py`
- **CORS Settings**: Allow frontend origin (localhost:3000)
- **API Port**: Default 5050 (configurable)

### Frontend Configuration
- **API URL**: Set via `REACT_APP_API_URL` environment variable
- **Refresh Intervals**: Configurable in component settings
- **Column Preferences**: Saved in browser local storage

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues
1. **Port Already in Use**:
   ```bash
   # Find process using port 5050
   lsof -i :5050
   
   # Kill process
   kill -9 <PID>
   ```

2. **Database Connection Error**:
   - Ensure database setup script was run
   - Check database file permissions
   - Verify SQLite installation

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

#### Frontend Issues
1. **Port Already in Use**:
   ```bash
   # Kill process on port 3000
   lsof -i :3000
   kill -9 <PID>
   
   # Or use different port
   npm start -- --port=3001
   ```

2. **API Connection Error**:
   - Verify backend is running on correct port
   - Check `REACT_APP_API_URL` environment variable
   - Ensure CORS is properly configured

3. **Build Errors**:
   - Clear node_modules: `rm -rf node_modules`
   - Reinstall dependencies: `npm install`
   - Check TypeScript compilation

### Debug Mode
- **Frontend**: Open browser developer tools
- **Backend**: Check terminal logs and API responses
- **Network**: Use browser Network tab to inspect API calls

## 📝 Development Notes

### Code Structure
```
indices-webapp/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── data_calculator.py  # Performance calculations
│   ├── momentum_calculator.py # Momentum metrics
│   └── setup_database.py  # Database initialization
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
└── database/              # SQLite database files
```

### Adding New Features
1. **Backend**: Add new endpoints in `backend/api/main.py`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Pages**: Add new pages in `frontend/src/pages/`
4. **Types**: Update TypeScript types in `frontend/src/types/`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review API documentation at `http://localhost:5050/docs`
- Open an issue in the repository

---

**Version**: 1.0.0  
**Last Updated**: 2025-03-29
