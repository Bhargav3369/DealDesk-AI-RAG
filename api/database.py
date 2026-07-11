import sqlite3
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_db_path():
    # Store locally in /data directory, or /tmp if running serverless on Vercel
    if os.environ.get("VERCEL"):
        return "/tmp/analytics.db"
    
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    return str(data_dir / "analytics.db")

def init_db():
    path = get_db_path()
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                vendor TEXT,
                mode TEXT,
                confidence TEXT,
                answer TEXT,
                feedback INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def log_chat(query, vendor, mode, confidence, answer):
    init_db()
    path = get_db_path()
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_logs (query, vendor, mode, confidence, answer)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, str(vendor), str(mode), str(confidence), str(answer)))
        conn.commit()
        return cursor.lastrowid

def update_feedback(log_id, feedback_value):
    path = get_db_path()
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE chat_logs SET feedback = ? WHERE id = ?
        ''', (feedback_value, log_id))
        conn.commit()
