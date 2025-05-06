import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "seen_items.db"

def generate_token(x):
    raw = x.get("subject", "") + x.get("share_url", "")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_new_token_if_unseen(token, title, link):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT 1 FROM seen_items WHERE token = ?", (token,))
    exists = c.fetchone()

    if not exists:
        c.execute(
            "INSERT INTO seen_items (token, title, link, seen_at) VALUES (?, ?, ?, ?)",
            (token, title, link, datetime.now().isoformat())
        )
        conn.commit()

    conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS seen_items(
              token TEXT PRIMARY KEY,
              title TEXT,
              link TEXT,
              seen_at TEXT)
              """)
    conn.commit()
    conn.close()