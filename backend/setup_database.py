#!/usr/bin/env python3
"""
Database setup script for Indices Web Application
Creates SQLite database with all required tables and initial data
"""

import sqlite3
import os
import logging
from datetime import datetime

def setup_database():
    """Create database and all tables"""
    
    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Database path
    db_path = os.path.join(db_dir, 'index-database.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create indices_master table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indices_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL UNIQUE,
                index_type TEXT NOT NULL CHECK (index_type IN (
                    'precious_metal', 'nifty', 'sector', 'thematic', 
                    'liquid_fund', 'smallcap', 'midcap', 'largecap'
                )),
                description TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create index_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                open_price REAL,
                close_price REAL,
                high_price REAL,
                low_price REAL,
                volume INTEGER,
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES indices_master (id),
                UNIQUE(index_id, date)
            )
        ''')
        
        # Create index_calculated_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_calculated_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                calculation_date TEXT NOT NULL,
                daily_change REAL,
                weekly_change REAL,
                monthly_change REAL,
                yearly_change REAL,
                daily_change_percent REAL,
                weekly_change_percent REAL,
                monthly_change_percent REAL,
                yearly_change_percent REAL,
                FOREIGN KEY (index_id) REFERENCES indices_master (id),
                UNIQUE(index_id, calculation_date)
            )
        ''')
        
        # Create index_momentum_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_momentum_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                calculation_date TEXT NOT NULL,
                three_week_cumulative_return REAL,
                three_month_cumulative_return REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES indices_master (id),
                UNIQUE(index_id, calculation_date)
            )
        ''')
        
        # Create user_settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                refresh_interval INTEGER DEFAULT 300,
                theme TEXT DEFAULT 'light',
                language TEXT DEFAULT 'en'
            )
        ''')
        
        # Create index_recommendations table (Task 1.1)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                is_selected BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES indices_master(id),
                UNIQUE(index_id)
            )
        ''')
        
        # Create weekly_recommendations table (Task 1.2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                week_start_date TEXT NOT NULL,
                week_end_date TEXT NOT NULL,
                rank INTEGER NOT NULL,
                weekly_change_percent REAL,
                three_week_cumulative_return REAL,
                niftybees_weekly_change_percent REAL,
                niftybees_three_week_cumulative_return REAL,
                recommendation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES indices_master(id),
                UNIQUE(index_id, week_start_date)
            )
        ''')
        
        # Create monthly_recommendations table (Task 1.3)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_id INTEGER NOT NULL,
                month_start_date TEXT NOT NULL,
                month_end_date TEXT NOT NULL,
                rank INTEGER NOT NULL,
                monthly_change_percent REAL,
                three_month_cumulative_return REAL,
                niftybees_monthly_change_percent REAL,
                niftybees_three_month_cumulative_return REAL,
                recommendation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (index_id) REFERENCES indices_master(id),
                UNIQUE(index_id, month_start_date)
            )
        ''')
        
        # Create whatif_scenarios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatif_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                initial_amount REAL NOT NULL DEFAULT 100000,
                frequency TEXT NOT NULL DEFAULT 'weekly',
                allocation_1 REAL NOT NULL DEFAULT 50,
                allocation_2 REAL NOT NULL DEFAULT 30,
                allocation_3 REAL NOT NULL DEFAULT 20,
                start_date TEXT NOT NULL,
                end_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create whatif_simulation_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatif_simulation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                period_number INTEGER NOT NULL,
                period_start_date TEXT NOT NULL,
                period_end_date TEXT NOT NULL,
                recommendation_1_symbol TEXT,
                recommendation_2_symbol TEXT,
                recommendation_3_symbol TEXT,
                allocation_1_percent REAL NOT NULL,
                allocation_2_percent REAL NOT NULL,
                allocation_3_percent REAL NOT NULL,
                strategy_value_start REAL NOT NULL,
                strategy_value_end REAL NOT NULL,
                niftybees_value_start REAL NOT NULL,
                niftybees_value_end REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES whatif_scenarios(id) ON DELETE CASCADE
            )
        ''')
        
        print("Database tables created successfully")
        
        # Insert indices data
        insert_indices_data(cursor)
        
        # Configure logging
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'database_setup.log')),
                logging.StreamHandler()
            ]
        )
        
        # Create indexes for performance
        create_indexes(cursor)
        
        # Commit changes
        conn.commit()
        logging.info("Database setup completed successfully")
        
    except Exception as e:
        logging.error(f"Error setting up database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_indices_data(cursor):
    """Insert all supported indices into indices_master table"""
    
    indices_data = [
        # Precious Metal ETFs
        ('Silver BeES', 'SILVERBEES', 'precious_metal', 'Silver ETF', 1),
        ('Gold BeES', 'GOLDBEES', 'precious_metal', 'Gold ETF', 1),
        
        # Nifty ETFs
        ('Nifty BeES', 'NIFTYBEES', 'nifty', 'Nifty 50 ETF', 1),
        ('Motilal Oswal Nifty 500', 'MONIFTY500', 'nifty', 'Nifty 500 ETF', 1),
        ('Nifty Momentum 50', 'MOMENTUM50', 'nifty', 'Momentum 50 ETF', 1),
        
        # Sector ETFs
        ('Nifty IT BeES', 'ITBEES', 'sector', 'IT Sector ETF', 1),
        ('Nifty Bank BeES', 'BANKBEES', 'sector', 'Banking Sector ETF', 1),
        ('Nifty PSU Bank BeES', 'PSUBNKBEES', 'sector', 'PSU Banking Sector ETF', 1),
        ('Nifty Auto BeES', 'AUTOBEES', 'sector', 'Auto Sector ETF', 1),
        ('Nifty Junior BeES', 'JUNIORBEES', 'sector', 'Junior Cap ETF', 1),
        ('Nifty Pharma BeES', 'PHARMABEES', 'sector', 'Pharma Sector ETF', 1),
        ('Nifty FMCG ETF', 'FMCGIETF', 'sector', 'FMCG Sector ETF', 1),
        ('Nifty Midcap 150 BeES', 'MID150BEES', 'midcap', 'Midcap 150 ETF', 1),
        ('Nifty Oil & Gas ETF', 'OILIETF', 'sector', 'Oil & Gas Sector ETF', 1),
        ('Nifty Alpha 50', 'ALPHA', 'sector', 'Alpha 50 ETF', 1),
        ('Nifty Infra BeES', 'INFRABEES', 'sector', 'Infrastructure Sector ETF', 1),
        ('Nifty Next 50 ETF', 'NEXT50IETF', 'sector', 'Next 50 ETF', 1),
        ('Nifty Healthcare ETF', 'HEALTHIETF', 'sector', 'Healthcare Sector ETF', 1),
        ('Nifty Smallcap 250', 'SMALLCAP', 'smallcap', 'Smallcap 250 ETF', 1),
        
        # Thematic ETFs
        ('Nifty Total Market', 'AONETOTAL', 'thematic', 'Total Market ETF', 1),
        ('Nifty Momentum', 'MOMOMENTUM', 'thematic', 'Momentum ETF', 1),
        ('Nifty Quality Midcap 50', 'MONQ50', 'thematic', 'Quality Midcap 50 ETF', 1),
        ('HDFC Value Fund', 'HDFCVALUE', 'thematic', 'Value Fund ETF', 1),
        ('HDFC Growth Fund', 'HDFCGROWTH', 'thematic', 'Growth Fund ETF', 1),
        ('HDFC Momentum Fund', 'HDFCMOMENT', 'thematic', 'Momentum Fund ETF', 1),
        ('Motilal Oswal MSCI EAFE Fund', 'MODEFENCE', 'thematic', 'International Equity ETF', 1),
        ('Nifty EV & New Age Automotive', 'EVINDIA', 'thematic', 'EV Sector ETF', 1),
        ('Nifty Consumption ETF', 'CONSUMIETF', 'thematic', 'Consumption Sector ETF', 1),
        ('Nifty India Railways', 'GROWWRAIL', 'thematic', 'Railways Sector ETF', 1),
        ('Nifty IPO ETF', 'SELECTIPO', 'thematic', 'IPO ETF', 1),
        
        # Liquid Fund
        ('Liquid BeES', 'LIQUIDBEES', 'liquid_fund', 'Liquid Fund ETF', 1),
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO indices_master 
        (name, symbol, index_type, description, is_active) 
        VALUES (?, ?, ?, ?, ?)
    ''', indices_data)
    
    print(f"Inserted {len(indices_data)} indices into indices_master table")

def create_indexes(cursor):
    """Create indexes for better performance"""
    
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_index_data_index_id ON index_data(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_index_data_date ON index_data(date)',
        'CREATE INDEX IF NOT EXISTS idx_index_data_index_date ON index_data(index_id, date)',
        'CREATE INDEX IF NOT EXISTS idx_calculated_data_index_id ON index_calculated_data(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_calculated_data_date ON index_calculated_data(calculation_date)',
        'CREATE INDEX IF NOT EXISTS idx_calculated_data_index_date ON index_calculated_data(index_id, calculation_date)',
        'CREATE INDEX IF NOT EXISTS idx_indices_master_symbol ON indices_master(symbol)',
        'CREATE INDEX IF NOT EXISTS idx_indices_master_type ON indices_master(index_type)',
        'CREATE INDEX IF NOT EXISTS idx_momentum_data_index_id ON index_momentum_data(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_momentum_data_date ON index_momentum_data(calculation_date)',
        'CREATE INDEX IF NOT EXISTS idx_weekly_rec_index_id ON weekly_recommendations(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_weekly_rec_week ON weekly_recommendations(week_start_date)',
        'CREATE INDEX IF NOT EXISTS idx_monthly_rec_index_id ON monthly_recommendations(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_monthly_rec_month ON monthly_recommendations(month_start_date)',
        'CREATE INDEX IF NOT EXISTS idx_index_rec_index_id ON index_recommendations(index_id)',
        'CREATE INDEX IF NOT EXISTS idx_whatif_results_scenario ON whatif_simulation_results(scenario_id)',
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("Database indexes created successfully")

if __name__ == "__main__":
    setup_database()
