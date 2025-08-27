from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

from dotenv import load_dotenv
load_dotenv(".env")

config = context.config

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME")
db_ssl_ca = os.getenv("DB_SSL_CA")

db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": {"ca": db_ssl_ca}} if db_ssl_ca else {},
    )

    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
