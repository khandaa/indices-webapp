# YFinance Data Fetcher

This system fetches daily price data from Yahoo Finance and stores it in the `index_data` table. It intelligently checks for existing data and only fetches missing data.

## Features

- **Smart Data Fetching**: Only fetches data that doesn't already exist in the database
- **Bulk Operations**: Can fetch data for all indices or single index
- **Rate Limiting**: Built-in delays to avoid overwhelming Yahoo Finance API
- **Data Validation**: Handles missing data and API errors gracefully
- **Progress Tracking**: Shows detailed progress during fetch operations
- **Status Reporting**: Comprehensive status view of data coverage

## Files

- `fetch_yfinance_data.py` - Main data fetching script
- `setup_yfinance.sh` - Setup script for dependencies
- `requirements_yfinance.txt` - Python dependencies

## Installation

1. **Install dependencies:**
   ```bash
   cd scripts
   ./setup_yfinance.sh
   ```

2. **Or install manually:**
   ```bash
   cd scripts
   pip install -r requirements_yfinance.txt
   ```

## Usage

### Fetch All Indices Data
Fetch data for all indices in `indices_master` table:
```bash
python fetch_yfinance_data.py all

# Fetch from specific start date
python fetch_yfinance_data.py all 2023-01-01
```

### Fetch Single Index
Fetch data for a specific index:
```bash
python fetch_yfinance_data.py single NIFTYBEES

# Fetch from specific start date
python fetch_yfinance_data.py single RELIANCE 2024-01-01
```

### Check Data Status
View current data coverage for all indices:
```bash
python fetch_yfinance_data.py status
```

## Database Schema

### indices_master Table
The script will automatically add a `yfinance_symbol` column if it doesn't exist:

```sql
ALTER TABLE indices_master ADD COLUMN yfinance_symbol TEXT
```

### index_data Table
Creates the following table structure:

```sql
CREATE TABLE index_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    index_id INTEGER NOT NULL,
    open_price REAL NOT NULL,
    high_price REAL NOT NULL,
    low_price REAL NOT NULL,
    close_price REAL NOT NULL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (index_id) REFERENCES indices_master (id),
    UNIQUE(date, index_id)
)
```

## Algorithm

### Data Fetching Logic

1. **Check Existing Data**: 
   - Queries `index_data` table for latest date per index
   - Determines start date for new data fetch

2. **Determine Fetch Range**:
   - If data exists: Fetch from day after latest date
   - If no data: Fetch from default start date (1 year ago) or specified date

3. **Fetch from YFinance**:
   - Uses `yfinance` library with proper symbol mapping
   - Handles Indian stocks with `.NS` suffix
   - Implements rate limiting (0.5s delay between requests)

4. **Data Processing**:
   - Converts to standard format
   - Handles missing data gracefully
   - Validates price data integrity

5. **Database Storage**:
   - Uses `INSERT OR REPLACE` for idempotent operations
   - Maintains data consistency
   - Provides detailed logging

### Symbol Mapping

The script automatically maps symbols to Yahoo Finance format:

- **Default**: Adds `.NS` suffix for Indian stocks
- **Custom**: Uses `yfinance_symbol` column if specified
- **Fallback**: Uses original `symbol` column

## Examples

### Initial Setup
```bash
# Install dependencies
cd scripts
./setup_yfinance.sh

# Check current status
python fetch_yfinance_data.py status

# Fetch all data from last year
python fetch_yfinance_data.py all 2023-01-01
```

### Daily Updates
```bash
# Fetch latest data for all indices
python fetch_yfinance_data.py all

# Update specific index
python fetch_yfinance_data.py single NIFTYBEES
```

### Historical Backfill
```bash
# Fetch 5 years of historical data
python fetch_yfinance_data.py all 2019-01-01

# Fill gaps for specific index
python fetch_yfinance_data.py single RELIANCE 2020-01-01
```

## Error Handling

- **API Errors**: Gracefully handles Yahoo Finance API failures
- **Data Validation**: Skips invalid or incomplete data
- **Database Errors**: Proper transaction handling and rollback
- **Rate Limiting**: Prevents API blocking with delays

## Performance Considerations

- **Batch Processing**: Efficient bulk database operations
- **Memory Management**: Processes data in chunks
- **Rate Limiting**: 0.5s delay between API calls
- **Incremental Updates**: Only fetches missing data

## Troubleshooting

### Common Issues

1. **"No data found for symbol"**
   - Check if symbol exists in `indices_master`
   - Verify `yfinance_symbol` mapping
   - Ensure symbol is valid on Yahoo Finance

2. **"Index not found in indices_master"**
   - Add index to `indices_master` table first
   - Check symbol spelling

3. **API Rate Limits**
   - Script includes built-in delays
   - For bulk operations, consider running during off-peak hours

### Debug Mode

For detailed debugging, modify the script to enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Automation

### Cron Job Setup
Set up daily data fetching:

```bash
# Edit crontab
crontab -e

# Add daily fetch at 6:00 PM
0 18 * * * cd /path/to/indices-webapp/scripts && python fetch_yfinance_data.py all
```

### Integration with Main Application
The fetched data integrates seamlessly with:
- **Frontend**: Daily price display and charts
- **API**: Price history endpoints
- **Recommendations**: Historical return calculations
- **Analytics**: Performance metrics

## Data Quality

- **Source**: Yahoo Finance (real-time market data)
- **Frequency**: Daily price data
- **Fields**: Open, High, Low, Close, Volume
- **Currency**: Local currency (INR for Indian indices)
- **Adjustments**: Price splits and dividends handled by yfinance
