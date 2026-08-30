# Database Connection helper
# Reads DATABASE_URL (Render) if present, else falls back to individual .env variables

import os

import psycopg2
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


def get_connection():
    if not db_pool:
        init_pool()

    conn = db_pool.getconn()

    # Clever trick: when routes.py calls conn.close(),
    # put it back in the pool instead of actually closing the TCP socket!
    def pool_close():
        db_pool.putconn(conn)

    conn.close = pool_close
    return conn
