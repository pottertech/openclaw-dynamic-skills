---
name: docker-deployment
description: Containerize applications with Docker, create Docker Compose configurations, and manage containerized services. Use when deploying applications, creating development environments, or orchestrating multi-container setups.
---

# Docker Deployment

Containerize applications and manage Docker deployments for development and production.

## When to Use

- Containerizing applications
- Creating reproducible development environments
- Multi-service orchestration (Docker Compose)
- Production deployments
- CI/CD pipeline integration
- Service isolation
- Resource management

## Basic Docker Commands

### Container Lifecycle

```bash
# Run container
docker run -d --name myapp -p 8080:80 myapp:latest

# List containers
docker ps                    # Running
docker ps -a                 # All

# Stop/Start
docker stop myapp
docker start myapp
docker restart myapp

# Remove
docker stop myapp && docker rm myapp

# View logs
docker logs myapp
docker logs -f myapp         # Follow
```

### Image Management

```bash
# Build image
docker build -t myapp:latest .

# List images
docker images

# Pull/Push
docker pull nginx:latest
docker push myapp:latest

# Remove image
docker rmi myapp:latest
```

## Dockerfile Examples

### Python Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### Node.js Application

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Expose port
EXPOSE 3000

# Run application
CMD ["node", "server.js"]
```

### Multi-Stage Build (Optimized)

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Docker Compose

### Basic Setup

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Multi-Service Setup

```yaml
version: '3.8'

services:
  # Web Application
  app:
    build: ./app
    ports:
      - "3000:3000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:pass@postgres:5432/app
    depends_on:
      - redis
      - postgres
  
  # Background Workers
  worker:
    build: ./app
    command: python worker.py
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

volumes:
  redis_data:
  postgres_data:
```

## Your Services (Potter's Quill)

### All-in-One Media Stack

```yaml
version: '3.8'

services:
  # ComfyUI (Image Generation)
  comfyui:
    image: comfyui/comfyui:latest
    ports:
      - "8188:8188"
    volumes:
      - /Volumes/ComfyUI-and-Data/comfyui:/app
      - comfyui_models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
  
  # Kokoro TTS
  kokoro:
    build: ./Kokoro-FastAPI
    ports:
      - "8880:8880"
    volumes:
      - kokoro_voices:/app/voices
  
  # ACE-Step (Music Generation)
  acestep:
    build: ./ACE-Step
    ports:
      - "7860:7860"
    volumes:
      - acestep_outputs:/app/outputs
  
  # Dynamic Skills Lookup
  skills-lookup:
    build: ./dynamic-skills
    ports:
      - "8845:8845"
    environment:
      - SKILLS_DB_DSN=postgresql://postgres:pass@postgres:5432/skillsdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  # PostgreSQL
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=skillsdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  comfyui_models:
  kokoro_voices:
  acestep_outputs:
  postgres_data:
  redis_data:
```

## Common Patterns

### Health Checks

```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Resource Limits

```yaml
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Networking

```yaml
services:
  app:
    build: .
    networks:
      - frontend
      - backend
  
  db:
    image: postgres:15
    networks:
      - backend

networks:
  frontend:
  backend:
    internal: true
```

## Best Practices

1. **Use specific versions** - Don't use `latest` in production
2. **Multi-stage builds** - Reduce image size
3. **.dockerignore** - Exclude unnecessary files
4. **Non-root user** - Security best practice
5. **Health checks** - Monitor container health
6. **Logging** - Configure log rotation
7. **Volumes** - Persist data
8. **Environment variables** - Don't hardcode secrets

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
