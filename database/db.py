import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


@contextmanager
def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "news_recommendation"),
    )
    try:
        yield connection
    finally:
        connection.close()


def fetch_categories(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT category FROM news_articles WHERE category IS NOT NULL AND category <> '' ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories


def _article_query(where_clause="", limit=None):
    query = """SELECT article_id, category, headline, abstract, snippet, lead_paragraph,
               publication_date, byline, url, image_url
               FROM news_articles """ + where_clause + " ORDER BY publication_date DESC"
    if limit:
        query += " LIMIT %s"
    return query


def _rows_to_dicts(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_articles(connection, category, limit=60):
    cursor = connection.cursor()
    cursor.execute(_article_query("WHERE category = %s", limit), (category, limit))
    articles = _rows_to_dicts(cursor)
    cursor.close()
    return articles


def fetch_article(connection, article_id):
    cursor = connection.cursor()
    cursor.execute(_article_query("WHERE article_id = %s"), (article_id,))
    rows = _rows_to_dicts(cursor)
    cursor.close()
    return rows[0] if rows else None


def fetch_model_articles(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT article_id, category, headline, abstract, snippet, lead_paragraph, keywords, section
                     FROM news_articles ORDER BY article_id""")
    rows = cursor.fetchall()
    cursor.close()
    return rows