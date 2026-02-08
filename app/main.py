"""
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import check_database_connection

# Import routers
from app.api.endpoints import projects, assessments


# Set up logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 60)
    
    # Check database connection
    if check_database_connection():
        logger.info("✓ Database connection verified")
    else:
        logger.error("✗ Database connection failed!")
        logger.warning("Application will start but database operations will fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Cleanup completed")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-grade tool for AI compliance and risk assessment",
    debug=settings.debug,
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(projects.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = check_database_connection()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": "connected" if db_healthy else "disconnected"
    }
