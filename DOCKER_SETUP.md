# Docker Setup Guide for SimpleAnalysis

## Overview

SimpleAnalysis uses Docker and Docker Compose to containerize all services:
- **MongoDB**: Database for storing users, watchlists, and analysis data
- **Redis**: Cache for stock data and session management
- **Backend**: FastAPI application
- **Frontend**: React application with Nginx

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Network                     │
│            (simpleanalysis-network)                  │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ MongoDB  │  │  Redis   │  │ Backend  │           │
│  │ :27017   │  │  :6379   │  │  :8000   │           │
│  └──────────┘  └──────────┘  └────┬─────┘           │
│                                    │                  │
│                              ┌─────▼─────┐           │
│                              │ Frontend  │           │
│                              │   :80     │           │
│                              └───────────┘           │
│                                                       │
└─────────────────────────────────────────────────────┘
         │              │              │
    Persistent      Persistent    Nginx serves
    Volume          Volume        static files
    (mongodb_data)  (redis_data)  & proxies API
```

## Configuration Files

### 1. Environment Files

**backend/.env** - For local development
```env
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
```

**backend/.env.docker** - For Docker deployment
```env
MONGODB_URL=mongodb://mongodb:27017  # Uses Docker service name
REDIS_URL=redis://redis:6379/0       # Uses Docker service name
```

### 2. Docker Compose Files

**docker-compose.yml** - Full production deployment
- Builds and runs all 4 services
- Includes healthchecks
- Uses persistent volumes

**docker-compose.dev.yml** - Development mode
- Runs only MongoDB and Redis
- Allows backend/frontend to run locally for faster development

## Quick Start

### Option 1: Full Docker Deployment

Run all services in Docker:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Check service status
docker-compose ps

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

Access the application:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

### Option 2: Development Mode

Run only databases in Docker, backend/frontend locally:

```bash
# Start MongoDB and Redis
docker-compose -f docker-compose.dev.yml up -d

# In terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
python main.py

# In terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Access the application:
- **Frontend**: http://localhost:3000 (Vite dev server)
- **Backend API**: http://localhost:8000
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

## Healthchecks

All services include healthchecks to ensure proper startup order:

### MongoDB Healthcheck
```yaml
healthcheck:
  test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 40s
```

### Redis Healthcheck
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Backend Healthcheck
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

The backend will only start after MongoDB and Redis are healthy.

## Persistent Data

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep simpleanalysis

# Expected volumes:
# - simpleanalysis_mongodb_data
# - simpleanalysis_mongodb_config
# - simpleanalysis_redis_data

# Inspect a volume
docker volume inspect simpleanalysis_mongodb_data

# Backup MongoDB data
docker-compose exec mongodb mongodump --out /data/backup

# Restore MongoDB data
docker-compose exec mongodb mongorestore /data/backup
```

## Common Commands

### Rebuild Services

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and start
docker-compose up -d --build
```

### Execute Commands in Containers

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Access Redis CLI
docker-compose exec redis redis-cli

# Access backend shell
docker-compose exec backend /bin/bash

# Run Python commands in backend
docker-compose exec backend python -c "print('Hello')"
```

### View Service Status

```bash
# Show running containers
docker-compose ps

# Show resource usage
docker stats

# Show logs from all services
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Show last 100 lines
docker-compose logs --tail=100
```

## Troubleshooting

### Backend Can't Connect to MongoDB

**Problem**: Backend shows "Failed to connect to MongoDB"

**Solutions**:
1. Check if MongoDB is healthy:
   ```bash
   docker-compose ps
   ```

2. Check MongoDB logs:
   ```bash
   docker-compose logs mongodb
   ```

3. Verify network connectivity:
   ```bash
   docker-compose exec backend ping mongodb
   ```

4. Ensure using correct MongoDB URL:
   - Docker: `mongodb://mongodb:27017`
   - Local: `mongodb://localhost:27017`

### Port Already in Use

**Problem**: "port is already allocated"

**Solutions**:
1. Check what's using the port:
   ```bash
   # Linux/Mac
   lsof -i :8000

   # Windows
   netstat -ano | findstr :8000
   ```

2. Change port in docker-compose.yml:
   ```yaml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

### Services Not Starting

**Problem**: Services keep restarting

**Solutions**:
1. Check logs for errors:
   ```bash
   docker-compose logs -f backend
   ```

2. Check healthcheck status:
   ```bash
   docker-compose ps
   ```

3. Remove old containers and rebuild:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Database Data Lost After Restart

**Problem**: Data disappears after stopping containers

**Solution**: Don't use `-v` flag when stopping:
```bash
# Good - keeps volumes
docker-compose down

# Bad - deletes volumes
docker-compose down -v
```

### Frontend Can't Reach Backend

**Problem**: Frontend shows network errors

**Solutions**:
1. Check if backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check CORS settings in backend/.env.docker:
   ```env
   CORS_ORIGINS=http://localhost,http://localhost:80
   ```

3. Check browser console for CORS errors

## Environment Variables

### Backend Environment Variables

| Variable | Description | Default (Local) | Default (Docker) |
|----------|-------------|-----------------|------------------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` | `mongodb://mongodb:27017` |
| `MONGODB_DB_NAME` | Database name | `simpleanalysis` | `simpleanalysis` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT secret key | (required) | (required) |
| `DEBUG` | Debug mode | `True` | `True` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000` | `http://localhost,http://localhost:80` |

## Security Notes

### Development vs Production

The current setup is for **development only**. For production:

1. **Change SECRET_KEY**: Generate a secure random key
   ```bash
   openssl rand -hex 32
   ```

2. **Add MongoDB Authentication**:
   ```yaml
   mongodb:
     environment:
       MONGO_INITDB_ROOT_USERNAME: admin
       MONGO_INITDB_ROOT_PASSWORD: your-secure-password
   ```

3. **Add Redis Password**:
   ```yaml
   redis:
     command: redis-server --requirepass your-redis-password
   ```

4. **Use Environment Files**: Don't commit `.env.docker` to Git
   ```bash
   # Add to .gitignore
   echo "*.env.docker" >> .gitignore
   ```

5. **Enable SSL/TLS**: Use HTTPS for production

6. **Don't Expose Ports**: Remove port mappings for MongoDB/Redis
   ```yaml
   # Remove these in production:
   # ports:
   #   - "27017:27017"
   ```

## Network Configuration

All services run on the same Docker network (`simpleanalysis-network`) and can communicate using service names:

- Backend → MongoDB: `mongodb://mongodb:27017`
- Backend → Redis: `redis://redis:6379`
- Frontend → Backend: Proxied through Nginx

External access:
- Port 80: Frontend (Nginx)
- Port 8000: Backend API
- Port 27017: MongoDB (dev only)
- Port 6379: Redis (dev only)

## Next Steps

1. **Test the Setup**:
   ```bash
   docker-compose up -d
   docker-compose logs -f
   ```

2. **Create a Test User**:
   - Visit http://localhost
   - Click "Register"
   - Create an account

3. **Check Database**:
   ```bash
   docker-compose exec mongodb mongosh
   use simpleanalysis
   db.users.find()
   ```

4. **Monitor Services**:
   ```bash
   docker-compose ps
   docker stats
   ```

For more information, see the main [README.md](README.md).
