"""
db_connection.py

Single shared source of truth for the PostgreSQL connection.
Reads credentials from a `.env` file (same folder as this script)
instead of hardcoding them in every load_*.py file.

.env format expected:
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=banking_system
    DB_USER=postgres
    DB_PASSWORD=1234
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Load .env that sits next to this file
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_REQUIRED = {"DB_NAME": DB_NAME, "DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD}
_missing = [key for key, value in _REQUIRED.items() if not value]
if _missing:
    raise RuntimeError(
        f"Missing required DB settings in {ENV_PATH}: {', '.join(_missing)}. "
        "Make sure the .env file exists and contains DB_HOST, DB_PORT, "
        "DB_NAME, DB_USER, DB_PASSWORD."
    )


def get_engine() -> Engine:
    """Return a SQLAlchemy engine built from the .env credentials."""
    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(connection_string)
