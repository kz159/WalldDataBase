from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import os
import sys
path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from walld_db.models import get_psql_dsn, BASE
from walld_db.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

# Interpret the config file for Python logging.
# This line sets up loggers basically.
config = context.config
config.set_main_option('sqlalchemy.url', get_psql_dsn(DB_USER,
                                                      DB_PASSWORD,
                                                      DB_HOST,
                                                      DB_PORT,
                                                      DB_NAME))

fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BASE.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
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
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
