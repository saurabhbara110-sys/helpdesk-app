import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

pool = ConnectionPool(
    conninfo=f"host={os.getenv('DB_HOST', 'localhost')} "
             f"dbname={os.getenv('DB_NAME', 'helpdesk_db')} "
             f"user={os.getenv('DB_USER', 'helpdesk_user')} "
             f"password={os.getenv('DB_PASSWORD')}"
)


def get_user(username):
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password, department, role
                FROM users
                WHERE username = %s;
                """,
                (username,)
            )

            return cursor.fetchone()
