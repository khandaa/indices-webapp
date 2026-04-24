#!/usr/bin/env python3
"""
YFinance Data Fetcher
Fetches daily price data from yfinance and stores in index_data table
Only fetches data that doesn't already exist in the database
"""

import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import sys
import time

# Database connection
DB_PATH = '../database/index-database.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_indices(conn) -> List[Dict]:
    """Get all indices from indices_master table"""
    query = """
    SELECT id, name, symbol, symbol 
    FROM indices_master 
    WHERE symbol IS NOT NULL AND symbol != ''
    ORDER BY symbol
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]

def get_latest_date(conn, index_id: int) -> str:
    """Get the latest date for an index in index_data table"""
    query = """
    SELECT MAX(date) as latest_date 
    FROM index_data 
    WHERE index_id = ?
    """
    cursor = conn.execute(query, (index_id,))
    result = cursor.fetchone()
    return result['latest_date'] if result and result['latest_date'] else None

def fetch_yfinance_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch data from yfinance"""
    try:
        symbol_ns = symbol + ".NS"
        print(f"Fetching data for {symbol_ns} from {start_date} to {end_date}")
        
        # Download data
        ticker = yf.Ticker(symbol_ns)
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            print(f"No data found for {symbol_ns}")
            return pd.DataFrame()
        
        # Reset index to make date a column
        data.reset_index(inplace=True)
        
        # Select and rename columns
        if 'Adj Close' in data.columns:
            # Use Adjusted Close if available (accounts for splits/dividends)
            data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
            data = data.rename(columns={'Adj Close': 'adj_close'})
        else:
            data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            data['adj_close'] = data['Close']  # Use Close as fallback
        
        data.columns = ['date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'adj_close']
        
        # Convert date to string format
        data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        
        # Use adjusted close for close price if available
        data['close_price'] = data['adj_close']
        
        # Drop the adj_close column
        data = data.drop('adj_close', axis=1)
        
        print(f"Fetched {len(data)} records for {symbol}")
        return data
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def insert_price_data(conn, index_id: int, data: pd.DataFrame):
    """Insert price data into index_data table"""
    if data.empty:
        return
    
    # Convert to list of tuples for insertion
    records = []
    for _, row in data.iterrows():
        records.append((
            row['date'], 
            index_id,  # Explicit integer
            float(row['open_price']),
            float(row['high_price']),
            float(row['low_price']),
            float(row['close_price']),
            int(row['volume']) if pd.notna(row['volume']) else None
        ))
    
    # Insert data
    insert_query = """
    INSERT OR REPLACE INTO index_data 
    (date, index_id, open_price, high_price, low_price, close_price, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    conn.executemany(insert_query, records)
    conn.commit()
    print(f"Inserted {len(records)} records for index_id {index_id}")

def create_index_data_table(conn):
    """Create index_data table if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS index_data (
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
    """
    conn.execute(create_table_query)
    conn.commit()

def add_symbol_column(conn):
    """Add symbol column to indices_master if it doesn't exist"""
    try:
        conn.execute("ALTER TABLE indices_master ADD COLUMN symbol TEXT")
        conn.commit()
        print("Added symbol column to indices_master")
    except sqlite3.OperationalError:
        # Column already exists
        pass

def update_symbols(conn):
    """Update symbol column for indices that don't have it"""
    indices = get_indices(conn)
    
    for index in indices:
        if not index.get('symbol'):
            # Default to symbol with .NS suffix for Indian stocks
            # symbol = f"{index['symbol']}.NS"
            conn.execute(
                "UPDATE indices_master SET symbol = ? WHERE id = ?",
                (symbol, index['id'])
            )
    
    conn.commit()
    print("Updated yfinance symbols for indices")

def fetch_all_data(start_date: str = None):
    """Fetch data for all indices"""
    conn = get_db_connection()
    
    try:
        # Create table if needed
        create_index_data_table(conn)
        
        # Add symbol column if needed
        add_symbol_column(conn)
        
        # Update yfinance symbols
        update_symbols(conn)
        
        # Get all indices
        indices = get_indices(conn)
        print(f"Found {len(indices)} indices to fetch data for")
        
        # Default start date (1 year ago)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        total_fetched = 0
        total_inserted = 0
        
        for index in indices:
            print(f"\nProcessing {index['name']} ({index['symbol']})")
            
            # Get latest date for this index
            latest_date = get_latest_date(conn, index['id'])
            
            # Determine start date for fetching
            if latest_date:
                # Start from day after latest date
                fetch_start = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                print(f"Latest data: {latest_date}, fetching from: {fetch_start}")
            else:
                # No existing data, use default start date
                fetch_start = start_date
                print(f"No existing data, fetching from: {fetch_start}")
            
            # Skip if we're up to date
            if fetch_start >= end_date:
                print(f"Data is up to date for {index['symbol']}")
                continue
            
            # Fetch data
            data = fetch_yfinance_data(index['symbol'], fetch_start, end_date)
            
            if not data.empty:
                # Insert into database
                insert_price_data(conn, index['id'], data)
                total_fetched += len(data)
                total_inserted += len(data)
            
            # Rate limiting to avoid overwhelming yfinance
            time.sleep(0.5)
        
        print(f"\nSummary:")
        print(f"Total records fetched: {total_fetched}")
        print(f"Total records inserted: {total_inserted}")
        
    except Exception as e:
        print(f"Error in fetch_all_data: {e}")
        conn.rollback()
    finally:
        conn.close()

def fetch_single_index(symbol: str, start_date: str = None):
    """Fetch data for a single index"""
    conn = get_db_connection()
    
    try:
        create_index_data_table(conn)
        
        # Check if symbol column exists
        cursor = conn.execute("PRAGMA table_info(indices_master)")
        columns = [row[1] for row in cursor.fetchall()]
        has_symbol = 'symbol' in columns
        
        # Get index info
        if has_symbol:
            query = "SELECT id, symbol FROM indices_master WHERE symbol = ? OR symbol = ?"
            cursor = conn.execute(query, (symbol, symbol))
        else:
            query = "SELECT id, symbol FROM indices_master WHERE symbol = ?"
            cursor = conn.execute(query, (symbol,))
        
        index = cursor.fetchone()
        
        if not index:
            print(f"Index {symbol} not found in indices_master")
            return
        
        index_id = index['id']
        
        # Determine yfinance symbol (add .NS for yfinance API)
        original_symbol = index['symbol']
        if has_symbol and index['symbol']:
            symbol = index['symbol']
        else:
            # Add .NS suffix for Indian stocks
            symbol = f"{original_symbol}.NS"
        
        # Default start date (1 year ago)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Fetching data for {original_symbol} ({symbol}) from {start_date} to {end_date}")
        
        # Get latest date
        latest_date = get_latest_date(conn, index_id)
        
        if latest_date:
            fetch_start = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"Latest data: {latest_date}, fetching from: {fetch_start}")
        else:
            fetch_start = start_date
            print(f"No existing data, fetching from: {fetch_start}")
        
        # Skip if up to date
        if fetch_start >= end_date:
            print(f"Data is up to date for {symbol}")
            return
        
        # Fetch and insert data
        data = fetch_yfinance_data(symbol, fetch_start, end_date)
        if not data.empty:
            insert_price_data(conn, index_id, data)
        
    except Exception as e:
        print(f"Error in fetch_single_index: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_status():
    """Show current data status"""
    conn = get_db_connection()
    
    try:
        # Check if symbol column exists
        cursor = conn.execute("PRAGMA table_info(indices_master)")
        columns = [row[1] for row in cursor.fetchall()]
        has_symbol = 'symbol' in columns
        
        # Build query based on available columns
        if has_symbol:
            query = """
            SELECT 
                im.symbol,
                im.name,
                im.symbol,
                COUNT(id.id) as record_count,
                MIN(id.date) as earliest_date,
                MAX(id.date) as latest_date
            FROM indices_master im
            LEFT JOIN index_data id ON im.id = id.index_id
            GROUP BY im.id, im.symbol, im.name, im.symbol
            ORDER BY im.symbol
            """
        else:
            query = """
            SELECT 
                im.symbol,
                im.name,
                '' as symbol,
                COUNT(id.id) as record_count,
                MIN(id.date) as earliest_date,
                MAX(id.date) as latest_date
            FROM indices_master im
            LEFT JOIN index_data id ON im.id = id.index_id
            GROUP BY im.id, im.symbol, im.name
            ORDER BY im.symbol
            """
        
        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        print("\nData Status:")
        print("-" * 100)
        print(f"{'Symbol':<10} {'Name':<30} {'YFinance Symbol':<15} {'Records':<10} {'Earliest':<12} {'Latest':<12}")
        print("-" * 100)
        
        for result in results:
            record_count = result['record_count'] or 0
            earliest_date = result['earliest_date'] or 'N/A'
            latest_date = result['latest_date'] or 'N/A'
            symbol = result['symbol'] or 'N/A'
            
            print(f"{result['symbol']:<10} {result['name'][:30]:<30} {symbol:<15} {record_count:<10} {earliest_date:<12} {latest_date:<12}")
        
        print("-" * 100)
        print(f"Total indices: {len(results)}")
        
        # Show data summary
        total_records = sum(r['record_count'] or 0 for r in results)
        indices_with_data = sum(1 for r in results if r['record_count'] and r['record_count'] > 0)
        
        print(f"Indices with data: {indices_with_data}")
        print(f"Total records: {total_records}")
        
    except Exception as e:
        print(f"Error in show_status: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fetch_yfinance_data.py [COMMAND] [OPTIONS]")
        print("\nCommands:")
        print("  all [start_date]    - Fetch data for all indices (optional start_date in YYYY-MM-DD)")
        print("  single [symbol] [start_date] - Fetch data for single index")
        print("  status              - Show current data status")
        print("\nExamples:")
        print("  python fetch_yfinance_data.py all 2023-01-01")
        print("  python fetch_yfinance_data.py single NIFTYBEES")
        print("  python fetch_yfinance_data.py single RELIANCE 2024-01-01")
        print("  python fetch_yfinance_data.py status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "all":
        start_date = sys.argv[2] if len(sys.argv) > 2 else None
        fetch_all_data(start_date)
    elif command == "single":
        if len(sys.argv) < 3:
            print("Error: symbol is required for single command")
            sys.exit(1)
        symbol = sys.argv[2]
        start_date = sys.argv[3] if len(sys.argv) > 3 else None
        fetch_single_index(symbol, start_date)
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
