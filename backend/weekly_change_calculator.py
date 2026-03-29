#!/usr/bin/env python3
"""
Weekly Change Calculator Script
Calculates and updates weekly changes for specified indices or all indices
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
        logging.FileHandler(os.path.join(log_dir, 'weekly_change_calculator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeeklyChangeCalculator:
    """Handles calculation of weekly changes for indices"""
    
    def __init__(self, db_path: str = None):
        """Initialize WeeklyChangeCalculator with database path"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'index-database.db')
        
        self.db_path = db_path
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
    
    def get_indices_by_symbols(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get indices by their symbols"""
        try:
            placeholders = ','.join(['?' for _ in symbols])
            query = f"SELECT id, symbol, name FROM indices_master WHERE symbol IN ({placeholders}) AND is_active = 1"
            
            cursor = self.conn.cursor()
            cursor.execute(query, symbols)
            indices = cursor.fetchall()
            
            indices_list = []
            for index in indices:
                indices_list.append({
                    'id': index[0],
                    'symbol': index[1],
                    'name': index[2]
                })
            
            logger.info(f"Retrieved {len(indices_list)} indices for symbols: {symbols}")
            return indices_list
            
        except Exception as e:
            logger.error(f"Failed to get indices by symbols: {e}")
            raise
    
    def get_index_data(self, index_id: int, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get index data for weekly change calculation"""
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
    
    def calculate_weekly_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate weekly change and percentage change"""
        if len(df) < 7:
            logger.warning("Insufficient data for weekly calculation (less than 7 days)")
            return pd.Series(), pd.Series()
        
        # Resample to weekly data (using week ending on Friday)
        weekly_data = df.set_index('date').resample('W-FRI').last()
        
        # Calculate weekly changes
        weekly_change = weekly_data['close_price'].diff()
        weekly_change_percent = (weekly_change / weekly_data['close_price'].shift(1)) * 100
        
        # Reindex back to original dates using forward fill
        weekly_change = weekly_change.reindex(df['date'], method='ffill')
        weekly_change_percent = weekly_change_percent.reindex(df['date'], method='ffill')
        
        return weekly_change, weekly_change_percent
    
    def update_weekly_changes(self, index_id: int, start_date: str = None, end_date: str = None):
        """Update weekly changes for a specific index"""
        try:
            # Get index data
            df = self.get_index_data(index_id, start_date, end_date)
            
            if df.empty:
                logger.warning(f"No data available for weekly calculation for index_id {index_id}")
                return
            
            # Calculate weekly changes
            weekly_change, weekly_change_percent = self.calculate_weekly_change(df)
            
            if weekly_change.empty:
                logger.warning(f"Could not calculate weekly changes for index_id {index_id}")
                return
            
            # Prepare data for update
            update_data = []
            for i, date in enumerate(df['date']):
                if pd.notna(weekly_change.iloc[i]) or pd.notna(weekly_change_percent.iloc[i]):
                    update_data.append({
                        'index_id': index_id,
                        'calculation_date': date.strftime('%Y-%m-%d'),
                        'weekly_change': weekly_change.iloc[i] if pd.notna(weekly_change.iloc[i]) else None,
                        'weekly_change_percent': weekly_change_percent.iloc[i] if pd.notna(weekly_change_percent.iloc[i]) else None
                    })
            
            if not update_data:
                logger.warning(f"No valid weekly changes to update for index_id {index_id}")
                return
            
            # Update database
            cursor = self.conn.cursor()
            
            for data in update_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO index_calculated_data 
                    (index_id, calculation_date, weekly_change, weekly_change_percent)
                    VALUES (?, ?, ?, ?)
                ''', (data['index_id'], data['calculation_date'], data['weekly_change'], data['weekly_change_percent']))
            
            self.conn.commit()
            logger.info(f"Updated weekly changes for {len(update_data)} records for index_id {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to update weekly changes for index_id {index_id}: {e}")
            self.conn.rollback()
            raise
    
    def update_all_indices(self, symbols: List[str] = None, start_date: str = None, end_date: str = None):
        """Update weekly changes for all indices or specific symbols"""
        try:
            # Get indices to process
            if symbols:
                indices = self.get_indices_by_symbols(symbols)
            else:
                indices = self.get_all_indices()
            
            if not indices:
                logger.warning("No indices found to process")
                return
            
            logger.info(f"Processing weekly changes for {len(indices)} indices")
            
            success_count = 0
            error_count = 0
            
            for index in indices:
                try:
                    logger.info(f"Processing {index['name']} ({index['symbol']})")
                    self.update_weekly_changes(index['id'], start_date, end_date)
                    success_count += 1
                    logger.info(f"Successfully updated weekly changes for {index['name']}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to update weekly changes for {index['name']}: {e}")
                    continue
            
            logger.info(f"Weekly change update completed: {success_count} successful, {error_count} failed")
            
        except Exception as e:
            logger.error(f"Failed to update weekly changes: {e}")
            raise
    
    def get_weekly_change_summary(self, symbol: str = None) -> Dict[str, Any]:
        """Get summary of weekly changes for specific index or all indices"""
        try:
            cursor = self.conn.cursor()
            
            if symbol:
                # Get summary for specific symbol
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol,
                        COUNT(icd.id) as weekly_data_points,
                        AVG(icd.weekly_change) as avg_weekly_change,
                        AVG(icd.weekly_change_percent) as avg_weekly_change_percent,
                        MAX(icd.weekly_change_percent) as max_weekly_gain,
                        MIN(icd.weekly_change_percent) as max_weekly_loss
                    FROM indices_master im
                    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id
                    WHERE im.symbol = ? AND im.is_active = 1 AND icd.weekly_change IS NOT NULL
                    GROUP BY im.id, im.name, im.symbol
                '''
                cursor.execute(query, (symbol,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'name': result[0],
                        'symbol': result[1],
                        'weekly_data_points': result[2],
                        'avg_weekly_change': round(result[3], 2) if result[3] else None,
                        'avg_weekly_change_percent': round(result[4], 2) if result[4] else None,
                        'max_weekly_gain': round(result[5], 2) if result[5] else None,
                        'max_weekly_loss': round(result[6], 2) if result[6] else None
                    }
                else:
                    return {'error': f'No weekly data found for symbol {symbol}'}
            else:
                # Get summary for all indices
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol,
                        COUNT(icd.id) as weekly_data_points,
                        AVG(icd.weekly_change) as avg_weekly_change,
                        AVG(icd.weekly_change_percent) as avg_weekly_change_percent,
                        MAX(icd.weekly_change_percent) as max_weekly_gain,
                        MIN(icd.weekly_change_percent) as max_weekly_loss
                    FROM indices_master im
                    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id
                    WHERE im.is_active = 1 AND icd.weekly_change IS NOT NULL
                    GROUP BY im.id, im.name, im.symbol
                    ORDER BY im.name
                '''
                cursor.execute(query)
                results = cursor.fetchall()
                
                summary_list = []
                for result in results:
                    summary_list.append({
                        'name': result[0],
                        'symbol': result[1],
                        'weekly_data_points': result[2],
                        'avg_weekly_change': round(result[3], 2) if result[3] else None,
                        'avg_weekly_change_percent': round(result[4], 2) if result[4] else None,
                        'max_weekly_gain': round(result[5], 2) if result[5] else None,
                        'max_weekly_loss': round(result[6], 2) if result[6] else None
                    })
                
                return summary_list
                
        except Exception as e:
            logger.error(f"Failed to get weekly change summary: {e}")
            raise

def main():
    """Main function to run weekly change calculation"""
    calculator = WeeklyChangeCalculator()
    
    try:
        calculator.connect()
        
        # Update weekly changes for all indices
        logger.info("Starting weekly change calculation for all indices")
        calculator.update_all_indices()
        
        # Get summary of weekly changes
        summary = calculator.get_weekly_change_summary()
        logger.info(f"Weekly change summary for {len(summary)} indices")
        
        # Print summary for top 5 indices
        print("\n=== Weekly Change Summary ===")
        for i, item in enumerate(summary[:5]):
            print(f"{i+1}. {item['name']} ({item['symbol']})")
            print(f"   Data Points: {item['weekly_data_points']}")
            print(f"   Avg Weekly Change: {item['avg_weekly_change_percent']}%")
            print(f"   Best Week: {item['max_weekly_gain']}%")
            print(f"   Worst Week: {item['max_weekly_loss']}%")
            print()
        
        logger.info("Weekly change calculation completed successfully")
        
    except Exception as e:
        logger.error(f"Weekly change calculation failed: {e}")
        raise
    finally:
        calculator.disconnect()

if __name__ == "__main__":
    main()
