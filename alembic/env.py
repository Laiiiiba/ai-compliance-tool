"""
Alembic environment configuration.

CRITICAL: This file MUST import the single Base and all model modules.
Alembic autogenerate only sees models that are imported here.
"""

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ============================================================================
# CRITICAL IMPORTS: Single Base and Settings
# ============================================================================
# Import the SINGLE Base from our database module
# This is the same Base that all models use
from app.core.database import Base
from app.core.config import settings

# ============================================================================
# CRITICAL IMPORTS: All Model Modules
# ============================================================================
# Every model file must be explicitly imported here for Alembic to see it
# Even if we don't have models yet, we prepare the structure

# Future model imports will go here:
from app.db.models.project import Project
from app.db.models.assessment import Assessment
from app.db.models.answer import Answer
from app.db.models.regulatory_flag import RegulatoryFlag

# For now, we have no models, but the import structure is ready


# ============================================================================
# Alembic Configuration
# ============================================================================

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the SQLAlchemy URL from our settings
# This overrides whatever is in alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# ============================================================================
# CRITICAL: Set target_metadata to our single Base
# ============================================================================
# This tells Alembic which metadata to compare against the database
# Since all our models inherit from this Base, Alembic will see all of them
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Include schemas if using PostgreSQL schemas
        # include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Compare table and column types
            compare_type=True,
            # Compare server defaults
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()