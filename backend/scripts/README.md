# Backend scripts

Utility scripts for the Home Projects backend. Run from the `backend/` directory
with the virtual environment active, or inside the Docker container.

## Available scripts

### `seed.py` — Populate the database with sample projects

```bash
# From backend/ directory (local venv)
python scripts/seed.py

# Inside the running Docker container
docker exec projects_backend python scripts/seed.py
```

Seeds 5 realistic fake projects covering different categories (`home`, `school`,
`work`), visibility levels (`family`, `work`, `sensitive`), and media types
(`photo`, `video`, `document`). Safe to run multiple times — skips if data
already exists.
