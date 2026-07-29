# Database Connection helper
# Reads credentials from .env

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
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
