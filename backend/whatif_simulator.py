import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class WhatIfSimulator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
    
    def get_niftybees_id(self) -> Optional[int]:
        """Get Niftybees index ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM indices_master WHERE symbol = 'NIFTYBEES'")
        result = cursor.fetchone()
        return result['id'] if result else None
    
    def get_niftybees_weekly_change(self, week_start_date: str) -> Optional[float]:
        """Get Niftybees weekly change for a specific week"""
        cursor = self.conn.cursor()
        
        week_end = (datetime.strptime(week_start_date, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        niftybees_id = self.get_niftybees_id()
        
        # Get most recent price on or before start date
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (niftybees_id, week_start_date))
        start_row = cursor.fetchone()
        
        # Get most recent price on or before end date
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (niftybees_id, week_end))
        end_row = cursor.fetchone()
        
        if start_row and end_row and start_row[0] and end_row[0] and start_row[0] != 0:
            return ((end_row[0] - start_row[0]) / start_row[0]) * 100
        
        return None
    
    def get_niftybees_monthly_change(self, month_start_date: str) -> Optional[float]:
        """Get Niftybees monthly change for a specific month"""
        cursor = self.conn.cursor()
        
        start_dt = datetime.strptime(month_start_date, '%Y-%m-%d')
        if start_dt.month == 12:
            next_month = start_dt.replace(year=start_dt.year + 1, month=1, day=1)
        else:
            next_month = start_dt.replace(month=start_dt.month + 1, day=1)
        month_end = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
        
        niftybees_id = self.get_niftybees_id()
        
        # Get most recent price on or before start date
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (niftybees_id, month_start_date))
        start_row = cursor.fetchone()
        
        # Get most recent price on or before end date
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (niftybees_id, month_end))
        end_row = cursor.fetchone()
        
        if start_row and end_row and start_row[0] and end_row[0] and start_row[0] != 0:
            return ((end_row[0] - start_row[0]) / start_row[0]) * 100
        
        return None
    
    def get_week_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate list of week start/end dates between start and end"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        weeks = []
        current = start
        # Start from the exact start date, not adjusted to Monday
        
        while current <= end:
            week_end = current + timedelta(days=6)
            weeks.append({
                'week_start_date': current.strftime('%Y-%m-%d'),
                'week_end_date': min(week_end, end).strftime('%Y-%m-%d') if week_end > end else week_end.strftime('%Y-%m-%d')
            })
            current += timedelta(days=7)
        
        return weeks
    
    def get_month_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate list of month start/end dates between start and end"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        months = []
        current = start.replace(day=1)
        
        while current <= end:
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1, day=1)
            else:
                next_month = current.replace(month=current.month + 1, day=1)
            month_end = next_month - timedelta(days=1)
            
            months.append({
                'month_start_date': current.strftime('%Y-%m-%d'),
                'month_end_date': month_end.strftime('%Y-%m-%d')
            })
            current = next_month
        
        return months
    
    def simulate_weekly(
        self,
        initial_amount: float,
        start_date: str,
        end_date: str,
        allocation_1: float = 50,
        allocation_2: float = 30,
        allocation_3: float = 20
    ) -> Dict[str, Any]:
        """Run weekly simulation"""
        strategy_value = initial_amount
        niftybees_value = initial_amount
        results = []
        period = 1
        
        weeks = self.get_week_dates(start_date, end_date)
        
        for week in weeks:
            week_start = week['week_start_date']
            week_end = week['week_end_date']
            
            # Get recommendations for this week
            recs = self.get_weekly_recommendations_for_week(week_start)
            
            strategy_value_start = strategy_value
            niftybees_value_start = niftybees_value
            
            # Calculate strategy value
            rec_1_symbol = None
            rec_2_symbol = None
            rec_3_symbol = None
            
            if recs and len(recs) >= 3:
                amount_1 = strategy_value * (allocation_1 / 100)
                amount_2 = strategy_value * (allocation_2 / 100)
                amount_3 = strategy_value * (allocation_3 / 100)
                
                change_1 = recs[0].get('weekly_change_percent', 0) or 0
                change_2 = recs[1].get('weekly_change_percent', 0) or 0
                change_3 = recs[2].get('weekly_change_percent', 0) or 0
                
                value_1 = amount_1 * (1 + change_1 / 100)
                value_2 = amount_2 * (1 + change_2 / 100)
                value_3 = amount_3 * (1 + change_3 / 100)
                
                strategy_value = value_1 + value_2 + value_3
                
                rec_1_symbol = recs[0].get('symbol')
                rec_2_symbol = recs[1].get('symbol')
                rec_3_symbol = recs[2].get('symbol')
            
            # Calculate Niftybees value
            niftybees_change = self.get_niftybees_weekly_change(week_start)
            if niftybees_change is not None:
                niftybees_value = niftybees_value * (1 + niftybees_change / 100)
            
            results.append({
                'period_number': period,
                'period_start_date': week_start,
                'period_end_date': week_end,
                'recommendation_1_symbol': rec_1_symbol,
                'recommendation_2_symbol': rec_2_symbol,
                'recommendation_3_symbol': rec_3_symbol,
                'allocation_1_percent': allocation_1,
                'allocation_2_percent': allocation_2,
                'allocation_3_percent': allocation_3,
                'amount_invested_1': round(amount_1, 2) if recs and len(recs) >= 3 else 0,
                'amount_invested_2': round(amount_2, 2) if recs and len(recs) >= 3 else 0,
                'amount_invested_3': round(amount_3, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_1': round(value_1, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_2': round(value_2, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_3': round(value_3, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_1': round(change_1, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_2': round(change_2, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_3': round(change_3, 2) if recs and len(recs) >= 3 else 0,
                'strategy_value_start': round(strategy_value_start, 2),
                'strategy_value_end': round(strategy_value, 2),
                'niftybees_value_start': round(niftybees_value_start, 2),
                'niftybees_value_end': round(niftybees_value, 2)
            })
            
            period += 1
        
        return {
            'results': results,
            'summary': {
                'initial_amount': initial_amount,
                'final_strategy_value': round(strategy_value, 2),
                'final_niftybees_value': round(niftybees_value, 2),
                'strategy_return_percent': round(((strategy_value - initial_amount) / initial_amount) * 100, 2),
                'niftybees_return_percent': round(((niftybees_value - initial_amount) / initial_amount) * 100, 2),
                'outperformance': round(((strategy_value - initial_amount) / initial_amount - (niftybees_value - initial_amount) / initial_amount) * 100, 2)
            }
        }
    
    def simulate_monthly(
        self,
        initial_amount: float,
        start_date: str,
        end_date: str,
        allocation_1: float = 50,
        allocation_2: float = 30,
        allocation_3: float = 20
    ) -> Dict[str, Any]:
        """Run monthly simulation"""
        strategy_value = initial_amount
        niftybees_value = initial_amount
        results = []
        period = 1
        
        months = self.get_month_dates(start_date, end_date)
        
        for month in months:
            month_start = month['month_start_date']
            month_end = month['month_end_date']
            
            # Get recommendations for this month
            recs = self.get_monthly_recommendations_for_month(month_start)
            
            strategy_value_start = strategy_value
            niftybees_value_start = niftybees_value
            
            # Calculate strategy value
            rec_1_symbol = None
            rec_2_symbol = None
            rec_3_symbol = None
            
            if recs and len(recs) >= 3:
                amount_1 = strategy_value * (allocation_1 / 100)
                amount_2 = strategy_value * (allocation_2 / 100)
                amount_3 = strategy_value * (allocation_3 / 100)
                
                change_1 = recs[0].get('monthly_change_percent', 0) or 0
                change_2 = recs[1].get('monthly_change_percent', 0) or 0
                change_3 = recs[2].get('monthly_change_percent', 0) or 0
                
                value_1 = amount_1 * (1 + change_1 / 100)
                value_2 = amount_2 * (1 + change_2 / 100)
                value_3 = amount_3 * (1 + change_3 / 100)
                
                strategy_value = value_1 + value_2 + value_3
                
                rec_1_symbol = recs[0].get('symbol')
                rec_2_symbol = recs[1].get('symbol')
                rec_3_symbol = recs[2].get('symbol')
            
            # Calculate Niftybees value
            niftybees_change = self.get_niftybees_monthly_change(month_start)
            if niftybees_change is not None:
                niftybees_value = niftybees_value * (1 + niftybees_change / 100)
            
            results.append({
                'period_number': period,
                'period_start_date': month_start,
                'period_end_date': month_end,
                'recommendation_1_symbol': rec_1_symbol,
                'recommendation_2_symbol': rec_2_symbol,
                'recommendation_3_symbol': rec_3_symbol,
                'allocation_1_percent': allocation_1,
                'allocation_2_percent': allocation_2,
                'allocation_3_percent': allocation_3,
                'amount_invested_1': round(amount_1, 2) if recs and len(recs) >= 3 else 0,
                'amount_invested_2': round(amount_2, 2) if recs and len(recs) >= 3 else 0,
                'amount_invested_3': round(amount_3, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_1': round(value_1, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_2': round(value_2, 2) if recs and len(recs) >= 3 else 0,
                'final_amount_3': round(value_3, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_1': round(change_1, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_2': round(change_2, 2) if recs and len(recs) >= 3 else 0,
                'return_percent_3': round(change_3, 2) if recs and len(recs) >= 3 else 0,
                'strategy_value_start': round(strategy_value_start, 2),
                'strategy_value_end': round(strategy_value, 2),
                'niftybees_value_start': round(niftybees_value_start, 2),
                'niftybees_value_end': round(niftybees_value, 2)
            })
            
            period += 1
        
        return {
            'results': results,
            'summary': {
                'initial_amount': initial_amount,
                'final_strategy_value': round(strategy_value, 2),
                'final_niftybees_value': round(niftybees_value, 2),
                'strategy_return_percent': round(((strategy_value - initial_amount) / initial_amount) * 100, 2),
                'niftybees_return_percent': round(((niftybees_value - initial_amount) / initial_amount) * 100, 2),
                'outperformance': round(((strategy_value - initial_amount) / initial_amount - (niftybees_value - initial_amount) / initial_amount) * 100, 2)
            }
        }
    
    def simulate(
        self,
        initial_amount: float,
        start_date: str,
        end_date: str,
        frequency: str = 'weekly',
        allocation_1: float = 50,
        allocation_2: float = 30,
        allocation_3: float = 20
    ) -> Dict[str, Any]:
        """Run simulation based on frequency"""
        if frequency == 'monthly':
            return self.simulate_monthly(initial_amount, start_date, end_date, allocation_1, allocation_2, allocation_3)
        return self.simulate_weekly(initial_amount, start_date, end_date, allocation_1, allocation_2, allocation_3)
    
    def save_scenario(
        self,
        name: str,
        description: str,
        initial_amount: float,
        frequency: str,
        allocation_1: float,
        allocation_2: float,
        allocation_3: float,
        start_date: str,
        end_date: str
    ) -> int:
        """Save a scenario to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO whatif_scenarios 
            (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date, end_date))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_scenarios(self) -> List[Dict]:
        """Get all scenarios"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM whatif_scenarios ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_scenario(self, scenario_id: int) -> Optional[Dict]:
        """Get a specific scenario"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM whatif_scenarios WHERE id = ?
        """, (scenario_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def update_scenario(self, scenario_id: int, **kwargs) -> bool:
        """Update a scenario"""
        allowed_fields = ['name', 'description', 'initial_amount', 'frequency', 
                          'allocation_1', 'allocation_2', 'allocation_3', 'start_date', 'end_date']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [scenario_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE whatif_scenarios SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_scenario(self, scenario_id: int) -> bool:
        """Delete a scenario"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM whatif_scenarios WHERE id = ?", (scenario_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_simulation_results(self, scenario_id: int, results: List[Dict]) -> None:
        """Save simulation results"""
        cursor = self.conn.cursor()
        
        # Delete existing results for this scenario
        cursor.execute("DELETE FROM whatif_simulation_results WHERE scenario_id = ?", (scenario_id,))
        
        # Insert new results
        for result in results:
            cursor.execute("""
                INSERT INTO whatif_simulation_results 
                (scenario_id, period_number, period_start_date, period_end_date,
                 recommendation_1_symbol, recommendation_2_symbol, recommendation_3_symbol,
                 allocation_1_percent, allocation_2_percent, allocation_3_percent,
                 amount_invested_1, amount_invested_2, amount_invested_3,
                 final_amount_1, final_amount_2, final_amount_3,
                 return_percent_1, return_percent_2, return_percent_3,
                 strategy_value_start, strategy_value_end, niftybees_value_start, niftybees_value_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario_id,
                result['period_number'],
                result['period_start_date'],
                result['period_end_date'],
                result.get('recommendation_1_symbol'),
                result.get('recommendation_2_symbol'),
                result.get('recommendation_3_symbol'),
                result['allocation_1_percent'],
                result['allocation_2_percent'],
                result['allocation_3_percent'],
                result.get('amount_invested_1', 0),
                result.get('amount_invested_2', 0),
                result.get('amount_invested_3', 0),
                result.get('final_amount_1', 0),
                result.get('final_amount_2', 0),
                result.get('final_amount_3', 0),
                result.get('return_percent_1', 0),
                result.get('return_percent_2', 0),
                result.get('return_percent_3', 0),
                result['strategy_value_start'],
                result['strategy_value_end'],
                result['niftybees_value_start'],
                result['niftybees_value_end']
            ))
        
        self.conn.commit()
    
    def get_simulation_results(self, scenario_id: int) -> List[Dict]:
        """Get simulation results for a scenario"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM whatif_simulation_results WHERE scenario_id = ? ORDER BY period_number
        """, (scenario_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_weekly_recommendations_for_week(self, week_start_date: str) -> List[Dict]:
        """Get top 3 weekly recommendations for a specific week"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.symbol,
                wr.weekly_change_percent,
                wr.three_week_cumulative_return
            FROM weekly_recommendations wr
            JOIN indices_master im ON wr.index_id = im.id
            WHERE wr.week_start_date = ? AND wr.rank <= 3
            ORDER BY wr.rank
        """, (week_start_date,))
        
        results = cursor.fetchall()
        if results:
            return [dict(row) for row in results]
        
        # Calculate recommendations if not in database
        return self._calculate_weekly_recommendations(week_start_date)
    
    def _calculate_weekly_recommendations(self, week_start_date: str) -> List[Dict]:
        """Calculate top 3 weekly recommendations for a week"""
        cursor = self.conn.cursor()
        
        # Get week end date (start + 6 days)
        week_end_date = (datetime.strptime(week_start_date, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        
        # Get all active indices
        cursor.execute("SELECT id, symbol FROM indices_master WHERE is_active = 1")
        all_indices = cursor.fetchall()
        
        index_returns = []
        for idx_id, symbol in all_indices:
            # Calculate 3-week cumulative return as of week end
            three_week_return = self._calculate_three_week_return(idx_id, week_end_date)
            
            # Get weekly change percent for this week
            cursor.execute("""
                SELECT weekly_change_percent
                FROM index_calculated_data
                WHERE index_id = ? AND calculation_date >= ? AND calculation_date <= ?
            """, (idx_id, week_start_date, week_end_date))
            result = cursor.fetchone()
            weekly_change = float(result[0]) if result and result[0] else None
            
            if three_week_return is not None:
                index_returns.append({
                    'id': idx_id,
                    'symbol': symbol,
                    'weekly_change_percent': weekly_change,
                    'three_week_cumulative_return': three_week_return
                })
        
        # Sort by 3W return and take top 3
        top_3 = sorted(index_returns, key=lambda x: x['three_week_cumulative_return'], reverse=True)[:3]
        
        # Store in database
        for rank, rec in enumerate(top_3, 1):
            cursor.execute("""
                INSERT OR REPLACE INTO weekly_recommendations 
                (index_id, week_start_date, week_end_date, rank, weekly_change_percent, 
                 three_week_cumulative_return, recommendation_date)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (rec['id'], week_start_date, week_end_date, rank, rec.get('weekly_change_percent'),
                  rec['three_week_cumulative_return']))
        self.conn.commit()
        
        return top_3
    
    def _calculate_three_week_return(self, index_id: int, end_date: str) -> Optional[float]:
        """Calculate 3-week cumulative return"""
        cursor = self.conn.cursor()
        
        # Get date 3 weeks before end date
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(weeks=3)
        start_date = start_dt.strftime('%Y-%m-%d')
        
        # Get price at start (first available <= start_date)
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date ASC LIMIT 1
        """, (index_id, start_date))
        start_row = cursor.fetchone()
        
        # Get price at end (latest available <= end_date)
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (index_id, end_date))
        end_row = cursor.fetchone()
        
        if start_row and end_row and start_row[0] and end_row[0] and start_row[0] != 0:
            return ((end_row[0] - start_row[0]) / start_row[0]) * 100
        
        return None
    
    def _calculate_three_month_return(self, index_id: int, end_date: str) -> Optional[float]:
        """Calculate 3-month cumulative return"""
        cursor = self.conn.cursor()
        
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=90)
        start_date = start_dt.strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date ASC LIMIT 1
        """, (index_id, start_date))
        start_row = cursor.fetchone()
        
        cursor.execute("""
            SELECT close_price FROM index_data
            WHERE index_id = ? AND date <= ?
            ORDER BY date DESC LIMIT 1
        """, (index_id, end_date))
        end_row = cursor.fetchone()
        
        if start_row and end_row and start_row[0] and end_row[0] and start_row[0] != 0:
            return ((end_row[0] - start_row[0]) / start_row[0]) * 100
        
        return None
    
    def get_monthly_recommendations_for_month(self, month_start_date: str) -> List[Dict]:
        """Get top 3 monthly recommendations for a specific month"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.symbol,
                mr.monthly_change_percent,
                mr.three_month_cumulative_return
            FROM monthly_recommendations mr
            JOIN indices_master im ON mr.index_id = im.id
            WHERE mr.month_start_date = ? AND mr.rank <= 3
            ORDER BY mr.rank
        """, (month_start_date,))
        
        results = cursor.fetchall()
        if results:
            return [dict(row) for row in results]
        
        # Calculate recommendations if not in database
        return self._calculate_monthly_recommendations(month_start_date)
    
    def _calculate_monthly_recommendations(self, month_start_date: str) -> List[Dict]:
        """Calculate top 3 monthly recommendations for a month"""
        cursor = self.conn.cursor()
        
        # Get month end date
        start_dt = datetime.strptime(month_start_date, '%Y-%m-%d')
        if start_dt.month == 12:
            next_month = start_dt.replace(year=start_dt.year + 1, month=1, day=1)
        else:
            next_month = start_dt.replace(month=start_dt.month + 1, day=1)
        month_end_date = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Get all active indices
        cursor.execute("SELECT id, symbol FROM indices_master WHERE is_active = 1")
        all_indices = cursor.fetchall()
        
        index_returns = []
        for idx_id, symbol in all_indices:
            # Calculate 3-month cumulative return
            three_month_return = self._calculate_three_month_return(idx_id, month_end_date)
            
            # Get monthly change percent for this month
            cursor.execute("""
                SELECT monthly_change_percent
                FROM index_calculated_data
                WHERE index_id = ? AND calculation_date >= ? AND calculation_date <= ?
            """, (idx_id, month_start_date, month_end_date))
            result = cursor.fetchone()
            monthly_change = float(result[0]) if result and result[0] else None
            
            if three_month_return is not None:
                index_returns.append({
                    'id': idx_id,
                    'symbol': symbol,
                    'monthly_change_percent': monthly_change,
                    'three_month_cumulative_return': three_month_return
                })
        
        # Sort by 3M return and take top 3
        top_3 = sorted(index_returns, key=lambda x: x['three_month_cumulative_return'], reverse=True)[:3]
        
        # Store in database
        for rank, rec in enumerate(top_3, 1):
            cursor.execute("""
                INSERT OR REPLACE INTO monthly_recommendations 
                (index_id, month_start_date, month_end_date, rank, monthly_change_percent, 
                 three_month_cumulative_return, recommendation_date)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (rec['id'], month_start_date, month_end_date, rank, rec.get('monthly_change_percent'),
                  rec['three_month_cumulative_return']))
        self.conn.commit()
        
        return top_3