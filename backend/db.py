"""
Database abstraction layer for Indices Web Application
Uses MySQL database only
"""

import os
import mysql.connector

def get_db_config():
    """Read database configuration from db.config"""
    config = {}
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_path, 'db.config')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    pass
                elif line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def connect_db():
    """Get a MySQL database connection"""
    config = get_db_config()
    return mysql.connector.connect(
        host=config.get('host', 'localhost'),
        port=int(config.get('port', 3306)),
        user=config.get('user', 'root'),
        password=config.get('password', ''),
        database=config.get('database', 'indices_db'),
        unix_socket=config.get('socket', ''),
        autocommit=False
    )

class Database:
    """MySQL Database class"""
    
    def __init__(self, db_type=None):  # backward compat
        self._conn = None
        self._cursor = None
    
    @property
    def conn(self):
        return self._conn
    
    def connect(self):
        self._conn = connect_db()
        return self
    
    def cursor(self):
        if self._conn is None:
            self.connect()
        self._cursor = self._conn.cursor()
        return self._cursor
    
    def close(self):
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def commit(self):
        if self._conn:
            self._conn.commit()
    
    def rollback(self):
        if self._conn:
            self._conn.rollback()
    
    def fetch_all(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cols = [d[0] for d in cursor.description] if cursor.description else []
        return [dict(zip(cols, row)) for row in results]
    
    def fetch_one(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        if row:
            cols = [d[0] for d in cursor.description] if cursor.description else []
            return dict(zip(cols, row))
        return None
    
    def execute(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params or ())
        self.commit()
        return cursor.lastrowid
    
    def execute_many(self, query, data):
        cursor = self.cursor()
        cursor.executemany(query, data)
        self.commit()
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self.close()
        return False

def get_db():
    """Context manager for database connections"""
    db = Database()
    try:
        db.connect()
        yield db
    finally:
        db.close()

def execute_query(query, params=None):
    """Execute a query and return results"""
    with get_db() as db:
        return db.fetch_all(query, params)

def execute_write(query, params=None):
    """Execute a write query"""
    with get_db() as db:
        return db.execute(query, params)