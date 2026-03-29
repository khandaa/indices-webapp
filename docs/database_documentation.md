# Database Documentation

## Overview
This database system manages financial indices data for the Indices Web Application. It stores historical price data, calculated performance metrics, and user settings.

## Database Schema

### Tables

#### 1. indices_master
Stores master information about all supported indices.

**Columns:**
- `id` (INTEGER PRIMARY KEY): Unique identifier for each index
- `name` (TEXT): Full name of the index
- `symbol` (TEXT UNIQUE): Trading symbol (e.g., 'NIFTYBEES')
- `index_type` (TEXT): Type of index (precious_metal, nifty, sector, thematic, liquid_fund, smallcap, midcap, largecap)
- `description` (TEXT): Brief description of the index
- `is_active` (BOOLEAN): Flag to indicate if the index is active (1 = active, 0 = inactive)

**Constraints:**
- `index_type` must be one of the predefined values
- `symbol` must be unique

#### 2. index_data
Stores historical price data for each index.

**Columns:**
- `id` (INTEGER PRIMARY KEY): Unique identifier for each record
- `index_id` (INTEGER): Foreign key referencing indices_master.id
- `date` (TEXT): Date of the price data (YYYY-MM-DD format)
- `open_price` (REAL): Opening price
- `close_price` (REAL): Closing price
- `high_price` (REAL): Highest price
- `low_price` (REAL): Lowest price
- `volume` (INTEGER): Trading volume
- `upload_date` (TEXT): Timestamp when data was uploaded

**Constraints:**
- `index_id` must exist in indices_master table
- Combination of `index_id` and `date` must be unique

#### 3. index_calculated_data
Stores calculated performance metrics for each index.

**Columns:**
- `id` (INTEGER PRIMARY KEY): Unique identifier for each record
- `index_id` (INTEGER): Foreign key referencing indices_master.id
- `calculation_date` (TEXT): Date for which metrics are calculated (YYYY-MM-DD format)
- `daily_change` (REAL): Daily price change
- `weekly_change` (REAL): Weekly price change
- `monthly_change` (REAL): Monthly price change
- `yearly_change` (REAL): Yearly price change
- `daily_change_percent` (REAL): Daily percentage change
- `weekly_change_percent` (REAL): Weekly percentage change
- `monthly_change_percent` (REAL): Monthly percentage change
- `yearly_change_percent` (REAL): Yearly percentage change

**Constraints:**
- `index_id` must exist in indices_master table
- Combination of `index_id` and `calculation_date` must be unique

#### 4. user_settings
Stores user preferences and settings.

**Columns:**
- `id` (INTEGER PRIMARY KEY): Unique identifier for each user
- `user_id` (TEXT UNIQUE): Unique user identifier
- `refresh_interval` (INTEGER): Data refresh interval in seconds (default: 300)
- `theme` (TEXT): UI theme preference (default: 'light')
- `language` (TEXT): Language preference (default: 'en')

**Constraints:**
- `user_id` must be unique

## Supported Indices

### Precious Metal ETFs
- **SILVERBEES**: Silver BeES
- **GOLDBEES**: Gold BeES

### Nifty ETFs
- **NIFTYBEES**: Nifty BeES
- **MONIFTY500**: Motilal Oswal Nifty 500
- **MOMENTUM50**: Nifty Momentum 50

### Sector ETFs
- **ITBEES**: Nifty IT BeES
- **BANKBEES**: Nifty Bank BeES
- **PSUBNKBEES**: Nifty PSU Bank BeES
- **AUTOBEES**: Nifty Auto BeES
- **JUNIORBEES**: Nifty Junior BeES
- **PHARMABEES**: Nifty Pharma BeES
- **FMCGIETF**: Nifty FMCG ETF
- **MID150BEES**: Nifty Midcap 150 BeES
- **OILIETF**: Nifty Oil & Gas ETF
- **ALPHA**: Nifty Alpha 50
- **INFRABEES**: Nifty Infra BeES
- **NEXT50IETF**: Nifty Next 50 ETF
- **HEALTHIETF**: Nifty Healthcare ETF
- **SMALLCAP**: Nifty Smallcap 250

### Thematic ETFs
- **AONETOTAL**: Nifty Total Market
- **MOMOMENTUM**: Nifty Momentum
- **MONQ50**: Nifty Quality Midcap 50
- **HDFCVALUE**: HDFC Value Fund
- **HDFCGROWTH**: HDFC Growth Fund
- **HDFCMOMENT**: HDFC Momentum Fund
- **MODEFENCE**: Motilal Oswal MSCI EAFE Fund
- **EVINDIA**: Nifty EV & New Age Automotive
- **CONSUMIETF**: Nifty Consumption ETF
- **GROWWRAIL**: Nifty India Railways
- **SELECTIPO**: Nifty IPO ETF

### Liquid Fund
- **LIQUIDBEES**: Liquid BeES

## Scripts Usage

### 1. setup_database.py
**Purpose**: Creates database tables and inserts initial data.

**Usage:**
```bash
python setup_database.py
```

**What it does:**
- Creates database folder and SQLite database file
- Creates all required tables with proper constraints
- Inserts all supported indices into indices_master table
- Creates performance indexes
- Logs all operations

### 2. data_loader.py
**Purpose**: Downloads historical data from yfinance and stores it in the database.

**Usage:**
```bash
python data_loader.py
```

**Features:**
- Downloads data for all active indices from yfinance
- Handles missing data gracefully
- Supports date range filtering
- Logs all operations
- Uses INSERT OR REPLACE to handle duplicates

**Advanced Usage:**
```python
from data_loader import DataLoader

loader = DataLoader()
loader.connect()

# Load data for specific indices
loader.load_data_for_specific_indices(['NIFTYBEES', 'GOLDBEES'])

# Load data for specific date range
loader.load_data_for_all_indices('2026-01-01', '2026-03-29')

loader.disconnect()
```

### 3. data_calculator.py
**Purpose**: Calculates performance metrics for all indices.

**Usage:**
```bash
python data_calculator.py
```

**Features:**
- Calculates daily, weekly, monthly, and yearly changes
- Calculates percentage changes
- Handles missing data gracefully
- Supports date range filtering
- Logs all operations

**Advanced Usage:**
```python
from data_calculator import DataCalculator

calculator = DataCalculator()
calculator.connect()

# Calculate for specific indices
calculator.calculate_for_specific_indices(['NIFTYBEES', 'GOLDBEES'])

# Calculate for specific date range
calculator.calculate_for_all_indices('2026-01-01', '2026-03-29')

calculator.disconnect()
```

### 4. advanced_operations.py
**Purpose**: Provides advanced functionality for flexible data management.

**Usage:**
```bash
python advanced_operations.py
```

**Features:**
- Load data for specific date ranges
- Calculate metrics for specific date ranges
- Get data summaries
- Validate data integrity
- Combined load and calculate operations

**Advanced Usage:**
```python
from advanced_operations import AdvancedOperations

ops = AdvancedOperations()

# Load and calculate for specific date range
ops.load_and_calculate_for_date_range('2026-01-01', '2026-03-29', ['NIFTYBEES'])

# Get data summary
summary = ops.get_data_summary('NIFTYBEES')

# Validate data integrity
validation = ops.validate_data_integrity()
```

## Database Performance

### Indexes
The following indexes are created for optimal performance:
- `idx_index_data_index_id`: On index_data.index_id
- `idx_index_data_date`: On index_data.date
- `idx_index_data_index_date`: Composite index on (index_id, date)
- `idx_calculated_data_index_id`: On index_calculated_data.index_id
- `idx_calculated_data_date`: On index_calculated_data.calculation_date
- `idx_calculated_data_index_date`: Composite index on (index_id, calculation_date)
- `idx_indices_master_symbol`: On indices_master.symbol
- `idx_indices_master_type`: On indices_master.index_type

### Data Validation
The system includes comprehensive data validation:
- Checks for indices without data
- Identifies data gaps
- Validates data integrity
- Reports issues and statistics

## Error Handling

All scripts include comprehensive error handling:
- Database connection errors
- Data download errors
- Calculation errors
- Data insertion errors
- Logging of all operations

## Dependencies

- **Python 3.7+**
- **yfinance**: For downloading financial data
- **pandas**: For data manipulation and calculations
- **sqlite3**: For database operations (built-in)

## Logging

All scripts use Python's logging module with:
- File logging (separate log files for each script)
- Console logging
- Timestamped log entries
- Different log levels (INFO, ERROR, WARNING)

## Data Sources

- **Primary**: Yahoo Finance via yfinance library
- **Data Format**: Daily OHLCV data (Open, High, Low, Close, Volume)
- **Update Frequency**: Can be configured per user requirements

## Security Considerations

- Database file should have appropriate permissions
- Connection strings should be secured
- Error logs should not contain sensitive information
- User data should be anonymized where possible

## Backup and Recovery

- Regular database backups recommended
- Export functionality available through scripts
- Data validation helps detect corruption
- Transaction logging for recovery

## Future Enhancements

- Support for real-time data feeds
- Additional calculation metrics
- Data visualization tools
- API endpoints for external access
- Automated data refresh scheduling
