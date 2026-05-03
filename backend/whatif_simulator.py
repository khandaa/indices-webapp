import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ['DB_TYPE'] = 'mysql'

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from db import Database
from config import get_backend_url


class WhatIfSimulator:
    def __init__(self, db_type: str = 'mysql'):
        self.db_type = db_type
        self.db = Database(db_type)
    
    def connect(self):
        """Connect to database"""
        self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.close()
    
    def get_scenarios(self) -> List[Dict[str, Any]]:
        """Get all scenarios"""
        results = self.db.fetch_all("SELECT * FROM whatif_scenarios ORDER BY created_at DESC")
        return results
    
    def get_scenario(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific scenario"""
        return self.db.fetch_one("SELECT * FROM whatif_scenarios WHERE id = %s", (scenario_id,))
    
    def create_scenario(self, name: str, description: str, initial_amount: float, 
                   frequency: str, allocation_1: float, allocation_2: float, 
                   allocation_3: float, start_date: str) -> int:
        """Create a new scenario"""
        return self.db.execute("""
            INSERT INTO whatif_scenarios 
            (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date))
    
    def save_scenario(self, name: str, description: str = "", initial_amount: float = 100000,
                   frequency: str = "weekly", allocation_1: float = 50, allocation_2: float = 30,
                   allocation_3: float = 20, start_date: str = None, end_date: str = None) -> int:
        """Create a new scenario (alias for create_scenario)"""
        return self.db.execute("""
            INSERT INTO whatif_scenarios 
            (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, description, initial_amount, frequency, allocation_1, allocation_2, allocation_3, start_date, end_date))
    
    def update_scenario(self, scenario_id: int, **kwargs) -> bool:
        """Update a scenario"""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{k} = %s" for k in kwargs.keys()])
        values = list(kwargs.values()) + [scenario_id]
        
        self.db.execute(f"UPDATE whatif_scenarios SET {set_clause} WHERE id = %s", values)
        return True
    
    def delete_scenario(self, scenario_id: int) -> bool:
        """Delete a scenario"""
        self.db.execute("DELETE FROM whatif_simulation_results WHERE scenario_id = %s", (scenario_id,))
        self.db.execute("DELETE FROM whatif_scenarios WHERE id = %s", (scenario_id,))
        return True
    
    def get_simulation_results(self, scenario_id: int) -> List[Dict[str, Any]]:
        """Get all simulation results for a scenario"""
        return self.db.fetch_all("""
            SELECT * FROM whatif_simulation_results 
            WHERE scenario_id = %s 
            ORDER BY period_number
        """, (scenario_id,))
    
    def add_simulation_result(self, scenario_id: int, period_number: int,
                              period_start_date: str, period_end_date: str,
                              recommendation_1_symbol: str, recommendation_2_symbol: str,
                              recommendation_3_symbol: str, allocation_1_percent: float,
                              allocation_2_percent: float, allocation_3_percent: float,
                              strategy_value_start: float, strategy_value_end: float,
                              niftybees_value_start: float, niftybees_value_end: float) -> int:
        """Add a simulation result"""
        return self.db.execute("""
            INSERT INTO whatif_simulation_results
            (scenario_id, period_number, period_start_date, period_end_date,
             recommendation_1_symbol, recommendation_2_symbol, recommendation_3_symbol,
             allocation_1_percent, allocation_2_percent, allocation_3_percent,
             strategy_value_start, strategy_value_end, niftybees_value_start, niftybees_value_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (scenario_id, period_number, period_start_date, period_end_date,
             recommendation_1_symbol, recommendation_2_symbol, recommendation_3_symbol,
             allocation_1_percent, allocation_2_percent, allocation_3_percent,
             strategy_value_start, strategy_value_end, niftybees_value_start, niftybees_value_end))
    
    def clear_simulation_results(self, scenario_id: int) -> bool:
        """Clear all simulation results for a scenario"""
        self.db.execute("DELETE FROM whatif_simulation_results WHERE scenario_id = %s", (scenario_id,))
        return True
    
    def get_performance_summary(self, scenario_id: int) -> Dict[str, Any]:
        """Get performance summary for a scenario"""
        results = self.db.fetch_one("""
            SELECT 
                SUM(CASE WHEN period_number = 1 THEN strategy_value_start ELSE 0 END) as initial_strategy_value,
                SUM(strategy_value_end) as final_strategy_value,
                SUM(niftybees_value_start) as initial_niftybees_value,
                SUM(niftybees_value_end) as final_niftybees_value,
                COUNT(*) as num_periods
            FROM whatif_simulation_results 
            WHERE scenario_id = %s
        """, (scenario_id,))
        
        if not results or not results.get('final_strategy_value'):
            return {}
        
        initial = results.get('initial_strategy_value', 0)
        final = results.get('final_strategy_value', 0)
        nifty_initial = results.get('initial_niftybees_value', 0)
        nifty_final = results.get('final_niftybees_value', 0)
        
        return {
            'initial_value': initial,
            'final_value': final,
            'strategy_return': ((final - initial) / initial * 100) if initial > 0 else None,
            'niftybees_initial_value': nifty_initial,
            'niftybees_final_value': nifty_final,
            'niftybees_return': ((nifty_final - nifty_initial) / nifty_initial * 100) if nifty_initial > 0 else None,
            'num_periods': results.get('num_periods', 0)
        }
    
    def simulate(self, initial_amount: float = 100000, start_date: str = None, end_date: str = None,
              frequency: str = "weekly", allocation_1: float = 50, allocation_2: float = 30,
              allocation_3: float = 20) -> Dict[str, Any]:
        """Run investment simulation based on recommendations"""
        import requests as req
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        backend_url = get_backend_url()
        recommendations_endpoint = f"{backend_url}/api/recommendations/{frequency}" if frequency == "weekly" else f"{backend_url}/api/recommendations/monthly"
        
        try:
            if frequency == "weekly":
                resp = req.get(f"{backend_url}/api/recommendations/weekly?past_weeks=52&include_upcoming=false")
            else:
                resp = req.get(f"{backend_url}/api/recommendations/monthly?past_months=12&include_upcoming=False")
            recommendations_data = resp.json()
        except Exception as e:
            return {'error': f'Failed to fetch recommendations: {str(e)}', 'results': []}
        
        results = []
        periods = recommendations_data.get('weeks' if frequency == 'weekly' else 'months', [])
        
        niftybees_cursor = self.db.fetch_one("""
            SELECT close_price FROM index_data 
            WHERE index_id = (SELECT id FROM indices_master WHERE symbol = 'NIFTYBEES')
            AND date <= %s ORDER BY date DESC LIMIT 1
        """, (start_date,))
        niftybees_price_start = niftybees_cursor.get('close_price', 0) if niftybees_cursor else 0
        
        niftybees_cursor = self.db.fetch_one("""
            SELECT close_price FROM index_data 
            WHERE index_id = (SELECT id FROM indices_master WHERE symbol = 'NIFTYBEES')
            AND date <= %s ORDER BY date DESC LIMIT 1
        """, (end_date,))
        niftybees_price_end = niftybees_cursor.get('close_price', 0) if niftybees_cursor else 0
        
        strategy_value = initial_amount
        niftybees_value = initial_amount
        
        for period in periods[:10]:
            period_key = 'week' if frequency == 'weekly' else 'month'
            period_info = period.get(period_key, '')
            recs = period.get('recommendations', [])
            
            if not recs:
                continue
                
            rec_1 = recs[0] if len(recs) > 0 else {}
            rec_2 = recs[1] if len(recs) > 1 else {}
            rec_3 = recs[2] if len(recs) > 2 else {}
            
            rec_1_return = rec_1.get('three_week_cumulative_return', 0) or rec_1.get('three_month_cumulative_return', 0) or 0
            rec_2_return = rec_2.get('three_week_cumulative_return', 0) or rec_2.get('three_month_cumulative_return', 0) or 0
            rec_3_return = rec_3.get('three_week_cumulative_return', 0) or rec_3.get('three_month_cumulative_return', 0) or 0
            
            strategy_return_pct = (rec_1_return * allocation_1 + rec_2_return * allocation_2 + rec_3_return * allocation_3) / 100
            
            strategy_value = strategy_value * (1 + strategy_return_pct / 100)
            niftybees_return = ((niftybees_price_end - niftybees_price_start) / niftybees_price_start * 100) if niftybees_price_start > 0 else 0
            niftybees_value = niftybees_value * (1 + niftybees_return / 100)
            
            results.append({
                'period': period_info,
                'recommendations': [
                    {'symbol': rec_1.get('symbol', ''), 'return': rec_1_return},
                    {'symbol': rec_2.get('symbol', ''), 'return': rec_2_return},
                    {'symbol': rec_3.get('symbol', ''), 'return': rec_3_return}
                ],
                'strategy_value': strategy_value,
                'niftybees_value': niftybees_value,
                'strategy_return': strategy_return_pct
            })
            
            niftybees_price_start = niftybees_price_end
        
        return {
            'initial_amount': initial_amount,
            'final_strategy_value': strategy_value,
            'final_niftybees_value': niftybees_value,
            'strategy_return': ((strategy_value - initial_amount) / initial_amount * 100) if initial_amount > 0 else 0,
            'niftybees_return': ((niftybees_value - initial_amount) / initial_amount * 100) if initial_amount > 0 else 0,
            'results': results
        }
    
    def save_simulation_results(self, scenario_id: int, results: List[Dict[str, Any]]) -> bool:
        """Save simulation results for a scenario"""
        for i, result in enumerate(results):
            self.add_simulation_result(
                scenario_id=scenario_id,
                period_number=i + 1,
                period_start_date=result.get('period', ''),
                period_end_date=result.get('period', ''),
                recommendation_1_symbol=result.get('recommendations', [{}])[0].get('symbol', ''),
                recommendation_2_symbol=result.get('recommendations', [{}])[1].get('symbol', ''),
                recommendation_3_symbol=result.get('recommendations', [{}])[2].get('symbol', ''),
                allocation_1_percent=50,
                allocation_2_percent=30,
                allocation_3_percent=20,
                strategy_value_start=result.get('strategy_value', 0),
                strategy_value_end=result.get('strategy_value', 0),
                niftybees_value_start=result.get('niftybees_value', 0),
                niftybees_value_end=result.get('niftybees_value', 0)
            )
        return True