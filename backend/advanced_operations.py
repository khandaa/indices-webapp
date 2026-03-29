#!/usr/bin/env python3
"""
Advanced functionality script for Indices Web Application
Provides flexible data loading and calculation capabilities
"""

import sqlite3
import yfinance as yf
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from data_loader import DataLoader
from data_calculator import DataCalculator

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'advanced_operations.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedOperations:
    """Handles advanced operations for flexible data management"""
    
    def __init__(self, db_path: str = None):
        """Initialize AdvancedOperations with database path"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'index-database.db')
        
        self.db_path = db_path
        self.data_loader = DataLoader(db_path)
        self.data_calculator = DataCalculator(db_path)
        
    def load_data_for_date_range(self, start_date: str, end_date: str, symbols: List[str] = None):
        """Load data for specific date range"""
        try:
            logger.info(f"Loading data for date range: {start_date} to {end_date}")
            
            self.data_loader.connect()
            
            if symbols:
                self.data_loader.load_data_for_specific_indices(symbols, start_date, end_date)
            else:
                self.data_loader.load_data_for_all_indices(start_date, end_date)
            
            logger.info(f"Data loading completed for date range: {start_date} to {end_date}")
            
        except Exception as e:
            logger.error(f"Failed to load data for date range: {e}")
            raise
        finally:
            self.data_loader.disconnect()
    
    def calculate_for_date_range(self, start_date: str, end_date: str, symbols: List[str] = None):
        """Calculate metrics for specific date range"""
        try:
            logger.info(f"Calculating metrics for date range: {start_date} to {end_date}")
            
            self.data_calculator.connect()
            
            if symbols:
                self.data_calculator.calculate_for_specific_indices(symbols, start_date, end_date)
            else:
                self.data_calculator.calculate_for_all_indices(start_date, end_date)
            
            logger.info(f"Calculation completed for date range: {start_date} to {end_date}")
            
        except Exception as e:
            logger.error(f"Failed to calculate for date range: {e}")
            raise
        finally:
            self.data_calculator.disconnect()
    
    def load_and_calculate_for_date_range(self, start_date: str, end_date: str, symbols: List[str] = None):
        """Load data and calculate metrics for specific date range"""
        try:
            logger.info(f"Loading and calculating for date range: {start_date} to {end_date}")
            
            # Load data first
            self.load_data_for_date_range(start_date, end_date, symbols)
            
            # Then calculate metrics
            self.calculate_for_date_range(start_date, end_date, symbols)
            
            logger.info(f"Load and calculate completed for date range: {start_date} to {end_date}")
            
        except Exception as e:
            logger.error(f"Failed to load and calculate for date range: {e}")
            raise
    
    def get_available_indices(self) -> List[Dict[str, Any]]:
        """Get list of all available indices"""
        try:
            self.data_loader.connect()
            indices = self.data_loader.get_all_indices()
            self.data_loader.disconnect()
            return indices
        except Exception as e:
            logger.error(f"Failed to get available indices: {e}")
            raise
    
    def get_data_summary(self, symbol: str = None) -> Dict[str, Any]:
        """Get summary of data for specific index or all indices"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if symbol:
                # Get data for specific symbol
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol, 
                        COUNT(id.id) as data_points,
                        MIN(id.date) as start_date,
                        MAX(id.date) as end_date,
                        AVG(id.close_price) as avg_price,
                        MAX(id.close_price) as max_price,
                        MIN(id.close_price) as min_price
                    FROM indices_master im
                    LEFT JOIN index_data id ON im.id = id.index_id
                    WHERE im.symbol = ? AND im.is_active = 1
                    GROUP BY im.id, im.name, im.symbol
                '''
                cursor.execute(query, (symbol,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'name': result[0],
                        'symbol': result[1],
                        'data_points': result[2],
                        'start_date': result[3],
                        'end_date': result[4],
                        'avg_price': round(result[5], 2) if result[5] else None,
                        'max_price': round(result[6], 2) if result[6] else None,
                        'min_price': round(result[7], 2) if result[7] else None
                    }
                else:
                    return {'error': f'Symbol {symbol} not found or not active'}
            else:
                # Get summary for all indices
                query = '''
                    SELECT 
                        im.name, 
                        im.symbol, 
                        COUNT(id.id) as data_points,
                        MIN(id.date) as start_date,
                        MAX(id.date) as end_date,
                        AVG(id.close_price) as avg_price,
                        MAX(id.close_price) as max_price,
                        MIN(id.close_price) as min_price
                    FROM indices_master im
                    LEFT JOIN index_data id ON im.id = id.index_id
                    WHERE im.is_active = 1
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
                        'data_points': result[2],
                        'start_date': result[3],
                        'end_date': result[4],
                        'avg_price': round(result[5], 2) if result[5] else None,
                        'max_price': round(result[6], 2) if result[6] else None,
                        'min_price': round(result[7], 2) if result[7] else None
                    })
                
                return summary_list
                
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            raise
        finally:
            conn.close()
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity and return report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            validation_results = {
                'total_indices': 0,
                'indices_with_data': 0,
                'indices_without_data': 0,
                'total_data_points': 0,
                'calculated_data_points': 0,
                'data_gaps': [],
                'issues': []
            }
            
            # Get total indices
            cursor.execute("SELECT COUNT(*) FROM indices_master WHERE is_active = 1")
            validation_results['total_indices'] = cursor.fetchone()[0]
            
            # Get indices with and without data
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT im.id) as with_data,
                    COUNT(DISTINCT CASE WHEN id.id IS NULL THEN im.id END) as without_data
                FROM indices_master im
                LEFT JOIN index_data id ON im.id = id.index_id
                WHERE im.is_active = 1
            ''')
            result = cursor.fetchone()
            validation_results['indices_with_data'] = result[0]
            validation_results['indices_without_data'] = result[1]
            
            # Get total data points
            cursor.execute("SELECT COUNT(*) FROM index_data")
            validation_results['total_data_points'] = cursor.fetchone()[0]
            
            # Get calculated data points
            cursor.execute("SELECT COUNT(*) FROM index_calculated_data")
            validation_results['calculated_data_points'] = cursor.fetchone()[0]
            
            # Check for data gaps (indices with less than expected data points)
            cursor.execute('''
                SELECT 
                    im.symbol, 
                    COUNT(id.id) as data_count
                FROM indices_master im
                LEFT JOIN index_data id ON im.id = id.index_id
                WHERE im.is_active = 1
                GROUP BY im.id, im.symbol
                HAVING data_count < 200
                ORDER BY data_count
            ''')
            gaps = cursor.fetchall()
            validation_results['data_gaps'] = [{'symbol': gap[0], 'data_count': gap[1]} for gap in gaps]
            
            # Check for issues
            if validation_results['indices_without_data'] > 0:
                validation_results['issues'].append(f"{validation_results['indices_without_data']} indices have no data")
            
            if validation_results['data_gaps']:
                validation_results['issues'].append(f"{len(validation_results['data_gaps'])} indices have insufficient data")
            
            conn.close()
            logger.info("Data validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate data integrity: {e}")
            raise

def main():
    """Main function for demonstration"""
    ops = AdvancedOperations()
    
    try:
        # Get available indices
        indices = ops.get_available_indices()
        print(f"Available indices: {len(indices)}")
        
        # Get data summary
        summary = ops.get_data_summary()
        print(f"Data summary for all indices: {len(summary)} indices with data")
        
        # Validate data integrity
        validation = ops.validate_data_integrity()
        print(f"Data validation: {validation}")
        
        # Example: Load data for specific date range
        # ops.load_and_calculate_for_date_range('2026-01-01', '2026-03-29', ['NIFTYBEES', 'GOLDBEES'])
        
    except Exception as e:
        logger.error(f"Advanced operations failed: {e}")
        raise

if __name__ == "__main__":
    main()
