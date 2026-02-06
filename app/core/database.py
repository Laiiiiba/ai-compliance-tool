"""
Database configuration and session management.

CRITICAL: This module defines THE SINGLE SQLAlchemy Base for the entire application.
All models MUST import Base from here. Never create a second Base.

This is essential for Alembic autogenerate to work correctly.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine,text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings


logger = logging.getLogger(__name__)


# ============================================================================
# CRITICAL: THE SINGLE BASE
# ============================================================================
# This is the ONLY place where Base is created.
# All models in app/db/models/ must import this Base.
# Never use declarative_base() anywhere else in the codebase.
# ============================================================================

Base = declarative_base()


# ============================================================================
# Database Engine Configuration
# ============================================================================

# Create database engine
# - pool_pre_ping: Verify connections before using them (handles stale connections)
# - echo: Log all SQL statements (useful in development, disable in production)
# - pool_size: Number of connections to maintain
# - max_overflow: Additional connections when pool is exhausted

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connection is alive before using
    echo=settings.debug,  # Log SQL in development only
    pool_size=5,  # Keep 5 connections in pool
    max_overflow=10,  # Allow up to 15 total connections (5 + 10 overflow)
)


# ============================================================================
# Session Factory
# ============================================================================

# SessionLocal is a factory for creating database sessions
# - autocommit=False: We explicitly control when to commit (safer)
# - autoflush=False: We explicitly control when to flush (more predictable)
# - bind=engine: Sessions created by this factory use our engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================================
# Dependency Injection
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI endpoints.
    
    Usage in endpoints:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    How it works:
        1. Creates a new session for each request
        2. Yields the session to the endpoint
        3. Automatically closes the session after the request
        4. Rolls back on exceptions to prevent partial commits
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================

def create_tables() -> None:
    """
    Create all database tables defined by models.
    
    WARNING: This is for testing/development only.
    In production, use Alembic migrations instead.
    
    This function creates tables based on Base.metadata.
    Since all models import the single Base, all tables will be created.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This destroys all data! Use with extreme caution.
    Only for testing/development.
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


# ============================================================================
# Database Health Check
# ============================================================================

def check_database_connection() -> bool:
    """
    Verify database connectivity.
    
    Used by health check endpoint and startup checks.
    
    Returns:
        bool: True if database is reachable, False otherwise
    """
    try:
        # Try to connect to the database
        # IMPORTANT: Use text() to wrap raw SQL queries in SQLAlchemy 2.0
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # ← CHANGED: Added text()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False