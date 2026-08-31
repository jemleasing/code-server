import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )


@contextmanager
def db_cursor(dictionary=True):
    """
    Usage:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            rows = cur.fetchall()
    Connection is closed automatically, even on error.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=dictionary)
    try:
        yield cur
        conn.commit()
    finally:
        cur.close()
        conn.close()
