import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class MomentumCalculator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def calculate_three_week_cumulative_return(self, index_id: int, end_date: Optional[str] = None) -> Optional[float]:
        """
        Calculate 3-week (21 trading days) cumulative return for an index
        
        Args:
            index_id: ID of the index
            end_date: End date for calculation (YYYY-MM-DD format). If None, uses latest available date.
            
        Returns:
            Cumulative return as percentage or None if insufficient data
        """
        if not self.conn:
            raise ValueError("Database connection not established")
        
        cursor = self.conn.cursor()
        
        # Get end date (latest available if not specified)
        if end_date:
            cursor.execute("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = ? AND date <= ?
            """, (index_id, end_date))
        else:
            cursor.execute("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = ?
            """, (index_id,))
        
        result = cursor.fetchone()
        if not result or not result['date']:
            return None
        
        latest_date = result['date']
        
        # Get start date (21 trading days before latest date)
        cursor.execute("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 22
        """, (index_id, latest_date))
        
        rows = cursor.fetchall()
        
        if len(rows) < 22:  # Need at least 22 days of data (21 periods)
            return None
        
        start_price = rows[-1]['close_price']  # 21st day back
        end_price = rows[0]['close_price']    # Latest day
        
        if start_price is None or end_price is None or start_price == 0:
            return None
        
        # Calculate cumulative return as percentage
        cumulative_return = ((end_price - start_price) / start_price) * 100
        return round(cumulative_return, 4)
    
    def calculate_three_month_cumulative_return(self, index_id: int, end_date: Optional[str] = None) -> Optional[float]:
        """
        Calculate 3-month (approximately 63 trading days) cumulative return for an index
        
        Args:
            index_id: ID of the index
            end_date: End date for calculation (YYYY-MM-DD format). If None, uses latest available date.
            
        Returns:
            Cumulative return as percentage or None if insufficient data
        """
        if not self.conn:
            raise ValueError("Database connection not established")
        
        cursor = self.conn.cursor()
        
        # Get end date (latest available if not specified)
        if end_date:
            cursor.execute("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = ? AND date <= ?
            """, (index_id, end_date))
        else:
            cursor.execute("""
                SELECT MAX(date) as date 
                FROM index_data 
                WHERE index_id = ?
            """, (index_id,))
        
        result = cursor.fetchone()
        if not result or not result['date']:
            return None
        
        latest_date = result['date']
        
        # Get start date (63 trading days before latest date)
        cursor.execute("""
            SELECT date, close_price
            FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC
            LIMIT 64
        """, (index_id, latest_date))
        
        rows = cursor.fetchall()
        
        if len(rows) < 64:  # Need at least 64 days of data (63 periods)
            return None
        
        start_price = rows[-1]['close_price']  # 63rd day back
        end_price = rows[0]['close_price']    # Latest day
        
        if start_price is None or end_price is None or start_price == 0:
            return None
        
        # Calculate cumulative return as percentage
        cumulative_return = ((end_price - start_price) / start_price) * 100
        return round(cumulative_return, 4)
    
    def calculate_all_momentum_metrics(self, index_id: int, end_date: Optional[str] = None) -> Dict[str, Optional[float]]:
        """
        Calculate all momentum metrics for an index
        
        Args:
            index_id: ID of the index
            end_date: End date for calculation (YYYY-MM-DD format). If None, uses latest available date.
            
        Returns:
            Dictionary with momentum metrics
        """
        return {
            'three_week_cumulative_return': self.calculate_three_week_cumulative_return(index_id, end_date),
            'three_month_cumulative_return': self.calculate_three_month_cumulative_return(index_id, end_date)
        }
    
    def update_momentum_data_for_all_indices(self, calculation_date: Optional[str] = None):
        """
        Update momentum data for all active indices
        
        Args:
            calculation_date: Date to use for calculations (YYYY-MM-DD format). If None, uses current date.
        """
        if not self.conn:
            raise ValueError("Database connection not established")
        
        cursor = self.conn.cursor()
        
        # Get all active indices
        cursor.execute("SELECT id FROM indices_master WHERE is_active = 1")
        indices = cursor.fetchall()
        
        if not calculation_date:
            calculation_date = datetime.now().strftime('%Y-%m-%d')
        
        updated_count = 0
        for index_row in indices:
            index_id = index_row['id']
            
            # Calculate momentum metrics
            momentum_data = self.calculate_all_momentum_metrics(index_id)
            
            # Check if we already have data for this date
            cursor.execute("""
                SELECT id FROM index_momentum_data 
                WHERE index_id = ? AND calculation_date = ?
            """, (index_id, calculation_date))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE index_momentum_data 
                    SET three_week_cumulative_return = ?, 
                        three_month_cumulative_return = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE index_id = ? AND calculation_date = ?
                """, (
                    momentum_data['three_week_cumulative_return'],
                    momentum_data['three_month_cumulative_return'],
                    index_id,
                    calculation_date
                ))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO index_momentum_data 
                    (index_id, calculation_date, three_week_cumulative_return, three_month_cumulative_return)
                    VALUES (?, ?, ?, ?)
                """, (
                    index_id,
                    calculation_date,
                    momentum_data['three_week_cumulative_return'],
                    momentum_data['three_month_cumulative_return']
                ))
            
            updated_count += 1
        
        self.conn.commit()
        return updated_count
    
    def get_latest_momentum_data(self, index_id: int) -> Dict[str, Any]:
        """
        Get the latest momentum data for an index
        
        Args:
            index_id: ID of the index
            
        Returns:
            Dictionary with latest momentum data
        """
        if not self.conn:
            raise ValueError("Database connection not established")
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT three_week_cumulative_return, three_month_cumulative_return, calculation_date
            FROM index_momentum_data
            WHERE index_id = ?
            ORDER BY calculation_date DESC
            LIMIT 1
        """, (index_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return {
                'three_week_cumulative_return': None,
                'three_month_cumulative_return': None,
                'calculation_date': None
            }
        
        return {
            'three_week_cumulative_return': float(result['three_week_cumulative_return']) if result['three_week_cumulative_return'] else None,
            'three_month_cumulative_return': float(result['three_month_cumulative_return']) if result['three_month_cumulative_return'] else None,
            'calculation_date': result['calculation_date']
        }
