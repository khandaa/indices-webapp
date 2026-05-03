#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend/api')
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=False)