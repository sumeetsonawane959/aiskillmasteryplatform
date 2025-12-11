"""
Authentication module for user login and registration.
"""
from .database import Database
from typing import Optional, Tuple


class AuthManager:
    def __init__(self, database: Database):
        self.db = database

    def register(self, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user."""
        if not email or not password:
            return False, "Email and password are required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        success = self.db.create_user(email, password)
        if success:
            return True, "Registration successful"
        else:
            return False, "Email already exists"

    def login(self, email: str, password: str) -> Tuple[Optional[int], str]:
        """Login user and return user_id if successful."""
        if not email or not password:
            return None, "Email and password are required"
        
        user_id = self.db.verify_user(email, password)
        if user_id:
            return user_id, "Login successful"
        else:
            return None, "Invalid email or password"

