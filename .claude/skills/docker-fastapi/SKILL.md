---
name: docker-fastapi
description: |
  Containerize FastAPI applications with Docker.
  Use when users ask to dockerize, containerize, create Dockerfile,
  docker-compose, or deploy FastAPI with Docker.
---

# Docker FastAPI Skill

## What This Skill Does
- Creates Dockerfiles (development with hot-reload, production optimized)
- Generates docker-compose.yml (with PostgreSQL/SQLite/None)
- Provides .dockerignore files
- Explains Docker commands and concepts
- Troubleshoots common Docker issues

## What This Skill Does NOT Do
- Kubernetes deployment (K8s)
- Cloud-specific deployment (AWS ECS, GCP Cloud Run, Azure Container Apps)
- CI/CD pipeline setup (GitHub Actions, GitLab CI)
- Non-FastAPI applications (Flask, Django, Express)

## Before Implementation

Gather context about the user's project:

| Context | How to Check |
|---------|--------------|
| Project structure | Look for `main.py` vs `app/` folder |
| Dependencies | Check `requirements.txt` or `pyproject.toml` |
| Database usage | Look for SQLAlchemy, SQLModel, databases imports |
| Existing Docker files | Check for Dockerfile, docker-compose.yml, .dockerignore |

## Required Clarifications

Before generating Docker files, ask the user these questions:

### 1. Environment
- **Development**: Hot-reload enabled, source mounted as volume, debug mode
- **Production**: Multi-stage build, optimized image, non-root user, health checks

### 2. Database
- **PostgreSQL**: Adds postgres container, network, volume, env vars
- **SQLite**: Uses volume for persistence
- **None**: Simple single-container setup

### 3. Project Structure
- **Simple**: Single `main.py` file (e.g., `uvicorn main:app`)
- **Structured**: `app/` folder with `__init__.py` (e.g., `uvicorn app.main:app`)

## Workflow

### Step 1: Analyze Project
1. Check existing files (main.py, app/, requirements.txt)
2. Identify database usage
3. Note any existing Docker configuration

### Step 2: Ask Clarifying Questions
Use AskUserQuestion to determine:
- Environment (dev/prod)
- Database needs
- Project structure (if not obvious)

### Step 3: Generate Files
Based on user choices, create:

| Choice | Files Generated |
|--------|-----------------|
| Dev + No DB | Dockerfile.dev, docker-compose.dev.yml, .dockerignore |
| Dev + PostgreSQL | Dockerfile.dev, docker-compose.dev.yml, .dockerignore |
| Prod + PostgreSQL | Dockerfile, docker-compose.yml, .dockerignore |
| Any | Always include .dockerignore |

### Step 4: Provide Commands
Give user the commands to:
1. Build the image
2. Start containers
3. View logs
4. Stop and cleanup

### Step 5: Explain Next Steps
- How to verify it's working
- Common modifications they might need
- Troubleshooting if something fails

## Reference Files

| File | When to Read |
|------|--------------|
| `references/core-concepts.md` | User is learning Docker or asks "what is..." |
| `references/dockerfile-patterns.md` | Creating any Dockerfile |
| `references/compose-patterns.md` | Multi-container setup with database |
| `references/commands-troubleshooting.md` | Running, debugging, or fixing issues |

## Example User Requests

These should trigger this skill:
- "Dockerize my FastAPI app"
- "Create a Dockerfile for this project"
- "Add docker-compose with PostgreSQL"
- "How do I containerize this API?"
- "Setup Docker for development"
- "Create production Docker setup"

## Output Format

When generating files, use this format:

```markdown
## Generated Files

### 1. Dockerfile
[code block with Dockerfile]

### 2. docker-compose.yml
[code block with compose file]

### 3. .dockerignore
[code block with ignore patterns]

## Commands

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Verify It Works
1. Open http://localhost:8000
2. Check http://localhost:8000/docs for Swagger UI
```

## Integration with fastapi-pro

This skill complements the `fastapi-pro` skill:
- `fastapi-pro`: Covers many topics including basic Docker deployment
- `docker-fastapi`: Deep focus on Docker with educational content, dev+prod options, and troubleshooting

Use this skill when Docker is the primary focus of the user's request.
