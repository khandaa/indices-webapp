from datetime import datetime, timedelta
from calendar import monthrange


def get_week_bounds(date):
    """Get the start and end dates of the week containing the given date.
    Week starts on Monday.
    
    Args:
        date: datetime or date object
        
    Returns:
        tuple: (week_start_date, week_end_date) as strings in YYYY-MM-DD format
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    # Get Monday of the week (weekday() returns 0=Monday, 6=Sunday)
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    
    return week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')


def get_week_bounds_from_iso(year, week):
    """Get week bounds from ISO year and week number.
    
    Args:
        year: ISO year
        week: ISO week number
        
    Returns:
        tuple: (week_start_date, week_end_date) as strings in YYYY-MM-DD format
    """
    # January 4th is always in week 1
    jan4 = datetime(year, 1, 4)
    week_start = jan4 + timedelta(weeks=week-1, days=-jan4.weekday())
    week_end = week_start + timedelta(days=6)
    
    return week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')


def get_week_from_date(date):
    """Extract year-week format from a date.
    
    Args:
        date: datetime or date object or string
        
    Returns:
        str: week in format "YYYY-WW" (e.g., "2026-W17")
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    return f"{date.year}-W{date.isocalendar()[1]:02d}"


def get_month_bounds(date):
    """Get the start and end dates of the month containing the given date.
    
    Args:
        date: datetime or date object or string in YYYY-MM-DD format
        
    Returns:
        tuple: (month_start_date, month_end_date) as strings in YYYY-MM-DD format
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    _, last_day = monthrange(date.year, date.month)
    month_start = date.replace(day=1)
    month_end = date.replace(day=last_day)
    
    return month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')


def get_month_from_date(date):
    """Extract year-month format from a date.
    
    Args:
        date: datetime or date object or string
        
    Returns:
        str: month in format "YYYY-MM"
    """
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    return f"{date.year}-{date.month:02d}"


def get_past_weeks(num_weeks, end_date=None):
    """Get list of past weeks.
    
    Args:
        num_weeks: Number of past weeks to include
        end_date: End date (defaults to today)
        
    Returns:
        list: List of dicts with week info
    """
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    weeks = []
    current_date = end_date
    
    for _ in range(num_weeks):
        week_start, week_end = get_week_bounds(current_date)
        week_str = get_week_from_date(current_date)
        
        weeks.append({
            'week': week_str,
            'start_date': week_start,
            'end_date': week_end,
            'is_past': True
        })
        
        # Move to previous week
        current_date = current_date - timedelta(days=7)
    
    return list(reversed(weeks))


def get_upcoming_weeks(num_weeks=1, start_date=None):
    """Get list of upcoming weeks.
    
    Args:
        num_weeks: Number of upcoming weeks
        start_date: Start date (defaults to today)
        
    Returns:
        list: List of dicts with week info
    """
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Start from start of current week
    week_start, week_end = get_week_bounds(start_date)
    
    weeks = []
    current_date = start_date + timedelta(days=7)  # Start from next week
    
    for _ in range(num_weeks):
        week_start, week_end = get_week_bounds(current_date)
        week_str = get_week_from_date(current_date)
        
        weeks.append({
            'week': week_str,
            'start_date': week_start,
            'end_date': week_end,
            'is_past': False
        })
        
        current_date = current_date + timedelta(days=7)
    
    return weeks


def get_past_months(num_months, end_date=None):
    """Get list of past months.
    
    Args:
        num_months: Number of past months to include
        end_date: End date (defaults to today)
        
    Returns:
        list: List of dicts with month info
    """
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    months = []
    current_date = end_date
    
    for _ in range(num_months):
        month_start, month_end = get_month_bounds(current_date)
        month_str = get_month_from_date(current_date)
        
        months.append({
            'month': month_str,
            'start_date': month_start,
            'end_date': month_end,
            'is_past': True
        })
        
        # Move to previous month
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            current_date = current_date.replace(month=current_date.month - 1)
    
    return list(reversed(months))


def get_upcoming_months(num_months=1, start_date=None):
    """Get list of upcoming months.
    
    Args:
        num_months: Number of upcoming months
        start_date: Start date (defaults to today)
        
    Returns:
        list: List of dicts with month info
    """
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Start from next month
    if start_date.month == 12:
        current_date = start_date.replace(year=start_date.year + 1, month=1)
    else:
        current_date = start_date.replace(month=start_date.month + 1)
    
    months = []
    
    for _ in range(num_months):
        month_start, month_end = get_month_bounds(current_date)
        month_str = get_month_from_date(current_date)
        
        months.append({
            'month': month_str,
            'start_date': month_start,
            'end_date': month_end,
            'is_past': False
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return months


def format_week_display(week_str):
    """Format week string for display.
    
    Args:
        week_str: Week string like "2026-W17"
        
    Returns:
        str: Formatted like "Week 17, 2026"
    """
    parts = week_str.split('-W')
    if len(parts) == 2:
        return f"Week {parts[1]}, {parts[0]}"
    return week_str


def format_month_display(month_str):
    """Format month string for display.
    
    Args:
        month_str: Month string like "2026-04"
        
    Returns:
        str: Formatted like "April 2026"
    """
    parts = month_str.split('-')
    if len(parts) == 2:
        try:
            month_name = datetime(int(parts[0]), int(parts[1]), 1).strftime('%B')
            return f"{month_name} {parts[0]}"
        except:
            pass
    return month_str