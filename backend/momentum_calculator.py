import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# os.environ['DB_TYPE'] = 'mysql'

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from db import Database


class MomentumCalculator:
    def __init__(self, db_type: str = 'mysql'):
        self.db_type = db_type
        self.db = Database(db_type)
    
    def connect(self):
        """Connect to the database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from the database"""
        self.db.close()
    
    def calculate_three_week_cumulative_return(self, index_id: int, end_date: Optional[str] = None) -> Optional[float]:
        """Calculate 3-week (21 trading days) cumulative return for an index"""
        if end_date:
            result = self.db.fetch_one("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = %s AND date <= %s
            """, (index_id, end_date))
        else:
            result = self.db.fetch_one("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = %s
            """, (index_id,))
        
        if not result or not result.get('date'):
            return None
        
        latest_date = result['date']
        
        results = self.db.fetch_all("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = %s AND date <= %s
            ORDER BY date DESC
            LIMIT 22
        """, (index_id, latest_date))
        
        if len(results) < 22:
            return None
        
        start_price = results[-1]['close_price']
        end_price = results[0]['close_price']
        
        if start_price is None or end_price is None or start_price == 0:
            return None
        
        cumulative_return = ((end_price - start_price) / start_price) * 100
        return round(cumulative_return, 4)
    
    def calculate_three_month_cumulative_return(self, index_id: int, end_date: Optional[str] = None) -> Optional[float]:
        """Calculate 3-month cumulative return for an index"""
        if end_date:
            result = self.db.fetch_one("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = %s AND date <= %s
            """, (index_id, end_date))
        else:
            result = self.db.fetch_one("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = %s
            """, (index_id,))
        
        if not result or not result.get('date'):
            return None
        
        latest_date = result['date']
        
        results = self.db.fetch_all("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = %s AND date <= %s
            ORDER BY date DESC
            LIMIT 64
        """, (index_id, latest_date))
        
        if len(results) < 64:
            return None
        
        start_price = results[-1]['close_price']
        end_price = results[0]['close_price']
        
        if start_price is None or end_price is None or start_price == 0:
            return None
        
        cumulative_return = ((end_price - start_price) / start_price) * 100
        return round(cumulative_return, 4)
    
    def calculate_all_momentum(self, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Calculate momentum for all active indices"""
        indices = self.db.fetch_all("SELECT id, symbol FROM indices_master WHERE is_active = 1")
        
        results = []
        for idx in indices:
            three_week = self.calculate_three_week_cumulative_return(idx['id'], end_date)
            three_month = self.calculate_three_month_cumulative_return(idx['id'], end_date)
            
            results.append({
                'index_id': idx['id'],
                'symbol': idx['symbol'],
                'three_week_cumulative_return': three_week,
                'three_month_cumulative_return': three_month
            })
        
        return results
    
    def save_momentum_data(self, index_id: int, end_date: str) -> bool:
        """Save momentum data for an index"""
        three_week = self.calculate_three_week_cumulative_return(index_id, end_date)
        three_month = self.calculate_three_month_cumulative_return(index_id, end_date)
        
        existing = self.db.fetch_one("""
            SELECT id FROM index_momentum_data 
            WHERE index_id = %s AND calculation_date = %s
        """, (index_id, end_date))
        
        if existing:
            self.db.execute("""
                UPDATE index_momentum_data 
                SET three_week_cumulative_return = %s, three_month_cumulative_return = %s, updated_at = NOW()
                WHERE index_id = %s AND calculation_date = %s
            """, (three_week, three_month, index_id, end_date))
        else:
            self.db.execute("""
                INSERT INTO index_momentum_data 
                (index_id, calculation_date, three_week_cumulative_return, three_month_cumulative_return)
                VALUES (%s, %s, %s, %s)
            """, (index_id, end_date, three_week, three_month))
        
        return True
    
    def get_momentum_data(self, index_id: int, end_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get saved momentum data for an index"""
        if end_date:
            return self.db.fetch_one("""
                SELECT * FROM index_momentum_data 
                WHERE index_id = %s AND calculation_date = %s
            """, (index_id, end_date))
        else:
            return self.db.fetch_one("""
                SELECT * FROM index_momentum_data 
                WHERE index_id = %s
                ORDER BY calculation_date DESC
                LIMIT 1
            """, (index_id,))
    
    def get_latest_momentum_data(self, index_id: int):
        """Get latest momentum data for an index"""
        return self.get_momentum_data(index_id)