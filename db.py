import psycopg

def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="helpdesk_db",
        user="helpdesk_user",
        password="REDACTED_PASSWORD"
    )
