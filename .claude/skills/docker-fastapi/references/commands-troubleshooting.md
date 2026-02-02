# Docker Commands & Troubleshooting

## Essential Commands

### Building

```bash
# Build image from Dockerfile
docker build -t myapp .

# Build with specific Dockerfile
docker build -t myapp -f Dockerfile.dev .

# Build without cache (fresh build)
docker build --no-cache -t myapp .

# Build with docker-compose
docker-compose build

# Build and start
docker-compose up --build
```

### Running

```bash
# Run container
docker run -p 8000:8000 myapp

# Run in background (detached)
docker run -d -p 8000:8000 myapp

# Run with name
docker run -d --name my-api -p 8000:8000 myapp

# Run with environment variables
docker run -e DATABASE_URL=... -p 8000:8000 myapp

# Run with volume mount
docker run -v $(pwd):/app -p 8000:8000 myapp

# Docker-compose up (foreground)
docker-compose up

# Docker-compose up (detached)
docker-compose up -d

# Specify compose file
docker-compose -f docker-compose.dev.yml up
```

### Viewing Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List images
docker images

# List volumes
docker volume ls

# Container logs
docker logs my-api

# Follow logs (live)
docker logs -f my-api

# Docker-compose logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f api
```

### Stopping & Removing

```bash
# Stop container
docker stop my-api

# Remove container
docker rm my-api

# Stop and remove
docker rm -f my-api

# Docker-compose stop (keeps containers)
docker-compose stop

# Docker-compose down (removes containers)
docker-compose down

# Down + remove volumes (WARNING: deletes data!)
docker-compose down -v

# Down + remove images
docker-compose down --rmi all
```

### Debugging

```bash
# Execute command in running container
docker exec -it my-api bash

# Execute command in running container (sh if no bash)
docker exec -it my-api sh

# Docker-compose exec
docker-compose exec api bash

# View container details
docker inspect my-api

# View container resource usage
docker stats

# View container processes
docker top my-api
```

---

## Cleanup Commands

### Remove Unused Resources

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes (WARNING: data loss!)
docker volume prune

# Remove all unused resources
docker system prune

# Remove everything including volumes (DANGER!)
docker system prune -a --volumes
```

### Remove Specific Resources

```bash
# Remove specific image
docker rmi myapp:latest

# Remove all images matching pattern
docker rmi $(docker images -q myapp)

# Remove specific volume
docker volume rm postgres_data
```

---

## Common Errors & Solutions

### 1. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solutions:**
```bash
# Find what's using the port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill the process or use different port
docker run -p 8001:8000 myapp

# Or in docker-compose.yml
ports:
  - "8001:8000"
```

### 2. Container Exits Immediately

**Error:**
Container starts and immediately stops.

**Debug:**
```bash
# View logs
docker logs my-api

# Run interactively to see error
docker run -it myapp

# Common causes:
# - Missing CMD in Dockerfile
# - Application crash on startup
# - Missing environment variables
# - Missing dependencies
```

### 3. Cannot Connect to Database

**Error:**
```
Connection refused to localhost:5432
```

**Problem:** Inside a container, `localhost` means the container itself, not your host machine.

**Solution:** Use service name instead:
```yaml
environment:
  # Wrong: localhost
  - DATABASE_URL=postgresql://user:pass@localhost:5432/db

  # Correct: service name
  - DATABASE_URL=postgresql://user:pass@db:5432/db
```

### 4. Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
```bash
# 1. Make sure requirements.txt is copied before pip install
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. Rebuild without cache
docker-compose build --no-cache

# 3. Check requirements.txt is not empty
cat requirements.txt
```

### 5. Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
```dockerfile
# 1. If using non-root user, ensure file ownership
COPY --chown=appuser:appuser . .

# 2. Or set permissions explicitly
RUN chmod +x /app/entrypoint.sh
```

### 6. Changes Not Reflected (Dev Mode)

**Problem:** Code changes not appearing despite hot-reload.

**Solutions:**
```yaml
# 1. Ensure volume mount is correct
volumes:
  - .:/app  # Current directory to /app

# 2. Check uvicorn has --reload flag
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]

# 3. Rebuild if dependencies changed
docker-compose up --build
```

### 7. Out of Disk Space

**Error:**
```
no space left on device
```

**Solution:**
```bash
# Clean up unused resources
docker system prune -a

# Check disk usage
docker system df
```

### 8. Build Context Too Large

**Problem:** Build takes forever or fails with large context.

**Solution:** Create proper `.dockerignore`:
```dockerignore
.git
__pycache__
*.pyc
.env
venv/
node_modules/
*.log
```

---

## Windows-Specific Issues

### 1. Line Ending Issues (CRLF vs LF)

**Error:**
```
/bin/bash^M: bad interpreter
```

**Solutions:**
```bash
# Convert to LF in Git config
git config --global core.autocrlf input

# Or in .gitattributes
* text=auto eol=lf
*.sh text eol=lf
```

### 2. Volume Mount Path Issues

**Problem:** Windows paths not working in volumes.

**Solutions:**
```yaml
# Use forward slashes
volumes:
  - ./app:/app

# Or Windows-style (less portable)
volumes:
  - C:/Users/name/project:/app

# In PowerShell, use ${PWD}
docker run -v ${PWD}:/app myapp
```

### 3. Docker Desktop Not Running

**Error:**
```
error during connect: This error may indicate that the docker daemon is not running
```

**Solution:**
1. Start Docker Desktop application
2. Wait for it to fully initialize (tray icon turns green)
3. Restart if stuck

### 4. WSL2 Memory Issues

**Problem:** Docker/WSL2 using too much memory.

**Solution:** Create/edit `%UserProfile%\.wslconfig`:
```ini
[wsl2]
memory=4GB
processors=2
```
Then restart WSL: `wsl --shutdown`

---

## Useful Aliases

Add to your shell profile (`.bashrc`, `.zshrc`, or PowerShell profile):

```bash
# Bash/Zsh
alias dc='docker-compose'
alias dcu='docker-compose up'
alias dcd='docker-compose down'
alias dcb='docker-compose build'
alias dps='docker ps'
alias dlogs='docker-compose logs -f'

# PowerShell
Set-Alias dc docker-compose
function dcu { docker-compose up @args }
function dcd { docker-compose down @args }
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Build | `docker-compose build` |
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Logs | `docker-compose logs -f` |
| Shell | `docker-compose exec api bash` |
| Rebuild | `docker-compose up --build` |
| Clean | `docker system prune` |
| Status | `docker ps` |
