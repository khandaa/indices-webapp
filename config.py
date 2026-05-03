import os
import configparser

def get_config():
    """Get configuration from db.config file"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.config')
    config.read(config_path)
    return config

def get_database_config():
    """Get database configuration"""
    config = get_config()
    db_config = {
        'host': config.get('database', 'host', fallback='localhost'),
        'port': config.getint('database', 'port', fallback=3306),
        'socket': config.get('database', 'socket', fallback=''),
        'user': config.get('database', 'user', fallback='root'),
        'password': config.get('database', 'password', fallback=''),
        'database': config.get('database', 'database', fallback='indices_db'),
    }
    return db_config

def get_app_config():
    """Get app configuration"""
    config = get_config()
    return {
        'backend_host': config.get('app', 'backend_host', fallback='0.0.0.0'),
        'backend_port': config.getint('app', 'backend_port', fallback=5050),
        'frontend_port': config.getint('app', 'frontend_port', fallback=3000),
    }

def get_backend_url():
    """Get backend API URL"""
    cfg = get_app_config()
    return f"http://localhost:{cfg['backend_port']}"

def get_allowed_origins():
    """Get allowed CORS origins"""
    cfg = get_app_config()
    frontend_port = cfg['frontend_port']
    return [
        f"http://localhost:{frontend_port}",
        f"http://localhost:{frontend_port + 1}",
        "http://localhost:3050",
        f"http://127.0.0.1:{frontend_port}",
    ]