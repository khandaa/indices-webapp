#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend/api')
import uvicorn
from config import get_app_config

if __name__ == "__main__":
    cfg = get_app_config()
    uvicorn.run("main:app", host=cfg['backend_host'], port=cfg['backend_port'], reload=False)