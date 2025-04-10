import logging
import os

from alembic.config import Config
from alembic import command
from alembic.util.exc import CommandError

path = os.path.join(os.getcwd(), "api_framework", "migrations", "alembic.ini")

alembic_cfg = Config(path)
logger = logging.getLogger(__name__)


def generate_revision(msg: str) -> None:
    try:
        command.revision(alembic_cfg, message=msg, autogenerate=True)
    except CommandError as e:
        logger.error(f"Error during generating revision: {e}")


def upgrade() -> None:
    try:
        command.upgrade(alembic_cfg, "head")
    except CommandError as e:
        logger.error(f"Error during migration: {e}")


def downgrade(revision: str = "-1") -> None:
    try:
        command.downgrade(alembic_cfg, revision)
    except CommandError as e:
        logger.error(f"Error during downgrade: {e}")
