"""
main.py — Asana Studio FastAPI application.
Serves API + static frontend files.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ensure backend is importable
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, db_is_seeded
from routers import poses, sequences, practices

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@asynccontextmanager
async def lifespan(app):
    """Initialize database and seed if needed."""
    init_db()
    if not db_is_seeded():
        from seed_poses import seed_database
        seed_database()
    yield


app = FastAPI(
    title="Asana Studio",
    description="Comprehensive yoga pose database, sequence generator, and practice builder.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(poses.router)
app.include_router(sequences.router)
app.include_router(practices.router)

# Serve frontend static files
for subdir in ("css", "js", "assets"):
    dirpath = os.path.join(FRONTEND_DIR, subdir)
    if os.path.isdir(dirpath):
        app.mount(f"/{subdir}", StaticFiles(directory=dirpath), name=subdir)


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
def health():
    from database import get_connection
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM poses").fetchone()[0]
    conn.close()
    return {"status": "healthy", "poses_count": count}
