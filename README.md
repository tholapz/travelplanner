# Travel Planner

A full-stack travel planning application built with FastAPI and React, designed to help users plan and manage their travel itineraries.

## Technology Stack

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

**Development:**
- Docker Compose for development environment
- Traefik as reverse proxy
- Pre-commit hooks for code quality

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd travelplanner
```

2. Start the development environment:
```bash
docker compose watch
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

For detailed development instructions, see [CLAUDE.md](./CLAUDE.md).

### Key Commands

**Backend (from `backend/` directory):**
```bash
uv sync                          # Install dependencies
bash ./scripts/test.sh           # Run tests with coverage
bash ./scripts/lint.sh           # Run linting
```

**Frontend (from `frontend/` directory):**
```bash
npm install                      # Install dependencies
npm run dev                      # Start development server
npm run lint                     # Run linting
npm run generate-client          # Generate API client
```

**Docker Development:**
```bash
docker compose watch             # Start with live reload
docker compose logs [service]    # View logs
docker compose down -v           # Stop and clean volumes
```

## Configuration

Update environment variables in `.env` files before deployment:
- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD` 
- `POSTGRES_PASSWORD`

Generate secure keys with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
