import logging
import os
from datetime import datetime
from typing import Dict, Optional, Any

import requests
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variable to store the latest leaderboard data
leaderboard_data: Optional[Dict[str, Any]] = None
last_updated: Optional[datetime] = None

# Configuration
SEGMENT_ID = "12368762"
STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN", "73725f7af2f6468c0bea57e8464ea273a100b74c")
CERT_PATH = os.getenv("CERT_PATH")


class StravaLeaderboardService:
    """Service to handle Strava API interactions"""
    
    def __init__(self, access_token: str, segment_id: str, cert_path: str):
        self.access_token = access_token
        self.segment_id = segment_id
        self.cert_path = cert_path
        self.base_url = "https://www.strava.com/api/v3"
    
    def fetch_leaderboard(self) -> Optional[Dict[str, Any]]:
        """Fetch leaderboard data from Strava API"""
        url = f"{self.base_url}/segments/{self.segment_id}/leaderboard?club_id=1114386"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Determine SSL verification strategy
        verify = False
        logger.warning("SSL certificate verification disabled")
        
        response = requests.get(url, headers=headers, verify=verify, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Successfully fetched leaderboard data for segment {self.segment_id}")
        return data


# Initialize the service
strava_service = StravaLeaderboardService(STRAVA_ACCESS_TOKEN, SEGMENT_ID, CERT_PATH)


async def update_leaderboard():
    """Scheduled task to update leaderboard data"""
    global leaderboard_data, last_updated
    
    logger.info("Updating leaderboard data...")
    
    data = strava_service.fetch_leaderboard()
    if data:
        leaderboard_data = data
        last_updated = datetime.now()
        logger.info("Leaderboard data updated successfully")
    else:
        logger.warning("Failed to update leaderboard data")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the application and start the scheduler"""
    logger.info("Starting Strava Leaderboard API service...")
    
    # Fetch initial data
    await update_leaderboard()
    
    # Set up scheduler for periodic updates (every 15 minutes)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_leaderboard,
        'interval',
        minutes=15,
        id='update_leaderboard',
        replace_existing=True
    )
    scheduler.start()
    
    # Store scheduler in app state for cleanup
    app.state.scheduler = scheduler
    
    logger.info("Service started successfully")
    yield
    # cleanup code goes here
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()
    logger.info("Service shutdown complete")


app = FastAPI(
    title="Strava Leaderboard API",
    description="API service that fetches and serves Strava segment leaderboard data",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Strava Leaderboard API",
        "version": "1.0.0",
        "segment_id": SEGMENT_ID,
        "status": "running",
        "last_updated": last_updated.isoformat() if last_updated else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_available": leaderboard_data is not None,
        "last_updated": last_updated.isoformat() if last_updated else None
    }


@app.get("/leaderboard")
async def get_leaderboard():
    """Get the current leaderboard data"""
    if leaderboard_data is None:
        raise HTTPException(
            status_code=503,
            detail="Leaderboard data not available. Service may be starting up or experiencing issues."
        )
    
    return {
        "segment_id": SEGMENT_ID,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "data": leaderboard_data
    }


@app.get("/leaderboard/entries")
async def get_leaderboard_entries():
    """Get just the leaderboard entries without metadata"""
    if leaderboard_data is None:
        raise HTTPException(
            status_code=503,
            detail="Leaderboard data not available. Service may be starting up or experiencing issues."
        )
    
    entries = leaderboard_data.get("entries", [])
    return {
        "segment_id": SEGMENT_ID,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "entries": entries,
        "total_entries": len(entries)
    }


@app.get("/leaderboard/top/{count}")
async def get_top_entries(count: int):
    """Get the top N entries from the leaderboard"""
    if leaderboard_data is None:
        raise HTTPException(
            status_code=503,
            detail="Leaderboard data not available. Service may be starting up or experiencing issues."
        )
    
    if count <= 0:
        raise HTTPException(status_code=400, detail="Count must be greater than 0")
    
    entries = leaderboard_data.get("entries", [])
    top_entries = entries[:count]
    
    return {
        "segment_id": SEGMENT_ID,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "requested_count": count,
        "returned_count": len(top_entries),
        "entries": top_entries
    }


@app.post("/leaderboard/refresh")
async def refresh_leaderboard():
    """Manually trigger a leaderboard data refresh"""
    await update_leaderboard()
    
    if leaderboard_data is None:
        raise HTTPException(
            status_code=503,
            detail="Failed to refresh leaderboard data"
        )
    
    return {
        "message": "Leaderboard data refreshed successfully",
        "last_updated": last_updated.isoformat() if last_updated else None
    }


# if __name__ == "__main__":
#     uvicorn.run(
#         "app:app",
#         host="localhost",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )
