# Development Guide

## Local Development Setup

This guide covers setting up the development environment **without Docker** for faster iteration.

### Frontend Development

#### Prerequisites
- Node.js v18+ and npm

#### Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env.local file**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` if needed (default points to `http://localhost:8000`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   The app will open at http://localhost:5173 with hot-reload enabled.

5. **Build for production**
   ```bash
   npm run build
   ```

   Output will be in `dist/` directory.

---

### Backend Development

#### Prerequisites
- Python 3.12+
- PostgreSQL 16 (running locally or via Docker)

#### Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # On Windows (Command Prompt)
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your local database connection:
   ```env
   DATABASE_URL=postgresql://projects_user:projects_password@localhost:5432/projects_db
   API_HOST=0.0.0.0
   API_PORT=8000
   ENVIRONMENT=development
   ```

5. **Start the FastAPI server**
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at http://localhost:8000
   - API docs (Swagger): http://localhost:8000/docs
   - Alternative docs (ReDoc): http://localhost:8000/redoc

   The `--reload` flag enables auto-reload on file changes.

---

### Database Setup (Local PostgreSQL)

#### Option 1: Docker (Recommended for Local Dev)

If you have Docker installed, run PostgreSQL in a container:

```bash
docker run --name projects_db \
  -e POSTGRES_USER=projects_user \
  -e POSTGRES_PASSWORD=projects_password \
  -e POSTGRES_DB=projects_db \
  -p 5432:5432 \
  -d postgres:16-alpine
```

To stop:
```bash
docker stop projects_db
docker rm projects_db
```

To restart:
```bash
docker start projects_db
```

#### Option 2: Native PostgreSQL Installation

Install PostgreSQL 16 for your OS and create a database:

```bash
# Create database and user
psql -U postgres -c "CREATE DATABASE projects_db;"
psql -U postgres -c "CREATE USER projects_user WITH PASSWORD 'projects_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE projects_db TO projects_user;"
```

---

### Database Migrations (Alembic)

Alembic is configured for schema management. The initial schema migration (`a1b2c3d4e5f6`) creates all core tables and indexes.

**Migrations run automatically** when the backend Docker container starts (`alembic upgrade head` is prepended to the startup command). For local development without Docker, run manually:

#### Apply all pending migrations

```bash
cd backend
alembic upgrade head
```

#### Create a new migration after changing models

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
# Review the generated file in alembic/versions/ before applying
alembic upgrade head
```

#### Roll back one migration

```bash
alembic downgrade -1
```

#### View migration history

```bash
alembic current
alembic history
```

#### Seed the database with sample data

```bash
# Local venv (from backend/ directory)
python scripts/seed.py

# Inside the running Docker container
docker exec projects_backend python scripts/seed.py
```

The seed script inserts 5 realistic fake projects (home, school, work categories;
family/work/sensitive visibility; various media types). Safe to run multiple
times — skips if data already exists.

---

### Scanner (Chunk 6+)

The scanner walks the `projects_root` directory for `category/project_folder` pairs
and upserts `Project` records into the database.

#### Trigger a scan via HTTP

```bash
curl -X POST http://localhost:8000/api/scan
# or
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/scan"
```

Response:
```json
{ "created": 5, "updated": 3, "skipped": 0, "errors": [] }
```

Scanning is **idempotent**: running it twice always yields `created=0` on the second run.

#### How project directories must be structured

```
projects_root/          ← PROJECTS_ROOT env var; mounted into the container
  home/                 ← category (top-level subdirectory)
    2024_12_25_christmasMorning/   ← project folder (YYYY_MM_DD prefix)
    2024_04_cvhs_music_year_end/   ← project folder (YYYY_MM prefix → day=1)
    2016_halloween/                ← project folder (YYYY prefix → mtime day/month)
    legoAnimation/                 ← project folder (free-form → mtime date)
  school/
    2023_09_01_backToSchool_jonah/
  work/
    2025_01_10_portfolioWebsite/
```

Loose files (not directories) in any level are silently skipped.

#### Date-parsing cascade

| Folder name pattern | Parsed date |
|---|---|
| `YYYY_MM_DD_…` | Exact date from folder name |
| `YYYY_MM_…` | First day of that month |
| `YYYY_…` | Year from folder; month+day from directory `mtime` |
| Free-form | Full date from directory `mtime` |

#### Swapping the project root (local dev → production)

Docker Compose binds `./sample_projects` to `/mnt/projects` by default:

```yaml
# docker-compose.yml
volumes:
  - ./sample_projects:/mnt/projects:ro
environment:
  PROJECTS_ROOT: /mnt/projects
  NAS_ROOT: /volume1/Projects
```

To point at a real NAS share, override both env vars without changing code:

```yaml
volumes:
  - /run/media/nas/Projects:/mnt/projects:ro
environment:
  PROJECTS_ROOT: /mnt/projects
  NAS_ROOT: /volume1/Projects
```

On Synology DSM (no Docker Compose override needed): set `PROJECTS_ROOT=/volume1/Projects`.

#### Windows + Docker Desktop (WSL2 back-end) limitation

Docker Desktop on Windows with the WSL2 back-end **cannot bind-mount mapped
network drives** (e.g. `Y:\`). The bind mount will appear empty inside the
container. Workarounds:

1. **Use `sample_projects/` for dev** — the `./sample_projects` bind mount works
   only if the project itself lives on a local drive (C:, D:, etc.), not on a
   network share. If your project is on a network share, copy `sample_projects/`
   to a local drive and adjust the `docker-compose.yml` volume source.
2. **Switch Docker Desktop to Hyper-V back-end** — Hyper-V can expose network
   drives. Requires Windows Pro/Enterprise and a Docker Desktop restart.
3. **Run the scan from the host directly** — install the backend venv, set
   `PROJECTS_ROOT` to the actual Windows path (e.g. `Y:\home`), and run:
   ```powershell
   python -c "
   from app.database import SessionLocal
   from app.scanner import scan_projects
   db = SessionLocal()
   r = scan_projects('Y:/home', db, nas_root='//NAS/home')
   db.commit(); print(r)
   "
   ```

---

### Environment Variables Reference

#### Backend (.env)
```env
# Database connection string (supports PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# API configuration
API_HOST=0.0.0.0              # Bind address
API_PORT=8000                 # Listen port

# Environment
ENVIRONMENT=development       # development, testing, production

# Scanner (Chunk 6+)
PROJECTS_ROOT=/mnt/projects   # Path inside the container to the project root
NAS_ROOT=/volume1/Projects    # Canonical NAS path stored in project records
```

#### Frontend (.env.local)
```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

#### Root (.env for Docker Compose)
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

# Scanner — override to mount a real NAS share instead of sample_projects/
# PROJECTS_ROOT=/mnt/projects
# NAS_ROOT=/volume1/Projects
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Pydantic settings (DATABASE_URL, PROJECTS_ROOT, etc.)
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── models/              # ORM models
│   │   ├── __init__.py      # Re-exports all models
│   │   ├── base.py          # Base + TimestampMixin
│   │   ├── project.py       # Project model
│   │   ├── tag.py           # Tag + ProjectTag models
│   │   ├── contributor.py   # Contributor + ProjectContributor models
│   │   └── project_link.py  # ProjectLink model
│   ├── schemas/             # Pydantic response schemas
│   │   └── project.py       # ProjectSummary, ProjectListResponse
│   ├── routes/              # FastAPI routers
│   │   ├── projects.py      # GET /api/projects
│   │   └── scan.py          # POST /api/scan
│   └── scanner/             # NAS directory scanner
│       ├── __init__.py
│       └── scanner.py       # parse_project_date, humanize_name, scan_projects
├── alembic/                 # Alembic migration environment
│   ├── env.py               # Migration runner (reads DATABASE_URL from app config)
│   ├── script.py.mako       # Template for new migration files
│   └── versions/            # Migration files
│       └── a1b2c3d4e5f6_initial_schema.py
├── scripts/
│   └── seed.py              # Populates DB with sample projects
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
└── .gitignore               # Git ignore patterns

frontend/
├── src/
│   ├── App.tsx             # Main React component
│   ├── main.tsx            # React DOM entry point
│   ├── index.css           # Global styles
│   ├── api/
│   │   └── projects.ts     # fetchProjects() — calls GET /api/projects
│   ├── types/
│   │   └── project.ts      # TypeScript types for ProjectSummary
│   └── components/
│       ├── layout/          # Header, Sidebar, MainContent, DetailsPanel, Footer
│       └── projects/
│           ├── ProjectCard.tsx
│           └── ProjectList.tsx
├── index.html              # HTML template
├── package.json            # npm dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── vite.config.ts          # Vite configuration
├── Dockerfile              # Production Docker image
└── nginx.conf              # Nginx configuration

sample_projects/            # Committed sample directory tree for local dev
├── README.md               # How to use and swap the sample data
├── home/                   # Category directories
├── school/
└── work/
```

---

## Common Tasks

### Run everything with Docker Compose

```bash
docker-compose up
```

This starts:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- Frontend (Nginx) on port 3000

### Access services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Rebuild Docker images

```bash
docker-compose build
```

### View logs

```bash
# All services
docker-compose logs -f

# Single service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Execute backend Python shell

```bash
docker-compose exec backend python
```

### Execute PostgreSQL shell

```bash
docker-compose exec db psql -U projects_user -d projects_db
```

---

## Troubleshooting

### Port already in use
If ports 3000, 5000, 5173, 8000, or 5432 are in use:
- Modify `.env` to use different ports
- Or stop conflicting services: `docker-compose down`

### Database connection error
Check that PostgreSQL is running and connection string in `.env` is correct:
```bash
# Test connection (from backend directory)
python -c "from sqlalchemy import create_engine; create_engine('postgresql://projects_user:projects_password@localhost:5432/projects_db').connect()"
```

### Frontend can't reach API
Ensure backend is running and `VITE_API_URL` in `frontend/.env.local` points to the correct backend URL (e.g., `http://localhost:8000`).

### Module not found errors
Ensure all dependencies are installed:
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

---

## Next Steps

1. Follow the chunking strategy in [home-projects-copilot-brief.md](../home-projects-copilot-brief.md)
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design overview
3. Start with Chunk 2 (Minimal frontend shell) or Chunk 3 (Minimal backend shell)
