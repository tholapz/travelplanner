# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Full Stack FastAPI Template project with a FastAPI backend and React frontend, designed for building travel planning applications. The project uses Docker Compose for development and includes authentication, user management, and item management features.

### Technology Stack

**Backend:**
- FastAPI with SQLModel for ORM
- PostgreSQL database
- Alembic for database migrations
- JWT authentication
- Pytest for testing
- Python 3.10+ with uv for package management

**Frontend:**
- React with TypeScript
- Vite for build tooling
- TanStack Query for state management
- TanStack Router for routing
- Chakra UI for components
- Playwright for E2E testing
- Biome for linting

## Development Commands

### Backend (from `backend/` directory)

**Setup:**
```bash
uv sync                           # Install dependencies
source .venv/bin/activate        # Activate virtual environment
```

**Testing and Quality:**
```bash
bash ./scripts/test.sh           # Run tests with coverage
bash ./scripts/lint.sh           # Run linting (mypy, ruff)
pytest                          # Run tests only
pytest -x                       # Stop on first failure
coverage html                   # Generate HTML coverage report
```

**Database Migrations:**
```bash
# Inside Docker container:
docker compose exec backend bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

**Development Server:**
```bash
fastapi dev app/main.py         # Local development server
# or via Docker:
docker compose watch            # Start with live reload
```

### Frontend (from `frontend/` directory)

**Setup:**
```bash
fnm use                         # Use Node version from .nvmrc
npm install                     # Install dependencies
```

**Development:**
```bash
npm run dev                     # Start development server (http://localhost:5173)
npm run build                   # Build for production
npm run lint                    # Run Biome linting
npm run generate-client         # Generate API client from OpenAPI spec
```

**Testing:**
```bash
npx playwright test             # Run E2E tests
npx playwright test --ui        # Run tests in UI mode
```

### Docker Development

**Main commands:**
```bash
docker compose watch            # Start full stack with live reload
docker compose stop [service]  # Stop specific service
docker compose logs [service]  # View logs
docker compose down -v         # Stop and clean volumes
```

**Service URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- Traefik UI: http://localhost:8090

## Architecture

### Backend Structure

**Core modules:**
- `app/models.py` - SQLModel database models and Pydantic schemas
- `app/crud.py` - Database operations (Create, Read, Update, Delete)
- `app/core/` - Configuration, database setup, security utilities
- `app/api/routes/` - API endpoint definitions
- `app/api/main.py` - API router configuration

**Key patterns:**
- Uses SQLModel for both database models and API schemas
- Implements cascade delete relationships between User and Item models
- JWT-based authentication with refresh tokens
- Environment-based configuration via Pydantic Settings
- Separate schemas for creation, updates, and public responses

### Frontend Structure

**Key directories:**
- `src/client/` - Auto-generated API client from OpenAPI
- `src/components/` - Reusable UI components organized by feature
- `src/routes/` - TanStack Router route definitions
- `src/hooks/` - Custom React hooks
- `src/theme/` - Chakra UI theme customization

**Generated client workflow:**
1. Backend changes update OpenAPI schema
2. Run `./scripts/generate-client.sh` or `npm run generate-client`
3. Commit the updated client files

### Database Schema

**Main entities:**
- `User` - Authentication and user management with UUID primary keys
- `Item` - User-owned items with cascade delete relationship
- Uses Alembic for versioned schema migrations

## Testing Strategy

**Backend:**
- Unit tests in `backend/app/tests/`
- Test utilities in `backend/app/tests/utils/`
- Coverage reporting with HTML output
- Separate test database configuration

**Frontend:**
- E2E tests with Playwright
- Tests require running Docker stack: `docker compose up -d --wait backend`
- Test files in `frontend/tests/`

## Pre-commit Hooks

The project uses pre-commit for code quality:
```bash
uv run pre-commit install       # Setup hooks
uv run pre-commit run --all-files  # Run manually
```

## Important Notes

- Always run linting commands before committing changes
- Use `docker compose watch` for development to get live reload
- Generate new API client after any backend API changes
- Database migrations require manual creation and application
- Frontend and backend can be developed independently using different ports