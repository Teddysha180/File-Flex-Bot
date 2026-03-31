import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from utils.config import config

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR))).resolve()
DB_PATH = DATA_DIR / "bot_database.db"


class UserDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                INSERT OR IGNORE INTO admins (user_id, added_by)
                VALUES (?, ?)
            """, (config.MAIN_ADMIN_ID, config.MAIN_ADMIN_ID))
            
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
                "total_files_processed": user[5]
            }

    def is_admin(self, user_id: int) -> bool:
        if user_id == config.MAIN_ADMIN_ID:
            return True
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None

    def add_admin(self, user_id: int, added_by: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO admins (user_id, added_by)
                VALUES (?, ?)
            """, (user_id, added_by))
            conn.commit()

    def remove_admin(self, user_id: int) -> bool:
        if user_id == config.MAIN_ADMIN_ID:
            return False
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    def list_admin_ids(self) -> list[int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM admins ORDER BY created_at ASC")
            return [row[0] for row in cursor.fetchall()]

    def list_admins(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.user_id, u.username, u.first_name, a.added_by, a.created_at
                FROM admins a
                LEFT JOIN users u ON u.user_id = a.user_id
                ORDER BY a.created_at ASC
            """)
            admins = []
            for row in cursor.fetchall():
                admins.append({
                    "user_id": row[0],
                    "username": row[1] or "",
                    "first_name": row[2] or "",
                    "added_by": row[3],
                    "created_at": row[4],
                    "is_main_admin": row[0] == config.MAIN_ADMIN_ID,
                })
            return admins

    def get_all_user_ids(self) -> list[int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users ORDER BY created_at ASC")
            return [row[0] for row in cursor.fetchall()]

    def get_dashboard_stats(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM users
                WHERE datetime(created_at) >= datetime('now', 'start of day')
            """)
            new_users_today = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM users
                WHERE datetime(created_at) >= datetime('now', '-7 days')
            """)
            new_users_week = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM admins")
            total_admins = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM processing_history")
            total_jobs = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM processing_history
                WHERE datetime(timestamp) >= datetime('now', 'start of day')
            """)
            jobs_today = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM processing_history
                WHERE datetime(timestamp) >= datetime('now', '-7 days')
            """)
            jobs_week = cursor.fetchone()[0]

            return {
                "total_users": total_users,
                "new_users_today": new_users_today,
                "new_users_week": new_users_week,
                "total_admins": total_admins,
                "total_jobs": total_jobs,
                "jobs_today": jobs_today,
                "jobs_week": jobs_week,
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
