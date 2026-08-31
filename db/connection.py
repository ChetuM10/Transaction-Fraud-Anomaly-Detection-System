# Database Connection helper
# Reads DATABASE_URL (Render) if present, else falls back to individual .env variables

import os

import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

db_pool = None


def init_pool():
    global db_pool
    if db_pool:
        return

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql://", 1)
        db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, database_url)
    else:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )


class PoolWrapper:
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        # Pass normal commands (like .cursor()) straight to the real connection
        return getattr(self._conn, name)

    def close(self):
        # Intercept .close() and safely put the connection back in the pool
        db_pool.putconn(self._conn)


def get_connection():
    if not db_pool:
        init_pool()
    # Wrap the connection before returning it so .close() behaves safely
    return PoolWrapper(db_pool.getconn())
