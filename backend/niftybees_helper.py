import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# os.environ['DB_TYPE'] = 'mysql'

from datetime import datetime

from db import Database


class NiftybeesHelper:
    """Helper to get Niftybees performance data for comparison"""
    
    def __init__(self, db_type='mysql'):
        self.db_type = db_type
        self.db = Database(db_type)
        self.niftybees_symbol = 'NIFTYBEES'
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.close()
    
    def get_niftybees_id(self):
        """Get Niftybees index ID"""
        result = self.db.fetch_one(
            "SELECT id FROM indices_master WHERE symbol = %s",
            (self.niftybees_symbol,)
        )
        return result['id'] if result else None
    
    def calculate_three_week_return(self, niftybees_id, end_date):
        """Calculate 3-week cumulative return as of end_date"""
        results = self.db.fetch_all("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = %s AND date <= %s
            ORDER BY date DESC
            LIMIT 22
        """, (niftybees_id, end_date))
        
        if len(results) < 22:
            return None
        
        start_price = results[-1]['close_price']
        end_price = results[0]['close_price']
        
        if not start_price or not end_price or start_price == 0:
            return None
        
        return ((end_price - start_price) / start_price) * 100
    
    def calculate_three_month_return(self, niftybees_id, end_date):
        """Calculate 3-month cumulative return as of end_date"""
        results = self.db.fetch_all("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = %s AND date <= %s
            ORDER BY date DESC
            LIMIT 64
        """, (niftybees_id, end_date))
        
        if len(results) < 64:
            return None
        
        start_price = results[-1]['close_price']
        end_price = results[0]['close_price']
        
        if not start_price or not end_price or start_price == 0:
            return None
        
        return ((end_price - start_price) / start_price) * 100
    
    def get_weekly_change_for_week(self, week_start_date, week_end_date):
        """Get weekly change % for a specific week."""
        niftybees_id = self.get_niftybees_id()
        
        if not niftybees_id:
            return {'weekly_change_percent': None, 'calculation_date': None}
        
        result = self.db.fetch_one("""
            SELECT weekly_change_percent, calculation_date
            FROM index_calculated_data
            WHERE index_id = %s
            AND calculation_date >= %s
            AND calculation_date <= %s
            ORDER BY calculation_date DESC
            LIMIT 1
        """, (niftybees_id, week_start_date, week_end_date))
        
        if result:
            return {
                'weekly_change_percent': float(result['weekly_change_percent']) if result['weekly_change_percent'] else None,
                'calculation_date': result['calculation_date']
            }
        
        return {'weekly_change_percent': None, 'calculation_date': None}
    
    def get_monthly_change_for_month(self, month_start_date, month_end_date):
        """Get monthly change % for a specific month."""
        niftybees_id = self.get_niftybees_id()
        
        if not niftybees_id:
            return {'monthly_change_percent': None, 'calculation_date': None}
        
        result = self.db.fetch_one("""
            SELECT monthly_change_percent, calculation_date
            FROM index_calculated_data
            WHERE index_id = %s
            AND calculation_date >= %s
            AND calculation_date <= %s
            ORDER BY calculation_date DESC
            LIMIT 1
        """, (niftybees_id, month_start_date, month_end_date))
        
        if result:
            return {
                'monthly_change_percent': float(result['monthly_change_percent']) if result['monthly_change_percent'] else None,
                'calculation_date': result['calculation_date']
            }
        
        return {'monthly_change_percent': None, 'calculation_date': None}
    
    def get_weekly_comparison(self, week_start_date, week_end_date):
        """Get complete weekly comparison data for Niftybees."""
        niftybees_id = self.get_niftybees_id()
        
        weekly_data = self.get_weekly_change_for_week(week_start_date, week_end_date)
        
        three_week_return = None
        if niftybees_id:
            three_week_return = self.calculate_three_week_return(niftybees_id, week_end_date)
        
        return {
            'niftybees_weekly_change_percent': weekly_data['weekly_change_percent'],
            'niftybees_three_week_cumulative_return': round(three_week_return, 4) if three_week_return else None,
            'calculation_date': weekly_data['calculation_date']
        }
    
    def get_monthly_comparison(self, month_start_date, month_end_date):
        """Get complete monthly comparison data for Niftybees."""
        niftybees_id = self.get_niftybees_id()
        
        monthly_data = self.get_monthly_change_for_month(month_start_date, month_end_date)
        
        three_month_return = None
        if niftybees_id:
            three_month_return = self.calculate_three_month_return(niftybees_id, month_end_date)
        
        return {
            'niftybees_monthly_change_percent': monthly_data['monthly_change_percent'],
            'niftybees_three_month_cumulative_return': round(three_month_return, 4) if three_month_return else None,
            'calculation_date': monthly_data['calculation_date']
        }