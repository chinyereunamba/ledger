# Docker Configuration

This directory contains Docker configuration files for containerized deployment.

## Files

- `Dockerfile.api` - Docker image for FastAPI backend
- `Dockerfile.frontend` - Docker image for frontend (nginx)
- `docker-compose.yml` - Docker Compose configuration

## Usage

### Build and Run with Docker Compose

```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Start services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Using Makefile

```bash
make docker-build  # Build images
make docker-up     # Start containers
make docker-down   # Stop containers
make docker-logs   # View logs
```

## Services

- **API**: FastAPI backend on port 8000
- **Frontend**: Nginx serving static files on port 3000

