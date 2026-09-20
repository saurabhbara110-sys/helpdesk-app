import os
import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "helpdesk_db"),
        user=os.getenv("DB_USER", "helpdesk_user"),
        password=os.getenv("DB_PASSWORD")
    )
