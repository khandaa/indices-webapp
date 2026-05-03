#!/usr/bin/env python3
"""
Database setup script for Indices Web Application
Uses MySQL database only
"""

import mysql.connector
import os
import logging
from datetime import datetime

def setup_database():
    """Create database and all tables"""
    
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'socket': '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
        'user': 'root',
        'password': 'Emp10yDEX',
        'database': 'indices_db'
    }
    
    # Connect to database
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        unix_socket=db_config['socket']
    )
    cursor = conn.cursor()
    
    # Create indices_master table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indices_master (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            symbol VARCHAR(50) NOT NULL UNIQUE,
            index_type VARCHAR(50) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create index_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(15, 4),
            close_price DECIMAL(15, 4),
            high_price DECIMAL(15, 4),
            low_price DECIMAL(15, 4),
            volume BIGINT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id, date)
        )
    ''')
    
    # Create index_calculated_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_calculated_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            calculation_date DATE NOT NULL,
            daily_change DECIMAL(15, 4),
            weekly_change DECIMAL(15, 4),
            monthly_change DECIMAL(15, 4),
            yearly_change DECIMAL(15, 4),
            daily_change_percent DECIMAL(10, 4),
            weekly_change_percent DECIMAL(10, 4),
            monthly_change_percent DECIMAL(10, 4),
            yearly_change_percent DECIMAL(10, 4),
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id, calculation_date)
        )
    ''')
    
    # Create index_momentum_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_momentum_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            calculation_date DATE NOT NULL,
            three_week_cumulative_return DECIMAL(10, 4),
            three_month_cumulative_return DECIMAL(10, 4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id, calculation_date)
        )
    ''')
    
    # Create user_settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL UNIQUE,
            refresh_interval INT DEFAULT 300,
            theme VARCHAR(20) DEFAULT 'light',
            language VARCHAR(10) DEFAULT 'en'
        )
    ''')
    
    # Create index_recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            is_selected BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id)
        )
    ''')
    
    # Create weekly_recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            week_start_date DATE NOT NULL,
            week_end_date DATE NOT NULL,
            rank INT NOT NULL,
            weekly_change_percent DECIMAL(10, 4),
            three_week_cumulative_return DECIMAL(10, 4),
            niftybees_weekly_change_percent DECIMAL(10, 4),
            niftybees_three_week_cumulative_return DECIMAL(10, 4),
            recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id, week_start_date)
        )
    ''')
    
    # Create monthly_recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            month_start_date DATE NOT NULL,
            month_end_date DATE NOT NULL,
            rank INT NOT NULL,
            monthly_change_percent DECIMAL(10, 4),
            three_month_cumulative_return DECIMAL(10, 4),
            niftybees_monthly_change_percent DECIMAL(10, 4),
            niftybees_three_month_cumulative_return DECIMAL(10, 4),
            recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE(index_id, month_start_date)
        )
    ''')
    
    # Create whatif_scenarios table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whatif_scenarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            initial_amount DECIMAL(15, 2) NOT NULL DEFAULT 100000,
            frequency VARCHAR(20) NOT NULL DEFAULT 'weekly',
            allocation_1 DECIMAL(5, 2) NOT NULL DEFAULT 50,
            allocation_2 DECIMAL(5, 2) NOT NULL DEFAULT 30,
            allocation_3 DECIMAL(5, 2) NOT NULL DEFAULT 20,
            start_date DATE NOT NULL,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    
    # Create whatif_simulation_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whatif_simulation_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scenario_id INT NOT NULL,
            period_number INT NOT NULL,
            period_start_date DATE NOT NULL,
            period_end_date DATE NOT NULL,
            recommendation_1_symbol VARCHAR(50),
            recommendation_2_symbol VARCHAR(50),
            recommendation_3_symbol VARCHAR(50),
            allocation_1_percent DECIMAL(5, 2) NOT NULL,
            allocation_2_percent DECIMAL(5, 2) NOT NULL,
            allocation_3_percent DECIMAL(5, 2) NOT NULL,
            strategy_value_start DECIMAL(15, 2) NOT NULL,
            strategy_value_end DECIMAL(15, 2) NOT NULL,
            niftybees_value_start DECIMAL(15, 2) NOT NULL,
            niftybees_value_end DECIMAL(15, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scenario_id) REFERENCES whatif_scenarios(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_index_data_index_id ON index_data(index_id)')
    cursor.execute('CREATE INDEX idx_index_data_date ON index_data(date)')
    cursor.execute('CREATE INDEX idx_calculated_data_index_id ON index_calculated_data(index_id)')
    cursor.execute('CREATE INDEX idx_calculated_data_date ON index_calculated_data(calculation_date)')
    cursor.execute('CREATE INDEX idx_momentum_data_index_id ON index_momentum_data(index_id)')
    cursor.execute('CREATE INDEX idx_momentum_data_date ON index_momentum_data(calculation_date)')
    cursor.execute('CREATE INDEX idx_indices_master_symbol ON indices_master(symbol)')
    cursor.execute('CREATE INDEX idx_indices_master_type ON indices_master(index_type)')
    cursor.execute('CREATE INDEX idx_weekly_rec_index_id ON weekly_recommendations(index_id)')
    cursor.execute('CREATE INDEX idx_weekly_rec_week ON weekly_recommendations(week_start_date)')
    cursor.execute('CREATE INDEX idx_monthly_rec_index_id ON monthly_recommendations(index_id)')
    cursor.execute('CREATE INDEX idx_monthly_rec_month ON monthly_recommendations(month_start_date)')
    cursor.execute('CREATE INDEX idx_whatif_results_scenario ON whatif_simulation_results(scenario_id)')
    
    # Insert default indices
    indices_data = [
        ('Silver BeES', 'SILVERBEES', 'precious_metal', 'Silver ETF', 1),
        ('Gold BeES', 'GOLDBEES', 'precious_metal', 'Gold ETF', 1),
        ('Nifty BeES', 'NIFTYBEES', 'nifty', 'Nifty 50 ETF', 1),
        ('Motilal Oswal Nifty 500', 'MONIFTY500', 'nifty', 'Nifty 500 ETF', 1),
        ('Nifty Momentum 50', 'MOMENTUM50', 'nifty', 'Momentum 50 ETF', 1),
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
        ('Liquid BeES', 'LIQUIDBEES', 'liquid_fund', 'Liquid Fund ETF', 1),
    ]
    
    for name, symbol, index_type, description, is_active in indices_data:
        cursor.execute(
            "INSERT IGNORE INTO indices_master (name, symbol, index_type, description, is_active) VALUES (%s, %s, %s, %s, %s)",
            (name, symbol, index_type, description, is_active)
        )
    
    conn.commit()
    print(f"Database tables created and {len(indices_data)} indices inserted")
    
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
    logging.info("Database setup completed successfully")
    
    conn.close()

if __name__ == "__main__":
    setup_database()