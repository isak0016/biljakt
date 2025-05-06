import sqlite3
import smtplib
import hashlib
import os
from datetime import datetime
from email.mime.text import MIMEText
from datetime import datetime


CAR_DB_PATH = "seen_items.db"
USER_DB_PATH = "mail_list.db"

def generate_token(x):
    raw = x.get("subject", "") + x.get("share_url", "")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def save_new_user_if_unseen(email, search_words):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()

    c.execute("SELECT 1 FROM mail_list WHERE email = ?", (email,))
    exists = c.fetchone()

    if not exists:
        c.execute(
            "INSERT INTO mail_list (email, search_words, user_seen_at) VALUES (?, ?, ?)",
            (email, search_words, datetime.now().isoformat())
        )
        conn.commit()

    conn.close()

def auto_service_get_user():
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM mail_list")
    rows = c.fetchall()
    conn.close()
    return rows

def auto_service_get_car():
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM mail_list")
    rows = c.fetchall()

    conn.close()
    return rows


def save_new_token_if_unseen(token, title, link):
    conn = sqlite3.connect(CAR_DB_PATH)
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


def init_car_db():
    conn = sqlite3.connect(CAR_DB_PATH)
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

def init_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS mail_list(
              email TEXT PRIMARY KEY,
              search_words TEXT,
              user_seen_at TEXT)
              """)
    conn.commit()
    conn.close()