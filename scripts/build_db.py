#!/usr/bin/env python3
"""Build the SQLite database from the extracted JSON."""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "output" / "saint_quotes.json"
DB_PATH = ROOT / "output" / "saint_quotes.db"


def build() -> None:
    with JSON_PATH.open(encoding="utf-8") as f:
        records = json.load(f)

    # Remove old DB so we get a clean build
    DB_PATH.unlink(missing_ok=True)

    con = sqlite3.connect(str(DB_PATH))
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE saint_quotes (
            id          INTEGER PRIMARY KEY,
            topic       TEXT NOT NULL,
            quote       TEXT NOT NULL,
            author      TEXT NOT NULL,
            page        INTEGER,
            source_title TEXT NOT NULL,
            source_file  TEXT NOT NULL
        );
        CREATE INDEX idx_topic  ON saint_quotes(topic);
        CREATE INDEX idx_author ON saint_quotes(author);
    """)

    cur.executemany(
        "INSERT INTO saint_quotes VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (r["id"], r["topic"], r["quote"], r["author"],
             r["page"], r["source_title"], r["source_file"])
            for r in records
        ],
    )

    con.commit()
    print(f"Created {DB_PATH}")
    print(f"  {cur.execute('SELECT COUNT(*) FROM saint_quotes').fetchone()[0]} quotes")
    print(f"  {cur.execute('SELECT COUNT(DISTINCT topic) FROM saint_quotes').fetchone()[0]} topics")
    print(f"  {cur.execute('SELECT COUNT(DISTINCT author) FROM saint_quotes').fetchone()[0]} authors")
    con.close()


if __name__ == "__main__":
    build()
