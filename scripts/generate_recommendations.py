#!/usr/bin/env python3
"""
Recommendations Data Generator
Generates weekly and monthly recommendations data starting from 01-Jan-2023
Weekly recommendations run every Saturday for the next week
Monthly recommendations run on the last day of each month for the next month
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple
import random
import calendar

# Database connection
DB_PATH = '../database/index-database.db'

# Configuration
DEFAULT_TOP_RANKS = 3  # Default number of top recommendations to keep

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_indices(conn) -> List[Dict]:
    """Get all indices from database"""
    query = """
    SELECT DISTINCT id, name, symbol 
    FROM indices_master 
    WHERE symbol IS NOT NULL AND symbol != ''
    ORDER BY symbol
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]

def get_historical_prices(conn, index_id: int, start_date: str, end_date: str) -> pd.DataFrame:
    """Get historical prices for an index"""
    query = """
    SELECT date, close_price 
    FROM index_data 
    WHERE index_id = ? AND date BETWEEN ? AND ?
    ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(index_id, start_date, end_date))
    return df

def calculate_returns(prices: pd.DataFrame) -> Dict[str, float]:
    """Calculate various returns from price data"""
    if len(prices) < 2:
        return {
            'weekly_return': None,
            'monthly_return': None,
            'three_week_cumulative': None,
            'three_month_cumulative': None
        }
    
    prices = prices.copy()
    prices['close_price'] = pd.to_numeric(prices['close_price'], errors='coerce')
    prices = prices.dropna(subset=['close_price'])
    
    if len(prices) < 2:
        return {
            'weekly_return': None,
            'monthly_return': None,
            'three_week_cumulative': None,
            'three_month_cumulative': None
        }
    
    # Calculate returns
    first_price = prices.iloc[0]['close_price']
    last_price = prices.iloc[-1]['close_price']
    
    # Weekly return (last 7 days available)
    weekly_prices = prices.tail(7)
    if len(weekly_prices) >= 2:
        weekly_first = weekly_prices.iloc[0]['close_price']
        weekly_last = weekly_prices.iloc[-1]['close_price']
        weekly_return = ((weekly_last - weekly_first) / weekly_first) * 100
    else:
        weekly_return = None
    
    # Monthly return (last 30 days available)
    monthly_prices = prices.tail(30)
    if len(monthly_prices) >= 2:
        monthly_first = monthly_prices.iloc[0]['close_price']
        monthly_last = monthly_prices.iloc[-1]['close_price']
        monthly_return = ((monthly_last - monthly_first) / monthly_first) * 100
    else:
        monthly_return = None
    
    # 3-week cumulative return
    three_week_prices = prices.tail(21)
    if len(three_week_prices) >= 2:
        three_week_first = three_week_prices.iloc[0]['close_price']
        three_week_last = three_week_prices.iloc[-1]['close_price']
        three_week_cumulative = ((three_week_last - three_week_first) / three_week_first) * 100
    else:
        three_week_cumulative = None
    
    # 3-month cumulative return
    three_month_prices = prices.tail(90)
    if len(three_month_prices) >= 2:
        three_month_first = three_month_prices.iloc[0]['close_price']
        three_month_last = three_month_prices.iloc[-1]['close_price']
        three_month_cumulative = ((three_month_last - three_month_first) / three_month_first) * 100
    else:
        three_month_cumulative = None
    
    return {
        'weekly_return': weekly_return,
        'monthly_return': monthly_return,
        'three_week_cumulative': three_week_cumulative,
        'three_month_cumulative': three_month_cumulative
    }

def get_saturdays(start_date: date, end_date: date) -> List[date]:
    """Get all Saturdays between start_date and end_date"""
    saturdays = []
    current_date = start_date
    
    # Find first Saturday
    while current_date.weekday() != 5:  # Saturday is 5
        current_date += timedelta(days=1)
    
    while current_date <= end_date:
        saturdays.append(current_date)
        current_date += timedelta(days=7)
    
    return saturdays

def get_last_days_of_months(start_date: date, end_date: date) -> List[date]:
    """Get last day of each month between start_date and end_date"""
    last_days = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        # Get last day of current month
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        last_day_date = current_date.replace(day=last_day)
        
        if last_day_date >= start_date and last_day_date <= end_date:
            last_days.append(last_day_date)
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)
    
    return last_days

def generate_week_recommendation_id(rec_date: date, symbol: str) -> str:
    """Generate unique weekly recommendation ID"""
    return f"weekly_{rec_date.strftime('%Y%m%d')}_{symbol}"

def generate_month_recommendation_id(rec_date: date, symbol: str) -> str:
    """Generate unique monthly recommendation ID"""
    return f"monthly_{rec_date.strftime('%Y%m%d')}_{symbol}"

def get_week_string(rec_date: date) -> str:
    """Generate week string in format YYYY-WXX"""
    # Find the first day of the year
    jan_1 = date(rec_date.year, 1, 1)
    # Calculate week number
    week_num = ((rec_date - jan_1).days // 7) + 1
    return f"{rec_date.year}-W{week_num:02d}"

def get_month_string(rec_date: date) -> str:
    """Generate month string in format YYYY-MM"""
    return f"{rec_date.year}-{rec_date.month:02d}"

def create_recommendations_table(conn):
    """Create recommendations table if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS recommendations (
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
        last_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (index_id) REFERENCES indices_master (id)
    )
    """
    conn.execute(create_table_query)
    conn.commit()

def insert_weekly_recommendations(conn, rec_date: date, indices: List[Dict], top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate and insert weekly recommendations for specified date"""
    print(f"Generating weekly recommendations for week starting {rec_date}")
    
    # Calculate date range for historical data (3 months before rec_date)
    end_date = rec_date - timedelta(days=1)  # Day before recommendation
    start_date = end_date - timedelta(days=90)  # 3 months of data
    
    recommendations = []
    
    for index in indices:
        try:
            # Get historical prices
            prices = get_historical_prices(conn, index['id'], 
                                       start_date.strftime('%Y-%m-%d'), 
                                       end_date.strftime('%Y-%m-%d'))
            
            if len(prices) < 10:  # Need at least 10 days of data
                continue
            
            # Calculate returns
            returns = calculate_returns(prices)
            
            # Create recommendation
            rec = {
                'recommendation_id': generate_week_recommendation_id(rec_date, index['symbol']),
                'recommendation_date': rec_date.strftime('%Y-%m-%d'),
                'recommendation_month': get_month_string(rec_date),
                'recommendation_week': get_week_string(rec_date),
                'index_id': index['id'],
                'index_name': index['name'],
                'index_symbol': index['symbol'],
                'weekly_return_percentage': returns['weekly_return'],
                'three_week_cumulative_return_percentage': returns['three_week_cumulative'],
                'weekly_recommendation_rank': None,  # Will be calculated after sorting
                'monthly_return_percentage': None,
                'three_month_cumulative_return_percentage': None,
                'monthly_recommendation_rank': None,
                'recommendation_type': 'weekly'
            }
            recommendations.append(rec)
            
        except Exception as e:
            print(f"Error processing {index['symbol']} for weekly recommendation: {e}")
            continue
    
    # Sort by 3-week cumulative return and rank
    recommendations.sort(key=lambda x: x['three_week_cumulative_return_percentage'] or -999, reverse=True)
    for i, rec in enumerate(recommendations):
        rec['weekly_recommendation_rank'] = i + 1
    
    # Keep only top X recommendations
    recommendations = recommendations[:top_ranks]
    
    # Insert into database
    if recommendations:
        insert_query = """
        INSERT OR REPLACE INTO recommendations (
            recommendation_id, recommendation_date, recommendation_month, recommendation_week,
            index_id, index_name, index_symbol, weekly_return_percentage,
            three_week_cumulative_return_percentage, weekly_recommendation_rank,
            monthly_return_percentage, three_month_cumulative_return_percentage,
            monthly_recommendation_rank, recommendation_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for rec in recommendations:
            conn.execute(insert_query, (
                rec['recommendation_id'], rec['recommendation_date'], rec['recommendation_month'],
                rec['recommendation_week'], rec['index_id'], rec['index_name'], rec['index_symbol'],
                rec['weekly_return_percentage'], rec['three_week_cumulative_return_percentage'],
                rec['weekly_recommendation_rank'], rec['monthly_return_percentage'],
                rec['three_month_cumulative_return_percentage'], rec['monthly_recommendation_rank'],
                rec['recommendation_type']
            ))
        
        conn.commit()
        print(f"Inserted {len(recommendations)} weekly recommendations for {rec_date}")

def insert_monthly_recommendations(conn, rec_date: date, indices: List[Dict], top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate and insert monthly recommendations for specified date"""
    print(f"Generating monthly recommendations for {rec_date}")
    
    # Calculate date range for historical data (3 months before rec_date)
    end_date = rec_date - timedelta(days=1)  # Day before recommendation
    start_date = end_date - timedelta(days=90)  # 3 months of data
    
    recommendations = []
    
    for index in indices:
        try:
            # Get historical prices
            prices = get_historical_prices(conn, index['id'], 
                                       start_date.strftime('%Y-%m-%d'), 
                                       end_date.strftime('%Y-%m-%d'))
            
            if len(prices) < 10:  # Need at least 10 days of data
                continue
            
            # Calculate returns
            returns = calculate_returns(prices)
            
            # Create recommendation
            rec = {
                'recommendation_id': generate_month_recommendation_id(rec_date, index['symbol']),
                'recommendation_date': rec_date.strftime('%Y-%m-%d'),
                'recommendation_month': get_month_string(rec_date),
                'recommendation_week': None,
                'index_id': index['id'],
                'index_name': index['name'],
                'index_symbol': index['symbol'],
                'weekly_return_percentage': None,
                'three_week_cumulative_return_percentage': None,
                'weekly_recommendation_rank': None,
                'monthly_return_percentage': returns['monthly_return'],
                'three_month_cumulative_return_percentage': returns['three_month_cumulative'],
                'monthly_recommendation_rank': None,  # Will be calculated after sorting
                'recommendation_type': 'monthly'
            }
            recommendations.append(rec)
            
        except Exception as e:
            print(f"Error processing {index['symbol']} for monthly recommendation: {e}")
            continue
    
    # Sort by 3-month cumulative return and rank
    recommendations.sort(key=lambda x: x['three_month_cumulative_return_percentage'] or -999, reverse=True)
    for i, rec in enumerate(recommendations):
        rec['monthly_recommendation_rank'] = i + 1
    
    # Keep only top X recommendations
    recommendations = recommendations[:top_ranks]
    
    # Insert into database
    if recommendations:
        insert_query = """
        INSERT OR REPLACE INTO recommendations (
            recommendation_id, recommendation_date, recommendation_month, recommendation_week,
            index_id, index_name, index_symbol, weekly_return_percentage,
            three_week_cumulative_return_percentage, weekly_recommendation_rank,
            monthly_return_percentage, three_month_cumulative_return_percentage,
            monthly_recommendation_rank, recommendation_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for rec in recommendations:
            conn.execute(insert_query, (
                rec['recommendation_id'], rec['recommendation_date'], rec['recommendation_month'],
                rec['recommendation_week'], rec['index_id'], rec['index_name'], rec['index_symbol'],
                rec['weekly_return_percentage'], rec['three_week_cumulative_return_percentage'],
                rec['weekly_recommendation_rank'], rec['monthly_return_percentage'],
                rec['three_month_cumulative_return_percentage'], rec['monthly_recommendation_rank'],
                rec['recommendation_type']
            ))
        
        conn.commit()
        print(f"Inserted {len(recommendations)} monthly recommendations for {rec_date}")

def generate_weekly_recommendations_for_date(conn, target_date: date, indices: List[Dict], top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate weekly recommendations for a specific date"""
    print(f"Generating weekly recommendations for {target_date}")
    insert_weekly_recommendations(conn, target_date, indices, top_ranks)
    print(f"Generated weekly recommendations for {target_date.strftime('%Y-%m-%d')}")

def generate_monthly_recommendations_for_date(conn, target_date: date, indices: List[Dict], top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate monthly recommendations for a specific date"""
    print(f"Generating monthly recommendations for {target_date}")
    insert_monthly_recommendations(conn, target_date, indices, top_ranks)
    print(f"Generated monthly recommendations for {target_date.strftime('%Y-%m-%d')}")

def generate_all_recommendations(top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate all recommendations from 01-Jan-2023 to present"""
    conn = get_db_connection()
    
    try:
        # Create recommendations table
        create_recommendations_table(conn)
        
        # Get all indices
        indices = get_indices(conn)
        print(f"Found {len(indices)} indices")
        
        # Set date range
        start_date = date(2025, 1, 1)
        end_date = date.today()
        
        print(f"Generating recommendations from {start_date} to {end_date}")
        
        # Generate weekly recommendations (every Saturday)
        saturdays = get_saturdays(start_date, end_date)
        print(f"Found {len(saturdays)} Saturdays for weekly recommendations")
        
        for saturday in saturdays:
            try:
                insert_weekly_recommendations(conn, saturday, indices, top_ranks)
            except Exception as e:
                print(f"Error generating weekly recommendations for {saturday}: {e}")
                continue
        
        # Generate monthly recommendations (last day of each month)
        last_days = get_last_days_of_months(start_date, end_date)
        print(f"Found {len(last_days)} month-end dates for monthly recommendations")
        
        for last_day in last_days:
            try:
                insert_monthly_recommendations(conn, last_day, indices, top_ranks)
            except Exception as e:
                print(f"Error generating monthly recommendations for {last_day}: {e}")
                continue
        
        print("Recommendations generation completed successfully!")

def generate_recommendations_for_date_range(start_date_str: str, end_date_str: str, recommendation_type: str, top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate recommendations for a specific date range and type"""
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD")
        return
    
    conn = get_db_connection()
    try:
        create_recommendations_table(conn)
        indices = get_indices(conn)
        
        if recommendation_type.lower() == 'weekly':
            # Generate weekly recommendations for each week in range
            current_date = start_date
            while current_date <= end_date:
                # Find the next Saturday (or use current date if it's a valid day)
                if current_date.weekday() in [4, 5, 6]:  # Friday, Saturday, Sunday
                    generate_weekly_recommendations_for_date(conn, current_date, indices, top_ranks)
                    current_date += timedelta(days=7)
                else:
                    # Move to next Saturday
                    days_until_saturday = (5 - current_date.weekday()) % 7
                    if days_until_saturday <= 0:
                        days_until_saturday += 7
                    current_date += timedelta(days=days_until_saturday)
        
        elif recommendation_type.lower() == 'monthly':
            # Generate monthly recommendations for each month in range
            current_date = start_date.replace(day=1)  # Start from first day of month
            while current_date <= end_date:
                # Generate for first day or last day of month
                _, last_day = calendar.monthrange(current_date.year, current_date.month)
                
                # Generate for first day
                generate_monthly_recommendations_for_date(conn, current_date, indices, top_ranks)
                
                # Generate for last day if it's within range
                last_day_date = current_date.replace(day=last_day)
                if last_day_date <= end_date:
                    generate_monthly_recommendations_for_date(conn, last_day_date, indices, top_ranks)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)
        
        else:
            print(f"Unknown recommendation type: {recommendation_type}. Use 'weekly' or 'monthly'")
            return
        
        print(f"Generated {recommendation_type} recommendations from {start_date} to {end_date}")
        
    except Exception as e:
        print(f"Error in date range recommendations generation: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    except Exception as e:
        print(f"Error in recommendations generation: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_current_week_recommendations(top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate recommendations for current week (run on Friday, Saturday, or Sunday)"""
    today = date.today()
    if today.weekday() not in [4, 5, 6]:  # Friday=4, Saturday=5, Sunday=6
        print("This script should only be run on Friday, Saturday, or Sunday for weekly recommendations")
        return
    
    conn = get_db_connection()
    try:
        create_recommendations_table(conn)
        indices = get_indices(conn)
        insert_weekly_recommendations(conn, today, indices, top_ranks)
        print(f"Generated weekly recommendations for {today.strftime('%A')}")
    finally:
        conn.close()

def generate_current_month_recommendations(top_ranks: int = DEFAULT_TOP_RANKS):
    """Generate recommendations for current month (run on last day or first day of month)"""
    today = date.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    
    # Allow running on first day or last day of month
    if today.day != 1 and today.day != last_day:
        print("This script should only be run on first day or last day of month for monthly recommendations")
        return
    
    conn = get_db_connection()
    try:
        create_recommendations_table(conn)
        indices = get_indices(conn)
        insert_monthly_recommendations(conn, today, indices, top_ranks)
        day_type = "first day" if today.day == 1 else "last day"
        print(f"Generated monthly recommendations for {day_type} of month")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "weekly":
            # Parse optional top_ranks parameter
            top_ranks = DEFAULT_TOP_RANKS
            if len(sys.argv) > 2:
                try:
                    top_ranks = int(sys.argv[2])
                    print(f"Using top {top_ranks} recommendations")
                except ValueError:
                    print(f"Invalid top_ranks parameter, using default: {DEFAULT_TOP_RANKS}")
            
            generate_current_week_recommendations(top_ranks)
            
        elif command == "monthly":
            # Parse optional top_ranks parameter
            top_ranks = DEFAULT_TOP_RANKS
            if len(sys.argv) > 2:
                try:
                    top_ranks = int(sys.argv[2])
                    print(f"Using top {top_ranks} recommendations")
                except ValueError:
                    print(f"Invalid top_ranks parameter, using default: {DEFAULT_TOP_RANKS}")
            
            generate_current_month_recommendations(top_ranks)
            
        elif command == "all":
            # Parse optional top_ranks parameter
            top_ranks = DEFAULT_TOP_RANKS
            if len(sys.argv) > 2:
                try:
                    top_ranks = int(sys.argv[2])
                    print(f"Using top {top_ranks} recommendations")
                except ValueError:
                    print(f"Invalid top_ranks parameter, using default: {DEFAULT_TOP_RANKS}")
            
            generate_all_recommendations(top_ranks)
            
        elif command == "date-range":
            # Generate recommendations for specific date range
            if len(sys.argv) < 4:
                print("Usage: python generate_recommendations.py date-range <start_date> <end_date> <weekly|monthly> [top_ranks]")
                print("Example: python generate_recommendations.py date-range 2023-01-01 2023-12-31 weekly 5")
                return
            
            start_date_str = sys.argv[2]
            end_date_str = sys.argv[3]
            recommendation_type = sys.argv[4]
            
            # Parse optional top_ranks parameter
            top_ranks = DEFAULT_TOP_RANKS
            if len(sys.argv) > 5:
                try:
                    top_ranks = int(sys.argv[5])
                    print(f"Using top {top_ranks} recommendations")
                except ValueError:
                    print(f"Invalid top_ranks parameter, using default: {DEFAULT_TOP_RANKS}")
            
            generate_recommendations_for_date_range(start_date_str, end_date_str, recommendation_type, top_ranks)
            
        else:
            print("Usage: python generate_recommendations.py [weekly|monthly|all|date-range] [top_ranks]")
            print("Commands:")
            print("  weekly - Generate current week recommendations (Friday/Saturday/Sunday)")
            print("  monthly - Generate current month recommendations (1st/last day)")
            print("  all - Generate all historical recommendations from 2025-01-01")
            print("  date-range - Generate recommendations for specific date range")
            print("Examples:")
            print("  python generate_recommendations.py weekly 5")
            print("  python generate_recommendations.py monthly 10")
            print("  python generate_recommendations.py all 3")
            print("  python generate_recommendations.py date-range 2023-01-01 2023-12-31 weekly 5")
    else:
        print(f"Generating all recommendations from 2025-01-01 with top {DEFAULT_TOP_RANKS} recommendations...")
        generate_all_recommendations()
