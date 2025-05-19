"""Database module for storing commit information."""
import os
import sqlite3
import json
from datetime import datetime
import logging
from ..config.config import DATABASE_PATH

os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def initialize_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commits (
        id TEXT PRIMARY KEY,
        author TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        files_changed TEXT NOT NULL,
        insertions INTEGER NOT NULL,
        deletions INTEGER NOT NULL,
        is_summarized INTEGER DEFAULT 0,
        diff_content TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        summary TEXT NOT NULL,
        commit_count INTEGER NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        is_posted INTEGER DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

def store_commit(commit_id, author, message, timestamp, files_changed, insertions, deletions, diff_content=""):
    """Store a commit in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    files_changed_json = json.dumps(files_changed)
    
    try:
        cursor.execute('''
        INSERT INTO commits (id, author, message, timestamp, files_changed, insertions, deletions, diff_content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (commit_id, author, message, timestamp, files_changed_json, insertions, deletions, diff_content))
        conn.commit()
        logging.info(f"Commit {commit_id[:7]} stored successfully")
    except sqlite3.IntegrityError:
        logging.warning(f"Commit {commit_id[:7]} already exists in the database")
    finally:
        conn.close()

def get_todays_commits():
    """Get all commits made today."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT * FROM commits
    WHERE date(timestamp) = ?
    ORDER BY timestamp ASC
    ''', (today,))
    
    commits = cursor.fetchall()
    result = []
    
    for commit in commits:
        files_changed = json.loads(commit[4])
        
        result.append({
            "id": commit[0],
            "author": commit[1],
            "message": commit[2],
            "timestamp": commit[3],
            "files_changed": files_changed,
            "insertions": commit[5],
            "deletions": commit[6],
            "is_summarized": bool(commit[7]),
            "diff_content": commit[8] if len(commit) > 8 else ""
        })
    
    conn.close()
    return result

def store_summary(date, summary, commit_count):
    """Store a daily summary in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO summaries (date, summary, commit_count, timestamp)
    VALUES (?, ?, ?, ?)
    ''', (date, summary, commit_count, timestamp))
    
    conn.commit()
    summary_id = cursor.lastrowid
    conn.close()
    
    logging.info(f"Summary for {date} stored successfully with ID {summary_id}")
    return summary_id

def mark_summary_as_posted(summary_id):
    """Mark a summary as posted to X."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE summaries
    SET is_posted = 1
    WHERE id = ?
    ''', (summary_id,))
    
    conn.commit()
    conn.close()
    
    logging.info(f"Summary {summary_id} marked as posted")

def mark_commits_as_summarized(commit_ids):
    """Mark commits as summarized."""
    if not commit_ids:
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?"] * len(commit_ids))
    
    cursor.execute(f'''
    UPDATE commits
    SET is_summarized = 1
    WHERE id IN ({placeholders})
    ''', commit_ids)
    
    conn.commit()
    conn.close()
    
    logging.info(f"Marked {len(commit_ids)} commits as summarized")

def commit_exists(commit_id):
    """Check if a commit exists in the database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM commits WHERE id = ?", (commit_id,))
        result = cursor.fetchone() is not None
        
        conn.close()
        return result
    except Exception as e:
        logging.error(f"Failed to check if commit {commit_id} exists: {str(e)}")
        return False
