"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from src.config import get_settings
from src.database import init_db
from src.schemas import HealthResponse
from src.skills import get_enabled_skill_routers
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    # Startup
    logger.info("Starting HHM Backend...")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database unavailable at startup (skills will still work): {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HHM Backend...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Health check endpoint
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version=settings.api_version,
            timestamp=datetime.utcnow(),
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "HHM - Happy Household Manager",
            "version": settings.api_version,
            "docs": "/docs",
        }
    
    # Skills endpoint - list available household skills
    @app.get("/skills")
    async def list_skills():
        """List enabled household skills"""
        from src.skills import get_enabled_skills
        skills = get_enabled_skills()
        return {
            "count": len(skills),
            "skills": [{"id": s.id, "enabled": s.is_enabled()} for s in skills],
        }
    
    # Register skill routers
    skill_routers = get_enabled_skill_routers()
    for router in skill_routers:
        app.include_router(router)
    
    if skill_routers:
        logger.info(f"Registered {len(skill_routers)} skill routers")
    
    logger.info("FastAPI application created successfully")
    return app


# Create application instance
app = create_app()
