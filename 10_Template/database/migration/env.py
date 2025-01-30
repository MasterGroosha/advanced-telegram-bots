import asyncio
from logging.config import fileConfig

from alembic import context
from dynaconf import Dynaconf

# this is the Alembic BotConfig object, which provides
# access to the values within the .ini file in use.
from sqlalchemy.ext.asyncio import create_async_engine

from config import Config
from database.models import Base

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_name(name, type_, _):
    if type_ == 'table':
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    settings = Dynaconf(
        envvar_prefix='APP_CONF',
        settings_files=['settings.toml', '.secrets.toml'],
    )
    app_config: Config = Config.parse_obj(settings)
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=app_config.db.uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    settings = Dynaconf(
        envvar_prefix='APP_CONF',
        settings_files=[
            'ROOT DIR OF PROJECT/settings.toml',
            'ROOT DIR OF PROJECT/.secrets.toml',
        ],
    )
    app_config: Config = Config.parse_obj(settings)
    connectable = create_async_engine(
        app_config.db.uri, **app_config.db.orm.engine.dict()
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
