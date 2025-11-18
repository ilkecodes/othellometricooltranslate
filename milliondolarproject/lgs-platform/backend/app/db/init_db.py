from .base import Base
from .session import engine

def init_db():
    """Create all tables using the engine from `app.db.session`.

    This is a synchronous helper for initial local setup. For production
    migrations, use Alembic.
    """
    Base.metadata.create_all(bind=engine)
