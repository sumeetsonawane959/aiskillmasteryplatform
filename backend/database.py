"""
Database management for user authentication and session history.
Supports both SQLite and MongoDB.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import hashlib


class Database:
    def __init__(self, db_type: str = "sqlite", mongodb_uri: str = None, db_name: str = None):
        self.db_type = db_type
        if db_type == "sqlite":
            self.db_path = "ai_learning.db"
            self._init_sqlite()
        elif db_type == "mongodb":
            self.mongodb_uri = mongodb_uri or "mongodb://localhost:27017/"
            self.db_name = db_name or "ai_learning_platform"
            self._init_mongodb()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _init_sqlite(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                questions TEXT NOT NULL,
                user_answers TEXT NOT NULL,
                evaluation TEXT NOT NULL,
                score REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
        except ConnectionFailure:
            raise ConnectionError("Failed to connect to MongoDB")

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256 (simple hashing for demo)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, password: str) -> bool:
        """Create a new user."""
        password_hash = self._hash_password(password)
        
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                    (email, password_hash, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                conn.close()
                return False
        else:
            try:
                self.db.users.insert_one({
                    "email": email,
                    "password_hash": password_hash,
                    "created_at": datetime.now().isoformat()
                })
                return True
            except Exception:
                return False

    def verify_user(self, email: str, password: str) -> Optional[int]:
        """Verify user credentials and return user_id if valid."""
        password_hash = self._hash_password(password)
        
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE email = ? AND password_hash = ?",
                (email, password_hash)
            )
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        else:
            user = self.db.users.find_one({
                "email": email,
                "password_hash": password_hash
            })
            return str(user["_id"]) if user else None

    def save_session(self, user_id, skill_name: str, questions: List[Dict], 
                    user_answers: List[str], evaluation: Dict, score: float) -> bool:
        """Save a quiz session with evaluation."""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sessions (user_id, skill_name, questions, user_answers, 
                   evaluation, score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id,
                    skill_name,
                    json.dumps(questions),
                    json.dumps(user_answers),
                    json.dumps(evaluation),
                    score,
                    datetime.now().isoformat()
                )
            )
            conn.commit()
            conn.close()
            return True
        else:
            self.db.sessions.insert_one({
                "user_id": str(user_id),
                "skill_name": skill_name,
                "questions": questions,
                "user_answers": user_answers,
                "evaluation": evaluation,
                "score": score,
                "created_at": datetime.now().isoformat()
            })
            return True

    def get_user_sessions(self, user_id) -> List[Dict]:
        """Get all sessions for a user."""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
            cursor.execute(
                """SELECT id, skill_name, questions, user_answers, evaluation, score, created_at
                   FROM sessions WHERE user_id = ? ORDER BY created_at DESC""",
                (user_id_int,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "id": row[0],
                    "skill_name": row[1],
                    "questions": json.loads(row[2]),
                    "user_answers": json.loads(row[3]),
                    "evaluation": json.loads(row[4]),
                    "score": row[5],
                    "created_at": row[6]
                })
            return sessions
        else:
            sessions = list(self.db.sessions.find(
                {"user_id": str(user_id)},
                {"_id": 0}
            ).sort("created_at", -1))
            return sessions

    def get_latest_session(self, user_id) -> Optional[Dict]:
        """Get the latest session for a user."""
        sessions = self.get_user_sessions(user_id)
        return sessions[0] if sessions else None

