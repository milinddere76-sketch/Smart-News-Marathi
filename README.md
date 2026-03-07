# स्मार्ट न्यूज मराठी (Smart News Marathi)

24x7 AI Live News Channel automation system.

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed.
- YouTube Stream Key.

### Initial Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your `YOUTUBE_STREAM_KEY` and other credentials.

### Running with Docker
To build and start all services:
```bash
docker-compose up --build
```

### Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL on port 5432
- **Redis**: For task queuing
