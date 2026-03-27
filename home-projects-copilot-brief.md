# Home Projects — Copilot Project Brief

## Instructions for AI Coding Agents

This document defines the system to be built.
Follow the chunking strategy exactly.
Focus only on the current chunk when prompted.
Do not implement future features unless explicitly requested.
Prefer simple, working solutions over complex abstractions.

## Purpose

This project is a **local-first home project and media management system** designed for a mixed-device household with a Synology NAS at the center.

It serves two goals:

1. **Real household value**
   - Inventory projects stored on the Synology NAS
   - Search projects by metadata such as people, media types, tags, and category
   - Track backup state and whether a project has changed since last offline backup
   - Enforce or encourage a project naming convention
   - Hide sensitive projects from non-privileged family members
   - Offer actions like opening a project in local applications

2. **Portfolio value**
   - Demonstrate strong product thinking
   - Showcase UI engineering, API design, database design, background processing, permissions, and deployment
   - Be suitable to discuss with prospective employers because work code cannot be shared

---

## Core Product Vision

The application will provide a browser-based interface for viewing and managing projects stored on the Synology NAS.

### Example capabilities
- View all projects
- Filter by category such as `home`, `school`, `work`
- Search for projects that include a given person, such as `Jonah`
- Find projects containing photos, video, or documents
- Track last offline backup date
- Detect whether the project has changed since backup
- Mark projects as sensitive and restrict who can view them
- Launch project-related workflows such as:
  - browse project files
  - open project in Premiere
  - open photos in Lightroom
  - browse folder in Explorer or Finder

---

## Deployment Context

### Home environment
- Primary workstation: Windows 11 desktop
- Additional devices: Windows laptops, Apple laptops, family devices
- Central storage: Synology NAS
- Shared project directory on NAS: `Projects`
- Typical directory structure:
  - `Projects/home/...`
  - `Projects/school/...`
  - `Projects/work/...`
- Typical project naming pattern:
  - `YYYY_MM_DD_description`
  - example: `2025_02_14_valentinesDay`

### Development approach
- Development will happen on the Windows machine using a real IDE
- Repository should live locally on the Windows machine, **not directly on an SMB-mounted Synology share**
- Deployment target is Synology Container Manager / Docker Compose
- GitHub Copilot will be used heavily to implement the software from prompts in logical chunks

---

## Recommended Tech Stack

### Frontend
- **React**
- **TypeScript**
- **Vite**
- **MUI** for UI components

### Backend
- **Python 3.12**
- **FastAPI**
- **SQLAlchemy**
- **Alembic**

### Database
- **PostgreSQL 16**

### Background processing
- Python worker service
- Initial implementation should be simple and not over-engineered
- Avoid Celery at first unless there is a real need

### Deployment
- **Docker Compose**
- Runs locally during development
- Runs on Synology NAS for household use

### File/media utilities
- `ffmpeg` / `ffprobe`
- `Pillow`

### Authentication and authorization
- Local users table
- Password hashing
- Roles:
  - `admin`
  - `editor`
  - `viewer`
- Visibility labels:
  - `family`
  - `school`
  - `work`
  - `sensitive`

---

## Architectural Principles

1. **Local-first**
   - Original media remains on the Synology NAS
   - Database stores metadata, file paths, labels, backup information, and search-oriented details
   - Thumbnails and previews may be cached separately

2. **Simple before sophisticated**
   - Build a thin but working end-to-end slice first
   - Prefer working vertical slices over ambitious frameworks early
   - Keep the queueing story simple until real pressure appears

3. **Safe and privacy-aware**
   - Sensitive media should not be exposed casually
   - Support restricted visibility of projects
   - Avoid unnecessary cloud dependence for private data

4. **Portfolio-friendly**
   - Favor familiar, modern tooling that employers understand quickly
   - Keep code organized and production-minded
   - Make the app easy to demo

---

## Initial Functional Areas

### 1. Project inventory
The system should discover and store project records based on the NAS directory structure.

At minimum, a project should capture:
- unique ID
- project name
- category
- NAS directory
- local directory if applicable
- created/modified dates
- tags
- file types
- number of files
- disk usage
- archived state
- thumbnail path
- last sync / last backup metadata
- notes
- links
- contributors
- clients / contacts if relevant

### 2. Search and filtering
The system should support filtering by:
- category
- tags
- project type
- project status
- archived state
- media type
- contributor
- text search
- changed since backup
- sensitive visibility rules

### 3. Backup tracking
The system should track:
- last offline backup date
- backup host / target
- whether project contents have changed since that backup

### 4. Sensitive project visibility
Projects may have a sensitivity level or labels that determine who can see them.

### 5. App integrations
The system may eventually support launching local applications or opening folders.

This should **not** be a first milestone because browser apps cannot directly launch arbitrary local applications without a local helper or desktop wrapper.

---

## Logical Chunking Strategy

The implementation should be broken into small, testable, low-risk chunks.

### Chunk 1 — Project skeleton and documentation
Goal:
- Create repo structure
- Add backend and frontend folders
- Add Docker Compose skeleton
- Add README and environment templates

Success criteria:
- Repo builds cleanly
- Frontend and backend folders exist
- Docker Compose file exists, even if services are stubbed

### Chunk 2 — Minimal frontend shell
Goal:
- Create a very simple React app
- Layout should show the major panels only
- No real data yet

Example layout:
- top header bar
- left navigation panel
- center main content panel
- right details panel
- footer or status area

Success criteria:
- App launches
- Panels render cleanly
- Uses a clean component structure

### Chunk 3 — Minimal backend shell
Goal:
- Create FastAPI app with health endpoint
- Add database connection config
- Add Dockerfile for backend

Success criteria:
- `/health` returns success
- backend runs in Docker
- frontend and backend can both start

### Chunk 4 — Database foundation
Goal:
- Add SQLAlchemy models and Alembic migrations
- Create initial `projects` table and related tables

Success criteria:
- migration runs successfully
- DB container starts
- tables exist

### Chunk 5 — End-to-end vertical slice: list projects
Goal:
- Add a `GET /projects` endpoint
- Frontend calls it and renders a simple project list
- Use seed data first

Success criteria:
- user can open the app and see projects from API
- loading and error states exist

### Chunk 6 — Scanner foundation
Goal:
- Add read-only scanning of a sample `Projects` directory
- Create projects in DB from folder structure
- Infer category and project name from folders

Success criteria:
- scan job populates DB
- frontend list reflects scanned projects

### Chunk 7 — Project details panel
Goal:
- When a project is selected, show detail fields in the right panel

Success criteria:
- selection works
- details update correctly
- detail card is easy to extend

### Chunk 8 — Search and filter basics
Goal:
- Add text search and basic category filter
- Filter results in frontend using backend query params

Success criteria:
- user can type a search
- user can choose category
- results update reliably

### Chunk 9 — Naming convention support
Goal:
- Detect whether folder names match expected naming convention
- Show compliance state in UI

Success criteria:
- projects show compliant / non-compliant state
- logic is isolated and testable

### Chunk 10 — Backup metadata
Goal:
- Add fields and UI for last backup date, backup host, and changed-since-backup indicator

Success criteria:
- project details show backup state
- project list can filter by changed-since-backup

### Chunk 11 — Permissions and sensitive visibility
Goal:
- Add users, roles, and a simple project visibility rule
- Prevent some users from seeing `sensitive` projects

Success criteria:
- restricted user cannot see sensitive items
- admin can see everything

### Chunk 12 — Media-aware indexing
Goal:
- Identify whether a project contains photos, videos, documents, or mixed media
- Capture some aggregate stats

Success criteria:
- file type data appears in project details
- list filters can use media type

### Chunk 13 — Polish and demo readiness
Goal:
- Improve UI clarity and consistency
- Add empty states, error states, and pleasant styling
- Prepare seed/demo dataset

Success criteria:
- app feels intentional
- app can be demoed without private real household data

### Chunk 14 — Optional native integration
Goal:
- Investigate local helper or desktop wrapper
- Enable actions like open folder or open in local app

Success criteria:
- one safe local action works on Windows
- architecture remains clean

## Explicit Non-Goals for Early Milestones

The following should be avoided at the beginning:
- cloud deployment of private media
- advanced ML or face recognition
- complex queueing infrastructure
- direct native application launching from the browser
- premature microservices
- advanced CDN work
- polished mobile app
- complex permissions beyond basic roles and labels

---

## Definition of Success for the Early Product

The first meaningful success milestone is:

> A browser-based app running locally that lists projects from the backend, allows selecting a project to view details, and is backed by a real PostgreSQL database with seed or scanned data.

That milestone should come before any advanced feature work.

---

## Long-Term Possibilities

After the core product is stable, future extensions could include:
- better media indexing
- thumbnail generation
- semantic search
- local helper for native app launching
- Tauri desktop wrapper
- backup verification workflows
- cloud-hosted demo environment with synthetic data
- public portfolio demo with fake projects
