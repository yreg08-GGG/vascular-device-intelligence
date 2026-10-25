"""Local SQLite persistence, including overlapping topic membership."""
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB = Path(__file__).resolve().parent.parent / 'data' / 'publications.sqlite3'


def connect(db=DEFAULT_DB):
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    connection.executescript('''
        CREATE TABLE IF NOT EXISTS publications (
            pmid TEXT PRIMARY KEY, title TEXT NOT NULL, publication_date TEXT,
            journal TEXT, abstract TEXT, fetched_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS topics (
            pmid TEXT REFERENCES publications(pmid), topic TEXT NOT NULL,
            PRIMARY KEY (pmid, topic));
    ''')
    return connection


def save_publications(publications, topic, db=DEFAULT_DB):
    connection = connect(db)
    try:
        with connection:
            for p in publications:
                connection.execute('''INSERT INTO publications VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(pmid) DO UPDATE SET title=excluded.title,
                    publication_date=excluded.publication_date, journal=excluded.journal,
                    abstract=excluded.abstract, fetched_at=excluded.fetched_at''',
                    (p.pmid, p.title, p.publication_date, p.journal, p.abstract, datetime.now(timezone.utc).isoformat()))
                connection.execute('INSERT OR IGNORE INTO topics VALUES (?, ?)', (p.pmid, topic))
    finally:
        connection.close()


def load_publications(topic=None, db=DEFAULT_DB):
    connection = connect(db)
    try:
        query = 'SELECT p.* FROM publications p'
        params = ()
        if topic:
            query += ' JOIN topics t ON p.pmid=t.pmid WHERE t.topic=?'
            params = (topic,)
        return [dict(row) for row in connection.execute(query + ' ORDER BY substr(p.publication_date,1,4) DESC, p.publication_date DESC, p.pmid DESC', params)]
    finally:
        connection.close()
