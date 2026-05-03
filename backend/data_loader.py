#!/usr/bin/env python3
"""
Data loading script for Indices Web Application
Loads historical data from yfinance for all indices in the database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# os.environ['DB_TYPE'] = 'mysql'

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from db import Database

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'data_loading.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading of index data from yfinance"""
    
    def __init__(self):
        """Initialize DataLoader with database"""
        self.db = Database()
        self._conn = None  # Legacy compatibility
    
    @property
    def conn(self):
        """Legacy property for backward compatibility"""
        return self.db._conn
        
    def connect(self):
        """Connect to database"""
        try:
            self.db.connect()
            logger.info(f"Connected to MySQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.close()
        logger.info("Disconnected from database")
    
    def get_all_indices(self) -> List[Dict[str, Any]]:
        """Get all active indices from database"""
        query = "SELECT id, symbol, name FROM indices_master WHERE is_active = 1"
        
        try:
            results = self.db.fetch_all(query)
            
            indices_list = []
            for row in results:
                indices_list.append({
                    'id': row['id'],
                    'symbol': row['symbol'],
                    'name': row['name']
                })
            
            logger.info(f"Retrieved {len(indices_list)} active indices")
            return indices_list
            
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            raise
    
    def get_index_data_from_yfinance(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Download index data from yfinance"""
        try:
            # Default to last 1 year if no dates specified
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Add .NS suffix for NSE indices if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                ticker = f"{symbol}.NS"
            else:
                ticker = symbol
            
            logger.info(f"Downloading data for {ticker} from {start_date} to {end_date}")
            
            # Download data
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()
            
            # Reset index to get date as column
            data.reset_index(inplace=True)
            
            # Rename columns to match database schema
            data.rename(columns={
                'Date': 'date',
                'Open': 'open_price',
                'Close': 'close_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Volume': 'volume'
            }, inplace=True)
            
            # Convert date to string format
            data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
            
            logger.info(f"Downloaded {len(data)} records for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download data for {symbol}: {e}")
            raise
    
    def insert_index_data(self, index_id: int, data: pd.DataFrame):
        """Insert index data into database"""
        try:
            # Add index_id and upload_date
            data['index_id'] = index_id
            data['upload_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Select only required columns
            required_columns = [
                'index_id', 'date', 'open_price', 'close_price', 
                'high_price', 'low_price', 'volume', 'upload_date'
            ]
            data_to_insert = data[required_columns]
            
            # Insert data using INSERT OR REPLACE to handle duplicates
            cursor = self.conn.cursor()
            
            for _, row in data_to_insert.iterrows():
                params = (
                    int(row['index_id']), str(row['date']), float(row['open_price']), 
                    float(row['close_price']), float(row['high_price']), float(row['low_price']),
                    int(row['volume']), str(row['upload_date'])
                )
                cursor.execute('''
                    INSERT OR REPLACE INTO index_data 
                    (index_id, date, open_price, close_price, high_price, low_price, volume, upload_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', params)
            
            self.conn.commit()
            logger.info(f"Inserted {len(data_to_insert)} records for index_id {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to insert data for index_id {index_id}: {e}")
            self.conn.rollback()
            raise
    
    def load_data_for_all_indices(self, start_date: str = None, end_date: str = None):
        """Load data for all active indices"""
        try:
            indices = self.get_all_indices()
            
            for index in indices:
                try:
                    logger.info(f"Loading data for {index['name']} ({index['symbol']})")
                    
                    # Download data
                    data = self.get_index_data_from_yfinance(index['symbol'], start_date, end_date)
                    
                    if not data.empty:
                        # Insert data
                        self.insert_index_data(index['id'], data)
                        logger.info(f"Successfully loaded data for {index['name']}")
                    else:
                        logger.warning(f"No data available for {index['name']}")
                        
                except Exception as e:
                    logger.error(f"Failed to load data for {index['name']}: {e}")
                    continue
            
            logger.info("Data loading completed for all indices")
            
        except Exception as e:
            logger.error(f"Failed to load data for all indices: {e}")
            raise
    
    def load_historical_data(self, start_date: str = '2019-01-01'):
        """Load historical data from specified start date to present for all active indices"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            indices = self.get_all_indices()
            
            logger.info(f"Loading historical data from {start_date} to {end_date}")
            
            for index in indices:
                try:
                    logger.info(f"Loading historical data for {index['name']} ({index['symbol']})")
                    
                    # Download historical data
                    data = self.get_index_data_from_yfinance(index['symbol'], start_date, end_date)
                    
                    if not data.empty:
                        # Insert data
                        self.insert_index_data(index['id'], data)
                        logger.info(f"Successfully loaded {len(data)} records for {index['name']}")
                    else:
                        logger.warning(f"No data available for {index['name']}")
                        
                except Exception as e:
                    logger.error(f"Failed to load historical data for {index['name']}: {e}")
                    continue
            
            logger.info("Historical data loading completed for all indices")
            
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            raise
    
    def load_data_for_specific_indices(self, symbols: List[str], start_date: str = None, end_date: str = None):
        """Load data for specific indices by symbols"""
        try:
            # Get index IDs for symbols
            placeholders = ','.join(['?' for _ in symbols])
            query = f"SELECT id, symbol, name FROM indices_master WHERE symbol IN ({placeholders}) AND is_active = 1"
            
            cursor = self.conn.cursor()
            cursor.execute(query, symbols)
            indices = cursor.fetchall()
            
            if not indices:
                logger.warning(f"No active indices found for symbols: {symbols}")
                return
            
            for index in indices:
                try:
                    index_dict = {'id': index[0], 'symbol': index[1], 'name': index[2]}
                    logger.info(f"Loading data for {index_dict['name']} ({index_dict['symbol']})")
                    
                    # Download data
                    data = self.get_index_data_from_yfinance(index_dict['symbol'], start_date, end_date)
                    
                    if not data.empty:
                        # Insert data
                        self.insert_index_data(index_dict['id'], data)
                        logger.info(f"Successfully loaded data for {index_dict['name']}")
                    else:
                        logger.warning(f"No data available for {index_dict['name']}")
                        
                except Exception as e:
                    logger.error(f"Failed to load data for {index_dict['name']}: {e}")
                    continue
            
            logger.info(f"Data loading completed for specified indices")
            
        except Exception as e:
            logger.error(f"Failed to load data for specific indices: {e}")
            raise

def main():
    """Main function to run data loading"""
    import sys
    
    loader = DataLoader()
    
    try:
        loader.connect()
        
        # Check if historical loading is requested
        if len(sys.argv) > 1 and sys.argv[1] == '--historical':
            start_date = sys.argv[2] if len(sys.argv) > 2 else '2019-01-01'
            logger.info(f"Loading historical data from {start_date}")
            loader.load_historical_data(start_date)
        else:
            # Load data for all indices for the last year
            loader.load_data_for_all_indices()
        
        logger.info("Data loading process completed successfully")
        
    except Exception as e:
        logger.error(f"Data loading process failed: {e}")
        raise
    finally:
        loader.disconnect()

if __name__ == "__main__":
    main()
