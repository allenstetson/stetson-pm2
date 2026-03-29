from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://projects_user:projects_password@db:5432/projects_db"
    environment: str = "development"

    # Path the backend container (or local process) can read for scanning.
    # In Docker: mount the real NAS share or sample_projects/ to this path.
    # On Synology: /volume1/Projects
    # Local dev (sample data): /mnt/projects  (bound to ./sample_projects)
    # Local dev (real NAS via Y:\): bind Y:\: to /mnt/projects and set this.
    projects_root: str = "/mnt/projects"

    # The NAS path prefix to store in project records for display purposes.
    # Allows the UI to show the canonical NAS location even when the container
    # reads from a different mount point.
    # e.g. "/volume1/Projects" on Synology, "//NAS/Projects" for UNC path.
    nas_root: str = "/volume1/Projects"

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """FastAPI dependency that returns a Settings instance."""
    return Settings()


settings = Settings()
