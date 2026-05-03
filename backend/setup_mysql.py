#!/usr/bin/env python3
"""
MySQL Database setup for Indices Web Application
Creates tables in MySQL database
"""

import mysql.connector
from mysql.connector import Error
import logging
import os

def read_config():
    """Read database configuration from db.config"""
    config = {}
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, 'db.config')
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return {
        'host': config.get('host', 'localhost'),
        'port': int(config.get('port', 3306)),
        'user': config.get('user', 'root'),
        'password': config.get('password', ''),
        'database': config.get('database', 'indices_db'),
        'unix_socket': config.get('socket', '')
    }

def create_mysql_tables(cursor):
    """Create all tables in MySQL"""
    
    tables = [
        '''CREATE TABLE IF NOT EXISTS indices_master (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            symbol VARCHAR(50) NOT NULL UNIQUE,
            index_type VARCHAR(50) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        )''',
        
        '''CREATE TABLE IF NOT EXISTS index_data (
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
            UNIQUE KEY unique_index_date (index_id, date)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS index_calculated_data (
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
            UNIQUE KEY unique_calc_date (index_id, calculation_date)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS index_momentum_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            calculation_date DATE NOT NULL,
            three_week_cumulative_return DECIMAL(10, 4),
            three_month_cumulative_return DECIMAL(10, 4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE KEY unique_momentum_date (index_id, calculation_date)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS user_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL UNIQUE,
            refresh_interval INT DEFAULT 300,
            theme VARCHAR(20) DEFAULT 'light',
            language VARCHAR(10) DEFAULT 'en'
        )''',
        
        '''CREATE TABLE IF NOT EXISTS index_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id INT NOT NULL,
            is_selected BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (index_id) REFERENCES indices_master(id),
            UNIQUE KEY unique_rec_index (index_id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS weekly_recommendations (
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
            UNIQUE KEY unique_weekly_rec (index_id, week_start_date)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS monthly_recommendations (
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
            UNIQUE KEY unique_monthly_rec (index_id, month_start_date)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS whatif_scenarios (
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
        )''',
        
        '''CREATE TABLE IF NOT EXISTS whatif_simulation_results (
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
        )'''
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    print("MySQL tables created successfully")

def create_indexes(cursor):
    """Create performance indexes"""
    
    indexes = [
        'CREATE INDEX idx_index_data_index_id ON index_data(index_id)',
        'CREATE INDEX idx_index_data_date ON index_data(date)',
        'CREATE INDEX idx_calculated_data_index_id ON index_calculated_data(index_id)',
        'CREATE INDEX idx_calculated_data_date ON index_calculated_data(calculation_date)',
        'CREATE INDEX idx_momentum_data_index_id ON index_momentum_data(index_id)',
        'CREATE INDEX idx_momentum_data_date ON index_momentum_data(calculation_date)',
        'CREATE INDEX idx_indices_master_symbol ON indices_master(symbol)',
        'CREATE INDEX idx_indices_master_type ON indices_master(index_type)',
        'CREATE INDEX idx_weekly_rec_index_id ON weekly_recommendations(index_id)',
        'CREATE INDEX idx_weekly_rec_week ON weekly_recommendations(week_start_date)',
        'CREATE INDEX idx_monthly_rec_index_id ON monthly_recommendations(index_id)',
        'CREATE INDEX idx_monthly_rec_month ON monthly_recommendations(month_start_date)',
        'CREATE INDEX idx_whatif_results_scenario ON whatif_simulation_results(scenario_id)',
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Error as e:
            pass
    
    print("Indexes created successfully")

def insert_default_indices(cursor):
    """Insert default indices data"""
    
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
            "INSERT INTO indices_master (name, symbol, index_type, description, is_active) VALUES (%s, %s, %s, %s, %s)",
            (name, symbol, index_type, description, is_active)
        )
    
    print(f"Inserted {len(indices_data)} indices")

def setup_database():
    """Main setup function"""
    
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'mysql_setup.log')),
            logging.StreamHandler()
        ]
    )
    
    try:
        db_config = read_config()
        logging.info("Read database configuration from db.config")
        
        logging.info("Connecting to MySQL...")
        mysql_conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            unix_socket=db_config['unix_socket']
        )
        logging.info("Connected to MySQL successfully")
        
        mysql_cursor = mysql_conn.cursor()
        
        create_mysql_tables(mysql_cursor)
        mysql_conn.commit()
        
        create_indexes(mysql_cursor)
        mysql_conn.commit()
        
        insert_default_indices(mysql_cursor)
        mysql_conn.commit()
        
        logging.info("Database setup completed successfully!")
        print("\n=== MySQL database setup completed! ===")
        
    except Error as e:
        logging.error(f"MySQL Error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error: {e}")
        raise
    finally:
        if 'mysql_conn' in locals() and mysql_conn.is_connected():
            mysql_conn.close()

if __name__ == "__main__":
    setup_database()