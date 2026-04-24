import sqlite3
from datetime import datetime


class NiftybeesHelper:
    """Helper to get Niftybees performance data for comparison"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.niftybees_symbol = 'NIFTYBEES'
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
    
    def get_niftybees_id(self):
        """Get Niftybees index ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM indices_master WHERE symbol = ?",
            (self.niftybees_symbol,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def calculate_three_week_return(self, niftybees_id, end_date):
        """Calculate 3-week cumulative return as of end_date"""
        cursor = self.conn.cursor()
        
        # Get 21 trading days before end_date
        cursor.execute("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 22
        """, (niftybees_id, end_date))
        
        rows = cursor.fetchall()
        if len(rows) < 22:
            return None
        
        start_price = rows[-1]['close_price']
        end_price = rows[0]['close_price']
        
        if not start_price or not end_price or start_price == 0:
            return None
        
        return ((end_price - start_price) / start_price) * 100
    
    def calculate_three_month_return(self, niftybees_id, end_date):
        """Calculate 3-month cumulative return as of end_date"""
        cursor = self.conn.cursor()
        
        # Get ~63 trading days before end_date
        cursor.execute("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 64
        """, (niftybees_id, end_date))
        
        rows = cursor.fetchall()
        if len(rows) < 64:
            return None
        
        start_price = rows[-1]['close_price']
        end_price = rows[0]['close_price']
        
        if not start_price or not end_price or start_price == 0:
            return None
        
        return ((end_price - start_price) / start_price) * 100
    
    def get_weekly_change_for_week(self, week_start_date, week_end_date):
        """Get weekly change % for a specific week.
        
        Args:
            week_start_date: Start date of the week (YYYY-MM-DD)
            week_end_date: End date of the week (YYYY-MM-DD)
            
        Returns:
            dict: weekly_change_percent, calculation_date
        """
        cursor = self.conn.cursor()
        niftybees_id = self.get_niftybees_id()
        
        if not niftybees_id:
            return {'weekly_change_percent': None, 'calculation_date': None}
        
        # Get the calculated data for the week
        cursor.execute("""
            SELECT weekly_change_percent, calculation_date
            FROM index_calculated_data
            WHERE index_id = ?
            AND calculation_date >= ?
            AND calculation_date <= ?
            ORDER BY calculation_date DESC
            LIMIT 1
        """, (niftybees_id, week_start_date, week_end_date))
        
        result = cursor.fetchone()
        if result:
            return {
                'weekly_change_percent': float(result[0]) if result[0] else None,
                'calculation_date': result[1]
            }
        
        return {'weekly_change_percent': None, 'calculation_date': None}
    
    def get_monthly_change_for_month(self, month_start_date, month_end_date):
        """Get monthly change % for a specific month.
        
        Args:
            month_start_date: Start date of the month (YYYY-MM-DD)
            month_end_date: End date of the month (YYYY-MM-DD)
            
        Returns:
            dict: monthly_change_percent, calculation_date
        """
        cursor = self.conn.cursor()
        niftybees_id = self.get_niftybees_id()
        
        if not niftybees_id:
            return {'monthly_change_percent': None, 'calculation_date': None}
        
        # Get the calculated data for the month
        cursor.execute("""
            SELECT monthly_change_percent, calculation_date
            FROM index_calculated_data
            WHERE index_id = ?
            AND calculation_date >= ?
            AND calculation_date <= ?
            ORDER BY calculation_date DESC
            LIMIT 1
        """, (niftybees_id, month_start_date, month_end_date))
        
        result = cursor.fetchone()
        if result:
            return {
                'monthly_change_percent': float(result[0]) if result[0] else None,
                'calculation_date': result[1]
            }
        
        return {'monthly_change_percent': None, 'calculation_date': None}
    
    def get_weekly_comparison(self, week_start_date, week_end_date):
        """Get complete weekly comparison data for Niftybees.
        
        Returns:
            dict: all weekly comparison fields
        """
        cursor = self.conn.cursor()
        niftybees_id = self.get_niftybees_id()
        
        weekly_data = self.get_weekly_change_for_week(week_start_date, week_end_date)
        
        # Calculate 3W return as of week end date
        three_week_return = None
        if niftybees_id:
            three_week_return = self.calculate_three_week_return(niftybees_id, week_end_date)
        
        return {
            'niftybees_weekly_change_percent': weekly_data['weekly_change_percent'],
            'niftybees_three_week_cumulative_return': round(three_week_return, 4) if three_week_return else None,
            'calculation_date': weekly_data['calculation_date']
        }
    
    def get_monthly_comparison(self, month_start_date, month_end_date):
        """Get complete monthly comparison data for Niftybees.
        
        Returns:
            dict: all monthly comparison fields
        """
        cursor = self.conn.cursor()
        niftybees_id = self.get_niftybees_id()
        
        monthly_data = self.get_monthly_change_for_month(month_start_date, month_end_date)
        
        # Calculate 3M return as of month end date
        three_month_return = None
        if niftybees_id:
            three_month_return = self.calculate_three_month_return(niftybees_id, month_end_date)
        
        return {
            'niftybees_monthly_change_percent': monthly_data['monthly_change_percent'],
            'niftybees_three_month_cumulative_return': round(three_month_return, 4) if three_month_return else None,
            'calculation_date': monthly_data['calculation_date']
        }