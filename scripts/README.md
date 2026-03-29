# Recommendations Generation System

This system generates weekly and monthly investment recommendations based on historical price data and momentum analysis.

## Features

- **Weekly Recommendations**: Generated every Friday, Saturday, or Sunday for upcoming week
- **Monthly Recommendations**: Generated on first day or last day of each month for the month
- **Historical Data**: Uses 3 months of historical data for calculations
- **Ranking System**: Ranks indices by cumulative returns (3-week for weekly, 3-month for monthly)
- **Configurable Top Rankings**: Recommend top X indices (default: 3)
- **Automated Scheduling**: Cron jobs for automatic execution

## Files

- `generate_recommendations.py` - Main script for generating recommendations
- `setup_cron.sh` - Script to set up automated scheduling
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Database Schema

The script creates a `recommendations` table with the following structure:

```sql
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id TEXT UNIQUE NOT NULL,
    recommendation_date DATE NOT NULL,
    recommendation_month TEXT NOT NULL,
    recommendation_week TEXT,
    index_id INTEGER NOT NULL,
    index_name TEXT NOT NULL,
    index_symbol TEXT NOT NULL,
    weekly_return_percentage REAL,
    three_week_cumulative_return_percentage REAL,
    weekly_recommendation_rank INTEGER,
    monthly_return_percentage REAL,
    three_month_cumulative_return_percentage REAL,
    monthly_recommendation_rank INTEGER,
    recommendation_type TEXT NOT NULL, -- 'weekly' or 'monthly'
    last_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Installation

1. **Install Python dependencies:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

2. **Ensure database exists:**
   - Make sure the `database/index-database.db` file exists
   - Ensure it contains `indices_master` and `index_data` tables

3. **Make scripts executable:**
   ```bash
   chmod +x generate_recommendations.py
   chmod +x setup_cron.sh
   ```

## Usage

### Generate All Historical Data
Generate all recommendations from 01-Jan-2023 to present:
```bash
python3 generate_recommendations.py all
# or simply
python3 generate_recommendations.py
```

### Generate Current Week Recommendations
Run this on Friday, Saturday, or Sunday to generate recommendations for the upcoming week:
```bash
python3 generate_recommendations.py weekly
```

### Generate Current Month Recommendations
Run this on the first day or last day of a month to generate recommendations for the month:
```bash
python3 generate_recommendations.py monthly
```

### Generate with Custom Top Rankings
Specify the number of top recommendations to generate (default is 3):
```bash
# Generate top 5 recommendations
python3 generate_recommendations.py all 5

# Generate top 10 weekly recommendations
python3 generate_recommendations.py weekly 10

# Generate top 7 monthly recommendations
python3 generate_recommendations.py monthly 7
```

### Generate Recommendations for Specific Date Range
Generate recommendations for a specific date range and type:
```bash
# Generate weekly recommendations for January 2023
python3 generate_recommendations.py date-range 2023-01-01 2023-01-31 weekly

# Generate monthly recommendations for 2023
python3 generate_recommendations.py date-range 2023-01-01 2023-12-31 monthly

# Generate top 5 recommendations for specific date range
python3 generate_recommendations.py date-range 2023-01-01 2023-12-31 weekly 5
```

## Automated Scheduling

Set up cron jobs for automatic execution:

```bash
./setup_cron.sh
```

This will create the following cron jobs:
- **Weekly**: Every Friday, Saturday, and Sunday at 9:00 AM
- **Monthly**: First day and last day of every month at 9:00 AM

### Manual Cron Setup

If you prefer to set up cron jobs manually:

```bash
# Edit crontab
crontab -e

# Add these lines:
# Weekly recommendations - every Saturday at 9:00 AM
0 9 * * 6 cd /path/to/project && python3 scripts/generate_recommendations.py weekly >> logs/weekly_cron.log 2>&1

# Monthly recommendations - last day of every month at 9:00 AM
0 9 28-31 * * [ $(date +%m -d tomorrow) != $(date +%m) ] && cd /path/to/project && python3 scripts/generate_recommendations.py monthly >> logs/monthly_cron.log 2>&1
```

## Algorithm Details

### Weekly Recommendations
- **Run Time**: Every Saturday
- **Data Period**: Previous 3 months of price data
- **Ranking Criteria**: 3-week cumulative return (descending)
- **Output**: Top-ranked indices for the upcoming week

### Monthly Recommendations
- **Run Time**: Last day of each month
- **Data Period**: Previous 3 months of price data
- **Ranking Criteria**: 3-month cumulative return (descending)
- **Output**: Top-ranked indices for the upcoming month

### Return Calculations

- **Weekly Return**: Return over the last 7 days of available data
- **Monthly Return**: Return over the last 30 days of available data
- **3-Week Cumulative**: Return over the last 21 days of available data
- **3-Month Cumulative**: Return over the last 90 days of available data

## Logging

Logs are stored in the `logs/` directory:
- `weekly_cron.log` - Weekly recommendation execution logs
- `monthly_cron.log` - Monthly recommendation execution logs

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure `database/index-database.db` exists
   - Check file permissions

2. **Insufficient Historical Data**
   - Script requires at least 10 days of price data
   - Check if `index_data` table is populated

3. **Cron Job Not Running**
   - Check cron service status: `sudo systemctl status cron`
   - Verify cron job installation: `crontab -l`
   - Check log files for errors

### Debug Mode

Run the script manually to see detailed output:
```bash
python3 generate_recommendations.py all
```

### Database Queries

Check generated recommendations:
```sql
-- View recent weekly recommendations
SELECT * FROM recommendations 
WHERE recommendation_type = 'weekly' 
ORDER BY recommendation_date DESC 
LIMIT 10;

-- View recent monthly recommendations
SELECT * FROM recommendations 
WHERE recommendation_type = 'monthly' 
ORDER BY recommendation_date DESC 
LIMIT 10;

-- View top ranked weekly recommendations
SELECT index_symbol, weekly_recommendation_rank, three_week_cumulative_return_percentage
FROM recommendations 
WHERE recommendation_type = 'weekly' 
AND weekly_recommendation_rank <= 3
ORDER BY recommendation_date DESC, weekly_recommendation_rank;
```

## Maintenance

- **Monitor Logs**: Regularly check log files for errors
- **Database Backup**: Periodically backup the recommendations database
- **Performance**: Monitor execution time, especially as data grows
- **Updates**: Review and update the algorithm as needed

## Integration with Frontend

The frontend `recommendations-table.tsx` component reads from this database and displays:
- All recommendations in a unified table format
- Filtering for past 12 months
- Ranking information
- Return percentages with visual indicators

Ensure the API endpoints are configured to read from the `recommendations` table.
