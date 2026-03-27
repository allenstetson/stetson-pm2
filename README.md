# Home Projects Manager

A **local-first home project and media management system** designed for a mixed-device household with a Synology NAS at the center.

## Quick Start

### Prerequisites
- Node.js v18+ and npm
- Python 3.12+
- Docker Desktop
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd StetsonProjectManager_v2
   ```

2. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

3. **Start all services with Docker Compose**
   ```bash
   docker-compose up
   ```

   Or use the Makefile (on Windows with WSL):
   ```bash
   make up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

### Local Development (without Docker)

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:5173

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Access at http://localhost:8000

---

## Project Structure

```
StetsonProjectManager_v2/
├── frontend/               # React + TypeScript + Vite application
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile         # Production Docker image
│   └── nginx.conf         # Nginx configuration for production
├── backend/                # FastAPI application
│   ├── app/
│   │   └── main.py        # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Python Docker image
│   └── .env.example       # Environment template for backend
├── docs/                   # Documentation
│   ├── DEVELOPMENT.md     # Development guide
│   └── ARCHITECTURE.md    # Architecture overview
├── scripts/               # Utility scripts
├── docker-compose.yml     # Docker Compose configuration
├── .env.example          # Root environment template
├── Makefile              # Convenient commands (for WSL/Linux)
└── README.md             # This file
```

---

## Technology Stack

### Frontend
- **React** 18+ with TypeScript
- **Vite** for fast development and optimized builds
- **Material-UI (MUI)** for component library
- **npm** for package management

### Backend
- **FastAPI** for REST API
- **SQLAlchemy** for ORM
- **Alembic** for database migrations
- **PostgreSQL 16** for database
- **Python 3.12** runtime

### Deployment
- **Docker** and **Docker Compose** for containerization
- **Nginx** for frontend production server
- **PostgreSQL** for persistent data

---

## Commands

### Using Docker Compose

```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build

# Clean up (remove containers and volumes)
docker-compose down -v
```

### Using Makefile (WSL/Linux/Git Bash)

```bash
make up          # Start services
make down        # Stop services
make logs        # View logs
make build       # Rebuild
make clean       # Remove containers and volumes
```

---

## Development Workflow

1. **Frontend changes**: Edit files in `frontend/src/`. Vite will hot-reload during `npm run dev`.
2. **Backend changes**: Edit files in `backend/app/`. Uvicorn will auto-reload if running with `--reload`.
3. **Database changes**: Use Alembic migrations (see [DEVELOPMENT.md](docs/DEVELOPMENT.md)).

---

## Environment Variables

Copy `.env.example` to `.env` and adjust values as needed:

```env
# Database
DB_USER=projects_user
DB_PASSWORD=projects_password
DB_NAME=projects_db
DB_PORT=5432

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
FRONTEND_PORT=3000

# Environment
ENVIRONMENT=development
```

---

## Contributing

This is a portfolio project. Follow this chunking strategy:
- Read [home-projects-copilot-brief.md](home-projects-copilot-brief.md) for the full product vision
- Implement features in logical, small chunks
- Keep code organized, tested, and well-documented
- Each chunk should result in a working, deployable slice

---

## License

Personal portfolio project.

---

## Next Steps

- See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local development setup
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture overview
- Read [home-projects-copilot-brief.md](home-projects-copilot-brief.md) for product vision and roadmap
