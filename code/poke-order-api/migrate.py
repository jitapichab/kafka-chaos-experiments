from alembic import command
from alembic.config import Config

from app.config import Config as CF


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", CF.DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations()