# server/inventory-service/db.py
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def get_db_connection():
    """
    Uses env vars (matches your current style):
      DATABASE_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    """
    try:
        conn = psycopg2.connect(
            host=os.environ["DATABASE_HOST"],
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
        conn.autocommit = False  # IMPORTANT: we want explicit transactions
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    For simple one-shot queries. NOT for the atomic adjust flow.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch_one:
                    return cur.fetchone()
                if fetch_all:
                    return cur.fetchall()
                return True
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
