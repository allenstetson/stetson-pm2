This directory is a committed sample of the Projects directory structure used for local development.

It mirrors the real NAS layout:

  Projects/
    home/       <- family home projects
    school/     <- school events and recordings
    work/       <- work and professional projects

To scan these into the database:

  docker exec projects_backend python scripts/scan.py

Or via the API:

  POST http://localhost:8000/api/scan

To point the scanner at a different root (real NAS share, Y:\ drive, etc.),
change the PROJECTS_ROOT environment variable in docker-compose.yml and update
the volume mount accordingly. The scanner code is identical either way.

See docs/DEVELOPMENT.md for full instructions.
