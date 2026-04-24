#!/bin/bash

# Setup Cron Job for YFinance Data Fetcher
# Sets up automated daily data fetching

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_status "Setting up cron job for YFinance data fetching..."

# Create temporary cron file
CRON_FILE="/tmp/yfinance_cron"

# Get current crontab
crontab -l > /tmp/current_cron 2>/dev/null || echo "" > /tmp/current_cron

# Create new cron entry
cat > "$CRON_FILE" << EOF
# YFinance Data Fetcher - Daily update at 6:00 PM
0 18 * * * cd $SCRIPT_DIR && source ../venv/bin/activate && python fetch_yfinance_data.py all >> $PROJECT_DIR/logs/yfinance_fetch.log 2>&1

$(cat /tmp/current_cron | grep -v "yfinance")
EOF

# Install new crontab
crontab "$CRON_FILE"

# Clean up
rm "$CRON_FILE" /tmp/current_cron

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

print_success "Cron job installed successfully!"
echo ""
echo "Schedule: Daily at 6:00 PM (18:00)"
echo "Log file: $PROJECT_DIR/logs/yfinance_fetch.log"
echo ""
echo "To view cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove cron job: crontab -r"
echo ""
echo "The script will fetch data for all indices that need updating."
