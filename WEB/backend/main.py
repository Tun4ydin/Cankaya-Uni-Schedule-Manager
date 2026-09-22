import sys
import os

# Base directory setup
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import courses, scheduler, profile, transcript, curriculum, sync

app = FastAPI(
    title="Çankaya University Schedule Manager API",
    description="FastAPI backend for Çankaya University Schedule Manager web application",
    version="1.0.0"
)

# CORS middleware for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router)
app.include_router(scheduler.router)
app.include_router(profile.router)
app.include_router(transcript.router)
app.include_router(curriculum.router)
app.include_router(sync.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Çankaya University Schedule Manager API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
