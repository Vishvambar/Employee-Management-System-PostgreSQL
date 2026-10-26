"""
Database Connection Manager.
Provides context managers, query executors, and connection pool helpers
for PostgreSQL interactions using psycopg2.
"""

import sys
import psycopg2
from psycopg2 import sql, extras
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from config import get_db_params


@contextmanager
def get_connection():
    """
    Context manager to obtain and cleanly close a PostgreSQL connection.
    Ensures rollback on error and proper resource cleanup.
    """
    conn = None
    try:
        conn = psycopg2.connect(**get_db_params())
        yield conn
    except psycopg2.Error as err:
        if conn:
            conn.rollback()
        print(f"\n[Database Error] Failed database operation: {err}", file=sys.stderr)
        raise
    finally:
        if conn and not conn.closed:
            conn.close()


def test_connection() -> bool:
    """
    Tests connectivity to the PostgreSQL database.
    Returns True if connected successfully, False otherwise.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"[✓] Connected successfully to PostgreSQL!")
                print(f"    Version: {version.split(',')[0]}")
                return True
    except Exception as e:
        print(f"[✗] Connection failed: {e}", file=sys.stderr)
        return False


def execute_read(query: str, params: Optional[Tuple] = None, as_dict: bool = True) -> List[Any]:
    """
    Executes a SELECT query and returns all matching records.
    If as_dict is True, returns a list of dictionaries with column names as keys.
    """
    with get_connection() as conn:
        cursor_factory = extras.RealDictCursor if as_dict else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return [dict(r) for r in rows] if as_dict else rows


def execute_write(query: str, params: Optional[Tuple] = None, returning_id: bool = False) -> Optional[int]:
    """
    Executes an INSERT, UPDATE, or DELETE statement.
    Commits changes automatically and rolls back on failure.
    If returning_id is True (e.g. INSERT ... RETURNING id), returns the generated ID.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result_id = None
            if returning_id:
                res = cur.fetchone()
                if res:
                    result_id = res[0]
            conn.commit()
            return result_id
