# Strava Leaderboard API Service

A FastAPI-based web service that fetches Strava segment leaderboard data every 15 minutes and provides REST endpoints to access the data.

## Features

- **Automatic Data Fetching**: Retrieves leaderboard data for Strava segment 6821922 every 15 minutes
- **REST API**: Multiple endpoints to access leaderboard data
- **Health Monitoring**: Health check endpoints for service monitoring
- **Manual Refresh**: Ability to manually trigger data updates
- **SSL Support**: Configurable SSL certificate verification

## Installation

1. Ensure you have Python 3.10+ installed
2. Install dependencies using UV:
   ```bash
   uv sync
   ```

## Configuration

1. Update the `.env` file with your Strava access token:
   ```
   STRAVA_ACCESS_TOKEN=your_access_token_here
   ```

2. Optional: Configure other settings in `.env`:
   ```
   CERT_PATH=path_to_your_certificate.crt
   HOST=0.0.0.0
   PORT=8000
   ```

## Running the Service

### Option 1: Using the startup script
```bash
uv run start_server.py
```

### Option 2: Using uvicorn directly
```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Direct Python execution
```bash
uv run python app.py
```

## API Endpoints

Once the service is running, it will be available at `http://localhost:8000`

### Core Endpoints

- **GET `/`** - Service information and status
- **GET `/health`** - Health check endpoint
- **GET `/leaderboard`** - Complete leaderboard data with metadata
- **GET `/leaderboard/entries`** - Just the leaderboard entries
- **GET `/leaderboard/top/{count}`** - Top N entries from the leaderboard
- **POST `/leaderboard/refresh`** - Manually trigger a data refresh

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

### Get complete leaderboard data
```bash
curl http://localhost:8000/leaderboard
```

### Get top 10 entries
```bash
curl http://localhost:8000/leaderboard/top/10
```

### Check service health
```bash
curl http://localhost:8000/health
```

### Manually refresh data
```bash
curl -X POST http://localhost:8000/leaderboard/refresh
```

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "segment_id": "6821922",
  "last_updated": "2025-07-22T10:30:00.123456",
  "data": {
    "entries": [
      {
        "athlete_name": "John Doe",
        "elapsed_time": 180,
        "rank": 1,
        // ... other Strava leaderboard fields
      }
    ]
  }
}
```

## Architecture

- **FastAPI**: Web framework for the REST API
- **APScheduler**: Background task scheduler for periodic data fetching
- **Requests**: HTTP client for Strava API calls
- **UV**: Python package manager

## Monitoring

The service includes health check endpoints and logging for monitoring:

- Service startup and shutdown events are logged
- Successful and failed API calls are logged
- Health status includes data availability information

## Development

### Running in Development Mode
```bash
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API
You can test the API using the interactive documentation at `/docs` or with curl commands as shown above.

## License

See LICENSE file for details.