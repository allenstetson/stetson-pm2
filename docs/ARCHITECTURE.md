# System Architecture

## Overview

This is a **local-first, three-tier system** for browsing and managing projects stored on a Synology NAS.

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser / Client                      │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / REST
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  Frontend (React + Vite)                    │
│  - Layout: Header, Nav, Content, Details, Footer           │
│  - Core UI: Project list, filters, search, details panel   │
│  - Consumes API via fetch / axios                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / REST API
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               Backend (FastAPI + Python)                    │
│  - REST API: /projects, /health, /search, etc.              │
│  - CORS middleware for frontend dev                         │
│  - Authentication & authorization stubs (future)            │
│  - Business logic & validation                              │
└───────────────────────┬─────────────────────────────────────┘
                        │ SQL / Connection Pool
                        │
┌───────────────────────▼─────────────────────────────────────┐
│           Database (PostgreSQL 16)                          │
│  - Persistent schema: projects, metadata, backup info, etc. │
│  - Searchable indices on tags, categories, etc.             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### 1. Local-First Design
- **Original media remains on Synology NAS** — the app does not copy or stream media
- **Metadata is in PostgreSQL** — project names, categories, tags, backup states, file counts, etc.
- **App is a thin metadata browser** — not a media hub or editor

### 2. Three-Tier Architecture
- **Frontend (React)** — user interface, rendering, client-side validation
- **Backend (FastAPI)** — API, business logic, database queries, permissions
- **Database (PostgreSQL)** — single source of truth for all metadata

### 3. Simple Before Complex
- **Health endpoint only** — `/health` returns basic status
- **No queuing yet** — background work is deferred to later chunks
- **Minimal project model** — core fields only in Chunk 4

### 4. Development vs. Production
- **Local dev**: frontend (`npm run dev`), backend (`uvicorn --reload`), PostgreSQL in Docker
- **Production**: Docker Compose orchestrates all three; frontend is pre-built and served by Nginx

---

## Deployment Context

### Local Development
```
Windows 11 Workstation
├── VS Code + Git
├── Node.js / npm (frontend dev)
├── Python 3.12 / venv (backend dev)
└── Docker Desktop
    ├── PostgreSQL container (if not using local install)
    └── Backend + Frontend containers (optional)
```

### Home Network Deployment (Synology NAS)
```
Synology NAS
├── Docker Compose
│   ├── Frontend (Nginx + React SPA)
│   ├── Backend (FastAPI + Python)
│   └── Database (PostgreSQL)
└── NAS Storage
    ├── Projects/ (original media)
    │   ├── home/...
    │   ├── school/...
    │   └── work/...
    └── Backups/
```

---

## Core Layers

### Frontend Layer (React + TypeScript + Vite)

**Responsibility**: Render UI, handle user input, call API, manage UI state

**Components**:
- **Header**: Branding, logout, settings
- **Left Navigation**: Category filters (home, school, work), sections
- **Center Content**: Project list, search bar, filters
- **Right Details Panel**: Selected project metadata
- **Footer**: Version, status indicators

**State Management**: Local React state for now; Redux/Zustand deferred unless needed

**API Client**: Fetch API or axios (to be decided)

**Key Pages**:
- Projects list view (default)
- Project details (right panel)
- Search / filter interface (integrated in list)

---

### Backend Layer (FastAPI + Python)

**Responsibility**: API endpoints, data validation, business logic, database queries, auth (stub)

**Core Modules**:
- `app/main.py`: FastAPI app, CORS, health endpoint
- `app/routes/` (future): Project routes, search routes, admin routes
- `app/models/` (future): SQLAlchemy ORM models
- `app/schemas/` (future): Pydantic request/response schemas
- `app/services/` (future): Business logic (project scanning, permission checks, etc.)

**Authentication** (stub for now, real implementation in Chunk 11):
- Placeholder for user context
- Role-based access control (admin, editor, viewer)
- Sensitivity labels (family, school, work, sensitive)

**Key Endpoints** (Chunk 5 onwards):
- `GET /health` ✓ (Chunk 1)
- `GET /projects` (Chunk 5)
- `GET /projects/{id}` (Chunk 5)
- `POST /search` (Chunk 8)
- `GET /projects?category=home` (Chunk 8)
- And more...

---

### Database Layer (PostgreSQL 16)

**Responsibility**: Persistent storage, transactions, querying

**Core Tables** (to be created in Chunk 4):
- `projects` — id, name, category, path, created_at, modified_at, archived
- `project_metadata` — tags, media_types, file_count, disk_usage, last_sync
- `backup_info` — last_backup_date, backup_host, last_sync_date
- `users` (Chunk 11) — id, username, email, role, password_hash
- `project_visibility` (Chunk 11) — project_id, visibility_label
- (More as features are added)

**Migrations**: Alembic manages schema versions

---

## Technology Choices

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React | Popular, component-based, large ecosystem |
| Frontend Build | Vite | Fast dev server, optimized production builds |
| Frontend Styling | MUI | Rich component library, professional UI |
| Frontend Lang | TypeScript | Type safety, better IDE support, catches errors early |
| Backend | FastAPI | Modern, fast, Pythonic, great for async, built-in API docs |
| Backend DB | SQLAlchemy | ORM, migrations (Alembic), type-safe queries |
| Database | PostgreSQL | Open-source, reliable, rich query language, excellent for metadata |
| Deployment | Docker Compose | Simple orchestration, local dev mirrors production |
| Environment | Python 3.12 | Latest LTS-ish version, good ecosystem support |

---

## Workflow: Data Inquiry Example

**User clicks "Projects" and filters by category "home":**

1. **Frontend** (React):
   - User selects filter "home" from left nav
   - Component calls `GET /projects?category=home`

2. **Backend** (FastAPI):
   - Route handler receives query param `category=home`
   - Queries PostgreSQL: `SELECT * FROM projects WHERE category='home'`
   - Returns JSON array of projects

3. **Database** (PostgreSQL):
   - Executes query, returns matching rows

4. **Frontend** (React):
   - Receives JSON, updates state
   - Re-renders project list with filtered results

---

## Security Considerations (to Implement Later)

- **Sensitive projects** should not appear to users who lack permission
- **Password hashing** required for user authentication
- **CORS** configured to whitelist frontend origin only
- **HTTPS** in production (LetsEncrypt or self-signed)
- **Environment variables** for secrets (DB password, API keys, etc.)

---

## Scalability Notes

- **Initial target**: Single-household use, ~100-1000 projects
- **Bottleneck avoidance**: Index on category, tags, contributor for fast searches
- **Future optimization**: Caching, pagination, async file scanning (Chunks 6+)
- **Not for**: Multi-tenant SaaS, large-scale media streaming

---

## Next Steps

1. **Chunk 2**: Build minimal frontend layout without data
2. **Chunk 3**: Build minimal backend health check
3. **Chunk 4**: Add database schema and migrations
4. **Chunk 5**: Wire frontend to backend with API call
5. Continue through chunking strategy in [home-projects-copilot-brief.md](../home-projects-copilot-brief.md)

---

## Appendix: Key Files

- [backend/app/main.py](../backend/app/main.py) — FastAPI app entry point
- [frontend/src/App.tsx](../frontend/src/App.tsx) — React layout component
- [docker-compose.yml](../docker-compose.yml) — Container orchestration
- [README.md](../README.md) — Quick-start guide
- [DEVELOPMENT.md](DEVELOPMENT.md) — Local dev setup
