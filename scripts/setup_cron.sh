#!/bin/bash
# Setup cron jobs for automated recommendations generation

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/generate_recommendations.py"

# Create cron jobs
# Weekly: Run every Saturday at 9:00 AM
# Monthly: Run on the last day of every month at 9:00 AM

# Create temporary cron file
CRON_FILE="/tmp/recommendations_cron"

cat > "$CRON_FILE" << EOF
# Recommendations Generation Cron Jobs
# Weekly recommendations - Friday, Saturday, and Sunday at 9:00 AM
0 9 * * 5 cd "$PROJECT_DIR" && /usr/bin/python3 "$PYTHON_SCRIPT" weekly >> "$PROJECT_DIR/logs/weekly_cron.log" 2>&1
0 9 * * 6 cd "$PROJECT_DIR" && /usr/bin/python3 "$PYTHON_SCRIPT" weekly >> "$PROJECT_DIR/logs/weekly_cron.log" 2>&1
0 9 * * 0 cd "$PROJECT_DIR" && /usr/bin/python3 "$PYTHON_SCRIPT" weekly >> "$PROJECT_DIR/logs/weekly_cron.log" 2>&1

# Monthly recommendations - first day and last day of every month at 9:00 AM
0 9 1 * * cd "$PROJECT_DIR" && /usr/bin/python3 "$PYTHON_SCRIPT" monthly >> "$PROJECT_DIR/logs/monthly_cron.log" 2>&1
0 9 28-31 * * [ \$(date +\%m -d tomorrow) != \$(date +\%m) ] && cd "$PROJECT_DIR" && /usr/bin/python3 "$PYTHON_SCRIPT" monthly >> "$PROJECT_DIR/logs/monthly_cron.log" 2>&1
EOF

# Install cron jobs
crontab "$CRON_FILE"

# Clean up
rm "$CRON_FILE"

echo "Cron jobs installed successfully!"
echo "Weekly recommendations: Friday, Saturday, and Sunday at 9:00 AM"
echo "Monthly recommendations: First day and last day of every month at 9:00 AM"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove cron jobs: crontab -r"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "Log directory created at: $PROJECT_DIR/logs"
