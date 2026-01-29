import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logging.basicConfig (
    filename = "app.log",
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.environ["DATABASE_HOST"],
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"]
        )
        return connection
    except Exception:
        logging.error("Database connection failed")
        return None
    
def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    connection = get_db_connection()
    if connection is None:
        logging.error("Database connection failed")
        return None

    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query, params)
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = None
                connection.commit()
                return result
            except Exception as e:
                connection.rollback()
                logging.error(f"Query failed: {e}")
                return None
