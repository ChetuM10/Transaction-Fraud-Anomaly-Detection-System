# Database Connection helper
# Reads DATABASE_URL (Render) if present, else falls back to individual .env variables

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    # Render provides a single DATABASE_URL string
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Render uses postgres:// but psycopg2 needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(database_url)

    # Local development fallback using individual variables
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Connected to Database Successfully!")
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
