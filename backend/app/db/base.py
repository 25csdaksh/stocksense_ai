"""
SQLAlchemy 2.0 Base Declarative Model & Mixins.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import MetaData, Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, declared_attr

# Naming convention for clean foreign keys, unique constraints, and indexes
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


def utc_now() -> datetime:
    """Returns current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generates standard UUID4 string."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 models."""
    metadata = metadata


class TimestampMixin:
    """Mixin for models requiring created_at and updated_at audit timestamps."""
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class UUIDPrimaryKeyMixin:
    """Mixin providing UUID string primary keys."""
    id = Column(String(36), primary_key=True, default=generate_uuid)
