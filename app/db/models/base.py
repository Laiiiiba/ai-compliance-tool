"""
Base model with common fields for all database models.

Provides timestamp tracking that applies to all models.
"""

from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.
    
    These fields are automatically managed:
    - created_at: Set when record is inserted
    - updated_at: Set when record is inserted, updated on every change
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Database sets this on insert
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Database sets this on insert
        onupdate=func.now(),  # Database updates this on every update
        nullable=False,
        comment="Timestamp when record was last updated"
    )