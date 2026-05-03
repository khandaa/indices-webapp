import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# os.environ['DB_TYPE'] = 'mysql'

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from db import Database


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