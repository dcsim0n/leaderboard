#!/usr/bin/env python3
"""
Startup script for the Strava Leaderboard API service
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("Starting Strava Leaderboard API service...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"API documentation: http://{host}:{port}/docs")
    
    # Start the server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )
