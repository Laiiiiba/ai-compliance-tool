"""
FastAPI application entry point.

This module creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging


# Set up logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Code before 'yield' runs on startup.
    Code after 'yield' runs on shutdown.
    
    This is where you:
    - Initialize database connections
    - Load ML models
    - Start background tasks
    - Clean up resources on shutdown
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 60)
    
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
# Allows frontend applications to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns basic API information.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Used by:
    - Docker healthchecks
    - Kubernetes liveness/readiness probes
    - Monitoring systems (Prometheus, DataDog, etc.)
    
    Returns:
        dict: Health status and basic system information
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env
    }


# Additional endpoints will be added here in future steps
# We'll use APIRouter to organize endpoints by domain