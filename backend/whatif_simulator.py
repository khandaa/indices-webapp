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
    
    def get_weekly_recommendations_for_week(self, week_start_date: str) -> List[Dict]:
        """Get top 3 recommendations for a specific week"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT wr.index_id, im.symbol, im.name, wr.rank, wr.weekly_change_percent
            FROM weekly_recommendations wr
            JOIN indices_master im ON wr.index_id = im.id
            WHERE wr.week_start_date = ?
            ORDER BY wr.rank
            LIMIT 3
        """, (week_start_date,))
        
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_monthly_recommendations_for_month(self, month_start_date: str) -> List[Dict]:
        """Get top 3 recommendations for a specific month"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT wr.index_id, im.symbol, im.name, wr.rank, wr.monthly_change_percent
            FROM monthly_recommendations wr
            JOIN indices_master im ON wr.index_id = im.id
            WHERE wr.month_start_date = ?
            ORDER BY wr.rank
            LIMIT 3
        """, (month_start_date,))
        
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_niftybees_weekly_change(self, week_start_date: str) -> Optional[float]:
        """Get Niftybees weekly change for a specific week"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT niftybees_weekly_change_percent
            FROM weekly_recommendations
            WHERE week_start_date = ? AND index_id = ?
        """, (week_start_date, self.get_niftybees_id()))
        
        result = cursor.fetchone()
        return result['niftybees_weekly_change_percent'] if result else None
    
    def get_niftybees_monthly_change(self, month_start_date: str) -> Optional[float]:
        """Get Niftybees monthly change for a specific month"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT niftybees_monthly_change_percent
            FROM monthly_recommendations
            WHERE month_start_date = ? AND index_id = ?
        """, (month_start_date, self.get_niftybees_id()))
        
        result = cursor.fetchone()
        return result['niftybees_monthly_change_percent'] if result else None
    
    def get_week_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate list of week start/end dates between start and end"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT week_start_date, week_end_date
            FROM weekly_recommendations
            WHERE week_start_date >= ? AND week_start_date <= ?
            ORDER BY week_start_date
        """, (start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_month_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate list of month start/end dates between start and end"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT month_start_date, month_end_date
            FROM monthly_recommendations
            WHERE month_start_date >= ? AND month_start_date <= ?
            ORDER BY month_start_date
        """, (start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
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
                 strategy_value_start, strategy_value_end, niftybees_value_start, niftybees_value_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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