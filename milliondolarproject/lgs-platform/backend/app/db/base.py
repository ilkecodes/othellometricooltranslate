"""Unified SQLAlchemy Base for the application.

This module re-exports the declarative base used by the models so that
Alembic and other parts of the application can import a single `Base`.
The actual base is defined in `app.models.base` (as_declarative) and
is re-exported here. We also import model modules so their classes are
registered on the Base.metadata for autogenerate.
"""

from app.models.base import Base  # the as_declarative Base used by models

# Import models so they are registered on Base.metadata for Alembic autogenerate
from app.models import (
    user as user_model,
    school as school_model,
    curriculum as curriculum_model,
    question as question_model,
    exam as exam_model,
    stats as stats_model,
    student_profile as student_profile_model,
)

# Re-export Base
# (other modules should import `from app.db.base import Base`)