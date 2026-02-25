# Import all the models, so that Base has them before being
# imported by Alembic or used by metadata
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.task import Task  # noqa
