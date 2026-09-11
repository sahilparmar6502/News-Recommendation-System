import csv
import os
import sys

import mysql.connector
from dotenv import load_dotenv


load_dotenv()
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "news.csv")
TABLE_SQL = """CREATE TABLE IF NOT EXISTS news_articles (
    article_id VARCHAR(100) PRIMARY KEY,
    category VARCHAR(150), headline TEXT, abstract TEXT, snippet TEXT,
    lead_paragraph TEXT, keywords LONGTEXT, section VARCHAR(150),
    subsection VARCHAR(150), publication_date DATETIME NULL, source VARCHAR(255),
    byline VARCHAR(500), article_type VARCHAR(100), url TEXT, image_url TEXT,
    fetched_at DATETIME NULL,
    INDEX idx_category (category), INDEX idx_publication_date (publication_date)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
INSERT_SQL = """INSERT INTO news_articles
 (article_id, category, headline, abstract, snippet, lead_paragraph, keywords, section,
  subsection, publication_date, source, byline, article_type, url, image_url, fetched_at)
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
 ON DUPLICATE KEY UPDATE category=VALUES(category), headline=VALUES(headline),
 abstract=VALUES(abstract), snippet=VALUES(snippet), lead_paragraph=VALUES(lead_paragraph),
 keywords=VALUES(keywords), publication_date=VALUES(publication_date), image_url=VALUES(image_url)"""


def clean(value):
    return value.strip() or None if value else None


def parse_datetime(value):
    return clean(value).replace("T", " ").replace("Z", "") if clean(value) else None


def row_values(row):
    return tuple(clean(row.get(column)) for column in (
        "article_id", "category", "headline", "abstract", "snippet", "lead_paragraph",
        "keywords", "section", "subsection")) + (parse_datetime(row.get("publication_date")),) + tuple(
        clean(row.get(column)) for column in ("source", "byline", "article_type", "url", "image_url")) + (parse_datetime(row.get("fetched_at")),)


def main():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"), port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"), password=os.getenv("MYSQL_PASSWORD", ""),
    )
    database = os.getenv("MYSQL_DATABASE", "news_recommendation")
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE `{database}`")
    cursor.execute(TABLE_SQL)
    with open(CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        batch = []
        imported = 0
        for row in reader:
            batch.append(row_values(row))
            if len(batch) == 1000:
                cursor.executemany(INSERT_SQL, batch)
                connection.commit()
                imported += len(batch)
                batch.clear()
        if batch:
            cursor.executemany(INSERT_SQL, batch)
            connection.commit()
            imported += len(batch)
    cursor.close()
    connection.close()
    print(f"Imported {imported} articles into {database}.news_articles")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Database setup failed: {error}", file=sys.stderr)
        raise