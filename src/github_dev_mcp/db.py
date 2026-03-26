from contextlib import contextmanager
import psycopg

from github_dev_mcp.config import settings


@contextmanager
def get_db():
    conn = psycopg.connect(settings.postgres_dsn)
    try:
        yield conn
    finally:
        conn.close()