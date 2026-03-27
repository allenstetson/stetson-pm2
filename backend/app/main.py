from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Home Projects API",
    description="Local-first home project and media management system",
    version="0.1.0",
)

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def get_health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Home Projects API v0.1.0"}
