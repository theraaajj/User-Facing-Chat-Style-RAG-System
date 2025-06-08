import os
import mysql.connector
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_documents_by_president(president_name: str, month: str):
    query = f"""
        SELECT document_number, title
        FROM federal_register_documents
        WHERE president = %s AND publication_date LIKE %s
        ORDER BY publication_date DESC
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, (president_name, f"%{month}%"))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_documents_by_topic(topic_keywords: str):
    keywords = topic_keywords.split()
    conditions = " OR ".join(["title LIKE %s OR summary LIKE %s" for _ in keywords])
    values = []
    for kw in keywords:
        values.extend([f"%{kw}%", f"%{kw}%"])

    query = f"""
        SELECT document_number, title
        FROM federal_register_documents
        WHERE {conditions}
        ORDER BY publication_date DESC
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, tuple(values))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_documents_by_date_range(start_date: str, end_date: str):
    query = f"""
        SELECT document_number, title
        FROM federal_register_documents
        WHERE publication_date BETWEEN %s AND %s
        ORDER BY publication_date DESC
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_latest_documents(limit: int = 5):
    query = f"""
        SELECT document_number, title
        FROM federal_register_documents
        ORDER BY publication_date DESC
        LIMIT %s
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
