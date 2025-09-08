"""
Main FastAPI application (No Auth Version)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from database import engine, get_db
from models import Base
from routers import webtoons_router, scenes_router, interactions_router, chat_router

load_dotenv()

# Create all tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="GLTR Webtoon Platform API",
    description="API for GLTR Webtoon Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")
    
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(webtoons_router.router, prefix="/api/webtoons", tags=["Webtoons"])
app.include_router(scenes_router.router, prefix="/api/scenes", tags=["Scenes"])
app.include_router(interactions_router.router, prefix="/api/interactions", tags=["Interactions"])
app.include_router(chat_router.router, prefix="/api", tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    # Tables are already created by Base.metadata.create_all(bind=engine)
    print("Database initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "GLTR Webtoon Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)