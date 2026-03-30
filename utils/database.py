import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bot_database.db"


class UserDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_files_processed INTEGER DEFAULT 0,
                    total_storage_saved INTEGER DEFAULT 0,
                    preferences TEXT DEFAULT '{}'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    input_filename TEXT,
                    output_filename TEXT,
                    file_size_input INTEGER,
                    file_size_output INTEGER,
                    processing_time FLOAT,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    daily_files INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 100,
                    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()

    def get_or_create_user(self, user_id: int, username: str = "", first_name: str = "", last_name: str = "") -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, last_name))
                
                cursor.execute("""
                    INSERT INTO user_stats (user_id)
                    VALUES (?)
                """, (user_id,))
                conn.commit()
                return {"user_id": user_id, "username": username, "first_name": first_name, "total_files_processed": 0}
            
            return {
                "user_id": user[0],
                "username": user[1],
                "first_name": user[2],
                "total_files_processed": user[4]
            }

    def log_processing(self, user_id: int, action: str, input_file: str, output_file: str,
                      input_size: int, output_size: int, processing_time: float, status: str = "success", 
                      error: str = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_history 
                (user_id, action, input_filename, output_filename, file_size_input, 
                 file_size_output, processing_time, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, action, input_file, output_file, input_size, output_size, 
                  processing_time, status, error))
            
            cursor.execute("""
                UPDATE users SET total_files_processed = total_files_processed + 1
                WHERE user_id = ?
            """, (user_id,))
            
            if output_size < input_size:
                saved = input_size - output_size
                cursor.execute("""
                    UPDATE users SET total_storage_saved = total_storage_saved + ?
                    WHERE user_id = ?
                """, (saved, user_id))
            
            conn.commit()

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            cursor.execute("""
                SELECT COUNT(*) FROM processing_history 
                WHERE user_id = ? AND timestamp >= datetime('now', '-7 days')
            """, (user_id,))
            files_this_week = cursor.fetchone()[0]
            
            return {
                "total_files": user[4],
                "storage_saved": user[5],
                "files_this_week": files_this_week,
                "member_since": user[6]
            }

    def get_processing_history(self, user_id: int, limit: int = 10) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT action, input_filename, output_filename, file_size_input, 
                       file_size_output, processing_time, timestamp
                FROM processing_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            return cursor.fetchall()

    def check_rate_limit(self, user_id: int, daily_limit: int = 100) -> tuple[bool, int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT daily_files, last_reset FROM user_stats WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
                conn.commit()
                return True, 0
            
            daily_files, last_reset = result
            last_reset_dt = datetime.fromisoformat(last_reset)
            
            if datetime.now() - last_reset_dt > timedelta(days=1):
                cursor.execute("""
                    UPDATE user_stats SET daily_files = 0, last_reset = ?
                    WHERE user_id = ?
                """, (datetime.now(), user_id))
                conn.commit()
                return True, 0
            
            if daily_files >= daily_limit:
                return False, daily_limit - daily_files
            
            cursor.execute("""
                UPDATE user_stats SET daily_files = daily_files + 1
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            
            return True, daily_files + 1

    def update_user_preference(self, user_id: int, pref_key: str, pref_value: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT preferences FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                prefs = json.loads(result[0]) if result[0] else {}
                prefs[pref_key] = pref_value
                cursor.execute("""
                    UPDATE users SET preferences = ? WHERE user_id = ?
                """, (json.dumps(prefs), user_id))
                conn.commit()


db = UserDatabase()
