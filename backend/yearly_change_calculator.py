#!/usr/bin/env python3
"""
Yearly Change Calculator Script
Calculates and updates yearly changes for specified indices or all indices
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
        logging.FileHandler(os.path.join(log_dir, 'yearly_change_calculator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YearlyChangeCalculator:
    """Handles calculation of yearly changes for indices"""
    
    def __init__(self, db_path: str = None):
        """Initialize YearlyChangeCalculator with database path"""
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
        """Get index data for yearly change calculation"""
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
    
    def calculate_yearly_change(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate yearly change and percentage change"""
        # For less than 365 days, we'll use the entire period as a "year"
        if len(df) < 30:  # Need at least 30 days for any meaningful calculation
            logger.warning("Insufficient data for yearly calculation (less than 30 days)")
            return pd.Series(), pd.Series()
        
        # If we have less than 365 days, calculate change from first to last day
        if len(df) < 365:
            logger.info(f"Using available {len(df)} days for yearly calculation")
            # Calculate change from first available day to current day
            first_price = df['close_price'].iloc[0]
            yearly_change = df['close_price'] - first_price
            yearly_change_percent = (yearly_change / first_price) * 100
            
            return yearly_change, yearly_change_percent
        else:
            # Resample to yearly data (using year end)
            yearly_data = df.set_index('date').resample('YE').last()
            
            # Calculate yearly changes
            yearly_change = yearly_data['close_price'].diff()
            yearly_change_percent = (yearly_change / yearly_data['close_price'].shift(1)) * 100
            
            # Reindex back to original dates using forward fill
            yearly_change = yearly_change.reindex(df['date'], method='ffill')
            yearly_change_percent = yearly_change_percent.reindex(df['date'], method='ffill')
            
            return yearly_change, yearly_change_percent
    
    def update_yearly_changes(self, index_id: int, start_date: str = None, end_date: str = None):
        """Update yearly changes for a specific index"""
        try:
            # Get index data
            df = self.get_index_data(index_id, start_date, end_date)
            
            if df.empty:
                logger.warning(f"No data available for yearly calculation for index_id {index_id}")
                return
            
            # Calculate yearly changes
            yearly_change, yearly_change_percent = self.calculate_yearly_change(df)
            
            if yearly_change.empty:
                logger.warning(f"Could not calculate yearly changes for index_id {index_id}")
                return
            
            # Prepare data for update
            update_data = []
            for i, date in enumerate(df['date']):
                if pd.notna(yearly_change.iloc[i]) or pd.notna(yearly_change_percent.iloc[i]):
                    update_data.append({
                        'index_id': index_id,
                        'calculation_date': date.strftime('%Y-%m-%d'),
                        'yearly_change': yearly_change.iloc[i] if pd.notna(yearly_change.iloc[i]) else None,
                        'yearly_change_percent': yearly_change_percent.iloc[i] if pd.notna(yearly_change_percent.iloc[i]) else None
                    })
            
            if not update_data:
                logger.warning(f"No valid yearly changes to update for index_id {index_id}")
                return
            
            # Update database
            cursor = self.conn.cursor()
            
            for data in update_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO index_calculated_data 
                    (index_id, calculation_date, yearly_change, yearly_change_percent)
                    VALUES (?, ?, ?, ?)
                ''', (data['index_id'], data['calculation_date'], data['yearly_change'], data['yearly_change_percent']))
            
            self.conn.commit()
            logger.info(f"Updated yearly changes for {len(update_data)} records for index_id {index_id}")
            
        except Exception as e:
            logger.error(f"Failed to update yearly changes for index_id {index_id}: {e}")
            self.conn.rollback()
            raise
    
    def update_all_indices(self, symbols: List[str] = None, start_date: str = None, end_date: str = None):
        """Update yearly changes for all indices or specific symbols"""
        try:
            # Get indices to process
            if symbols:
                indices = self.get_indices_by_symbols(symbols)
            else:
                indices = self.get_all_indices()
            
            if not indices:
                logger.warning("No indices found to process")
                return
            
            logger.info(f"Processing yearly changes for {len(indices)} indices")
            
            success_count = 0
            error_count = 0
            
            for index in indices:
                try:
                    logger.info(f"Processing {index['name']} ({index['symbol']})")
                    self.update_yearly_changes(index['id'], start_date, end_date)
                    success_count += 1
                    logger.info(f"Successfully updated yearly changes for {index['name']}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to update yearly changes for {index['name']}: {e}")
                    continue
            
            logger.info(f"Yearly change update completed: {success_count} successful, {error_count} failed")
            
        except Exception as e:
            logger.error(f"Failed to update yearly changes: {e}")
            raise
    
    def get_yearly_change_summary(self, symbol: str = None) -> Dict[str, Any]:
        """Get summary of yearly changes for specific index or all indices"""
        try:
            cursor = self.conn.cursor()
            
            if symbol:
                # Get summary for specific symbol
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol,
                        COUNT(icd.id) as yearly_data_points,
                        AVG(icd.yearly_change) as avg_yearly_change,
                        AVG(icd.yearly_change_percent) as avg_yearly_change_percent,
                        MAX(icd.yearly_change_percent) as max_yearly_gain,
                        MIN(icd.yearly_change_percent) as max_yearly_loss,
                        SUM(CASE WHEN icd.yearly_change_percent > 0 THEN 1 ELSE 0 END) as positive_years,
                        SUM(CASE WHEN icd.yearly_change_percent < 0 THEN 1 ELSE 0 END) as negative_years
                    FROM indices_master im
                    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id
                    WHERE im.symbol = ? AND im.is_active = 1 AND icd.yearly_change IS NOT NULL
                    GROUP BY im.id, im.name, im.symbol
                '''
                cursor.execute(query, (symbol,))
                result = cursor.fetchone()
                
                if result:
                    total_years = result[2] if result[2] else 0
                    positive_years = result[7] if result[7] else 0
                    negative_years = result[8] if result[8] else 0
                    win_rate = (positive_years / total_years * 100) if total_years > 0 else 0
                    
                    # Calculate volatility manually
                    volatility_query = '''
                        SELECT yearly_change_percent 
                        FROM index_calculated_data icd
                        JOIN indices_master im ON icd.index_id = im.id
                        WHERE im.symbol = ? AND icd.yearly_change IS NOT NULL
                    '''
                    cursor.execute(volatility_query, (symbol,))
                    volatility_data = [row[0] for row in cursor.fetchall() if row[0] is not None]
                    
                    if len(volatility_data) > 1:
                        import statistics
                        volatility = statistics.stdev(volatility_data)
                    else:
                        volatility = 0
                    
                    return {
                        'name': result[0],
                        'symbol': result[1],
                        'yearly_data_points': result[2],
                        'avg_yearly_change': round(result[3], 2) if result[3] else None,
                        'avg_yearly_change_percent': round(result[4], 2) if result[4] else None,
                        'max_yearly_gain': round(result[5], 2) if result[5] else None,
                        'max_yearly_loss': round(result[6], 2) if result[6] else None,
                        'positive_years': positive_years,
                        'negative_years': negative_years,
                        'win_rate': round(win_rate, 1),
                        'volatility': round(volatility, 2)
                    }
                else:
                    return {'error': f'No yearly data found for symbol {symbol}'}
            else:
                # Get summary for all indices
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol,
                        COUNT(icd.id) as yearly_data_points,
                        AVG(icd.yearly_change) as avg_yearly_change,
                        AVG(icd.yearly_change_percent) as avg_yearly_change_percent,
                        MAX(icd.yearly_change_percent) as max_yearly_gain,
                        MIN(icd.yearly_change_percent) as max_yearly_loss,
                        SUM(CASE WHEN icd.yearly_change_percent > 0 THEN 1 ELSE 0 END) as positive_years,
                        SUM(CASE WHEN icd.yearly_change_percent < 0 THEN 1 ELSE 0 END) as negative_years
                    FROM indices_master im
                    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id
                    WHERE im.is_active = 1 AND icd.yearly_change IS NOT NULL
                    GROUP BY im.id, im.name, im.symbol
                    ORDER BY avg_yearly_change_percent DESC
                '''
                cursor.execute(query)
                results = cursor.fetchall()
                
                summary_list = []
                for result in results:
                    total_years = result[2] if result[2] else 0
                    positive_years = result[7] if result[7] else 0
                    negative_years = result[8] if result[8] else 0
                    win_rate = (positive_years / total_years * 100) if total_years > 0 else 0
                    
                    # Calculate volatility manually for each index
                    volatility_query = '''
                        SELECT yearly_change_percent 
                        FROM index_calculated_data icd
                        WHERE icd.index_id = ? AND icd.yearly_change IS NOT NULL
                    '''
                    cursor.execute(volatility_query, (result[0] if isinstance(result[0], int) else None,))
                    # Get the index_id properly
                    index_id_query = "SELECT id FROM indices_master WHERE symbol = ?"
                    cursor.execute(index_id_query, (result[1],))
                    index_id = cursor.fetchone()[0]
                    
                    cursor.execute(volatility_query, (index_id,))
                    volatility_data = [row[0] for row in cursor.fetchall() if row[0] is not None]
                    
                    if len(volatility_data) > 1:
                        import statistics
                        volatility = statistics.stdev(volatility_data)
                    else:
                        volatility = 0
                    
                    summary_list.append({
                        'name': result[0],
                        'symbol': result[1],
                        'yearly_data_points': result[2],
                        'avg_yearly_change': round(result[3], 2) if result[3] else None,
                        'avg_yearly_change_percent': round(result[4], 2) if result[4] else None,
                        'max_yearly_gain': round(result[5], 2) if result[5] else None,
                        'max_yearly_loss': round(result[6], 2) if result[6] else None,
                        'positive_years': positive_years,
                        'negative_years': negative_years,
                        'win_rate': round(win_rate, 1),
                        'volatility': round(volatility, 2)
                    })
                
                return summary_list
                
        except Exception as e:
            logger.error(f"Failed to get yearly change summary: {e}")
            raise

def main():
    """Main function to run yearly change calculation"""
    calculator = YearlyChangeCalculator()
    
    try:
        calculator.connect()
        
        # Update yearly changes for all indices
        logger.info("Starting yearly change calculation for all indices")
        calculator.update_all_indices()
        
        # Get summary of yearly changes
        summary = calculator.get_yearly_change_summary()
        logger.info(f"Yearly change summary for {len(summary)} indices")
        
        # Print summary for top 5 performers
        print("\n=== Yearly Change Summary (Top 5 Performers) ===")
        for i, item in enumerate(summary[:5]):
            print(f"{i+1}. {item['name']} ({item['symbol']})")
            print(f"   Data Points: {item['yearly_data_points']}")
            print(f"   Avg Yearly Change: {item['avg_yearly_change_percent']}%")
            print(f"   Best Year: {item['max_yearly_gain']}%")
            print(f"   Worst Year: {item['max_yearly_loss']}%")
            print(f"   Win Rate: {item['win_rate']}% ({item['positive_years']}/{item['positive_years'] + item['negative_years']} years)")
            print(f"   Volatility: {item['volatility']}%")
            print()
        
        # Print summary for bottom 5 performers
        print("\n=== Yearly Change Summary (Bottom 5 Performers) ===")
        for i, item in enumerate(summary[-5:]):
            print(f"{i+1}. {item['name']} ({item['symbol']})")
            print(f"   Data Points: {item['yearly_data_points']}")
            print(f"   Avg Yearly Change: {item['avg_yearly_change_percent']}%")
            print(f"   Best Year: {item['max_yearly_gain']}%")
            print(f"   Worst Year: {item['max_yearly_loss']}%")
            print(f"   Win Rate: {item['win_rate']}% ({item['positive_years']}/{item['positive_years'] + item['negative_years']} years)")
            print(f"   Volatility: {item['volatility']}%")
            print()
        
        # Print overall market statistics
        if summary:
            avg_market_return = sum(item['avg_yearly_change_percent'] for item in summary if item['avg_yearly_change_percent']) / len([item for item in summary if item['avg_yearly_change_percent']])
            avg_volatility = sum(item['volatility'] for item in summary if item['volatility']) / len([item for item in summary if item['volatility']])
            
            print("\n=== Overall Market Statistics ===")
            print(f"Average Market Return: {avg_market_return:.2f}%")
            print(f"Average Volatility: {avg_volatility:.2f}%")
            print(f"Total Indices Analyzed: {len(summary)}")
        
        logger.info("Yearly change calculation completed successfully")
        
    except Exception as e:
        logger.error(f"Yearly change calculation failed: {e}")
        raise
    finally:
        calculator.disconnect()

if __name__ == "__main__":
    main()
