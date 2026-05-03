"""
MySQL Database connection handler for Indices Web Application
Reads configuration from db.config file in project root
"""

import os
import mysql.connector
from mysql.connector import pooling

_pool = None

def get_db_config():
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
    
    return config

def init_pool():
    """Initialize connection pool"""
    global _pool
    if _pool is None:
        config = get_db_config()
        _pool = pooling.MySQLConnectionPool(
            pool_name="indices_pool",
            pool_size=5,
            host=config.get('host', 'localhost'),
            port=int(config.get('port', 3306)),
            user=config.get('user', 'root'),
            password=config.get('password', ''),
            database=config.get('database', 'indices_db'),
            unix_socket=config.get('socket', '')
        )
    return _pool

def get_connection():
    """Get a connection from the pool"""
    if _pool is None:
        init_pool()
    return _pool.get_connection()

def get_cursor(connection=None):
    """Get a cursor from connection"""
    if connection is None:
        connection = get_connection()
    return connection.cursor(dictionary=True)

def close_connection(connection):
    """Close connection"""
    if connection:
        connection.close()

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
            conn.commit()
        return result
    finally:
        cursor.close()
        close_connection(conn)

def execute_many(query, data):
    """Execute many queries"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, data)
        conn.commit()
    finally:
        cursor.close()
        close_connection(conn)

def execute_write(query, params=None):
    """Execute a write query"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        close_connection(conn)