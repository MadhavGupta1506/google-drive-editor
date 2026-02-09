import sqlite3
from pathlib import Path
from typing import Optional, Dict
from contextlib import contextmanager


class TokenDatabase:
    """SQLite database for storing user tokens"""
    
    def __init__(self, db_path: str = "tokens.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tokens (
                    email TEXT PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on email for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_email ON user_tokens(email)
            """)
    
    def save_tokens(self, email: str, access_token: str, refresh_token: str) -> bool:
        """Save or update user tokens"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_tokens (email, access_token, refresh_token, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(email) DO UPDATE SET
                        access_token = excluded.access_token,
                        refresh_token = excluded.refresh_token,
                        updated_at = CURRENT_TIMESTAMP
                """, (email, access_token, refresh_token))
            return True
        except Exception as e:
            print(f"Error saving tokens: {e}")
            return False
    
    def get_tokens(self, email: str) -> Optional[Dict[str, str]]:
        """Retrieve user tokens"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT access_token, refresh_token
                    FROM user_tokens
                    WHERE email = ?
                """, (email,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "access_token": row["access_token"],
                        "refresh_token": row["refresh_token"]
                    }
                return None
        except Exception as e:
            print(f"Error retrieving tokens: {e}")
            return None
    
    def update_access_token(self, email: str, access_token: str) -> bool:
        """Update only the access token"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_tokens
                    SET access_token = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                """, (access_token, email))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating access token: {e}")
            return False
    
    def delete_tokens(self, email: str) -> bool:
        """Delete user tokens"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_tokens WHERE email = ?", (email,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting tokens: {e}")
            return False
    
    def user_exists(self, email: str) -> bool:
        """Check if user tokens exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM user_tokens WHERE email = ?", (email,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False


# Global database instance
token_db = TokenDatabase()
