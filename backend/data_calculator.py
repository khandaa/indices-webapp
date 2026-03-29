#!/usr/bin/env python3
"""
Data calculation script for Indices Web Application
Calculates daily, weekly, monthly, and yearly changes for all indices
"""

import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'data_calculation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCalculator:
    """Handles calculation of index performance metrics"""
    
    def __init__(self, db_path: str = None):
        """Initialize DataCalculator with database path"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'index-database.db')
        
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def get_all_indices(self) -> List[Dict[str, Any]]:
        """Get all active indices from database"""
        query = "SELECT id, symbol, name FROM indices_master WHERE is_active = 1"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            indices = cursor.fetchall()
            
            indices_list = []
            for index in indices:
                indices_list.append({
                    'id': index[0],
                    'symbol': index[1],
                    'name': index[2]
                })
            
            logger.info(f"Retrieved {len(indices_list)} active indices")
            return indices_list
            
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            raise
    
    def get_index_data(self, index_id: int, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get index data for calculation"""
        try:
            query = """
                SELECT date, close_price 
                FROM index_data 
                WHERE index_id = ? AND close_price IS NOT NULL
            """
            
            params = [index_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            if not data:
                logger.warning(f"No data found for index_id {index_id}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data, columns=['date', 'close_price'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            logger.info(f"Retrieved {len(df)} records for index_id {index_id}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get index data for index_id {index_id}: {e}")
            raise
    
    def calculate_daily_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate daily change and percentage change"""
        if len(df) < 2:
            return pd.Series(), pd.Series()
        
        daily_change = df['close_price'].diff()
        daily_change_percent = (daily_change / df['close_price'].shift(1)) * 100
        
        return daily_change, daily_change_percent
    
    def calculate_weekly_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate weekly change and percentage change (7 days ago to today)"""
        if len(df) < 7:
            return pd.Series(), pd.Series()

        # Calculate change from 7 days ago to current day
        weekly_change = df['close_price'] - df['close_price'].shift(7)
        weekly_change_percent = (weekly_change / df['close_price'].shift(7)) * 100

        return weekly_change, weekly_change_percent
    
    def calculate_monthly_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate monthly change and percentage change (30 days ago to today)"""
        if len(df) < 30:
            return pd.Series(), pd.Series()

        # Calculate change from 30 days ago to current day
        monthly_change = df['close_price'] - df['close_price'].shift(30)
        monthly_change_percent = (monthly_change / df['close_price'].shift(30)) * 100

        return monthly_change, monthly_change_percent
    
    def calculate_yearly_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate yearly change and percentage change"""
        # For less than 365 days, we'll use the entire period as a "year"
        if len(df) < 30:  # Need at least 30 days for any meaningful calculation
            return pd.Series(), pd.Series()
        
        # If we have less than 365 days, calculate change from first to last day
        if len(df) < 365:
            # Calculate change from first available day to current day
            first_price = df['close_price'].iloc[0]
            yearly_change = df['close_price'] - first_price
            yearly_change_percent = (yearly_change / first_price) * 100
            
            return yearly_change, yearly_change_percent
        else:
            # Resample to yearly data (using year end)
            yearly_data = df.set_index('date').resample('YE').last()
            
            yearly_change = yearly_data['close_price'].diff()
            yearly_change_percent = (yearly_change / yearly_data['close_price'].shift(1)) * 100
            
            # Reindex back to original dates
            yearly_change = yearly_change.reindex(df['date'], method='ffill')
            yearly_change_percent = yearly_change_percent.reindex(df['date'], method='ffill')
            
            return yearly_change, yearly_change_percent
    
    def calculate_all_metrics(self, index_id: int, start_date: str = None, end_date: str = None):
        """Calculate all performance metrics for an index"""
        try:
            # Get index data
            df = self.get_index_data(index_id, start_date, end_date)
            
            if df.empty:
                logger.warning(f"No data available for calculations for index_id {index_id}")
                return
            
            # Calculate all metrics
            daily_change, daily_change_percent = self.calculate_daily_change(df)
            weekly_change, weekly_change_percent = self.calculate_weekly_change(df)
            monthly_change, monthly_change_percent = self.calculate_monthly_change(df)
            yearly_change, yearly_change_percent = self.calculate_yearly_change(df)
            
            # Combine results
            results_df = pd.DataFrame({
                'index_id': index_id,
                'calculation_date': df['date'].dt.strftime('%Y-%m-%d'),
                'daily_change': daily_change,
                'weekly_change': weekly_change,
                'monthly_change': monthly_change,
                'yearly_change': yearly_change,
                'daily_change_percent': daily_change_percent,
                'weekly_change_percent': weekly_change_percent,
                'monthly_change_percent': monthly_change_percent,
                'yearly_change_percent': yearly_change_percent
            })
            
            # Remove rows with all NaN values (first few rows will have NaN for longer periods)
            results_df = results_df.dropna(how='all', subset=['daily_change', 'weekly_change', 'monthly_change', 'yearly_change'])
            
            # Ensure calculation_date is never null - fill with date string if needed
            results_df['calculation_date'] = results_df['calculation_date'].fillna('')
            
            # Remove rows where calculation_date is empty after fill
            results_df = results_df[results_df['calculation_date'] != '']
            
            # Convert NaN to None for database compatibility (except for calculation_date)
            for col in ['daily_change', 'weekly_change', 'monthly_change', 'yearly_change',
                       'daily_change_percent', 'weekly_change_percent', 'monthly_change_percent', 'yearly_change_percent']:
                results_df[col] = results_df[col].where(pd.notna(results_df[col]), None)
            
            # Insert into database
            self.insert_calculated_data(results_df)
            
            logger.info(f"Calculated metrics for {len(results_df)} records for index_id {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics for index_id {index_id}: {e}")
            raise
    
    def insert_calculated_data(self, data: pd.DataFrame):
        """Insert calculated data into database"""
        try:
            cursor = self.conn.cursor()
            
            for idx, row in data.iterrows():
                # Ensure calculation_date is not None
                if pd.isna(row['calculation_date']) or row['calculation_date'] == '':
                    logger.warning(f"Skipping row {idx} due to null calculation_date")
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO index_calculated_data 
                    (index_id, calculation_date, daily_change, weekly_change, monthly_change, yearly_change,
                     daily_change_percent, weekly_change_percent, monthly_change_percent, yearly_change_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['index_id'], row['calculation_date'], row['daily_change'], row['weekly_change'], 
                      row['monthly_change'], row['yearly_change'], row['daily_change_percent'], 
                      row['weekly_change_percent'], row['monthly_change_percent'], row['yearly_change_percent']))
            
            self.conn.commit()
            logger.info(f"Inserted {len(data)} calculated records")
            
        except Exception as e:
            logger.error(f"Failed to insert calculated data: {e}")
            self.conn.rollback()
            raise
    
    def calculate_for_all_indices(self, start_date: str = None, end_date: str = None):
        """Calculate metrics for all active indices"""
        try:
            indices = self.get_all_indices()
            
            for index in indices:
                try:
                    logger.info(f"Calculating metrics for {index['name']} ({index['symbol']})")
                    self.calculate_all_metrics(index['id'], start_date, end_date)
                    logger.info(f"Successfully calculated metrics for {index['name']}")
                except Exception as e:
                    logger.error(f"Failed to calculate metrics for {index['name']}: {e}")
                    continue
            
            logger.info("Calculation completed for all indices")
            
        except Exception as e:
            logger.error(f"Failed to calculate for all indices: {e}")
            raise
    
    def calculate_for_specific_indices(self, symbols: List[str], start_date: str = None, end_date: str = None):
        """Calculate metrics for specific indices by symbols"""
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
                    logger.info(f"Calculating metrics for {index_dict['name']} ({index_dict['symbol']})")
                    self.calculate_all_metrics(index_dict['id'], start_date, end_date)
                    logger.info(f"Successfully calculated metrics for {index_dict['name']}")
                except Exception as e:
                    logger.error(f"Failed to calculate metrics for {index_dict['name']}: {e}")
                    continue
            
            logger.info(f"Calculation completed for specified indices")
            
        except Exception as e:
            logger.error(f"Failed to calculate for specific indices: {e}")
            raise
    
    def calculate_for_date_range(self, start_date: str, end_date: str, symbols: List[str] = None):
        """Calculate metrics for specific date range"""
        try:
            if symbols:
                self.calculate_for_specific_indices(symbols, start_date, end_date)
            else:
                self.calculate_for_all_indices(start_date, end_date)
            
            logger.info(f"Calculation completed for date range {start_date} to {end_date}")
            
        except Exception as e:
            logger.error(f"Failed to calculate for date range: {e}")
            raise

def main():
    """Main function to run data calculation"""
    calculator = DataCalculator()
    
    try:
        calculator.connect()
        
        # Calculate metrics for all indices
        calculator.calculate_for_all_indices()
        
        logger.info("Data calculation process completed successfully")
        
    except Exception as e:
        logger.error(f"Data calculation process failed: {e}")
        raise
    finally:
        calculator.disconnect()

if __name__ == "__main__":
    main()
