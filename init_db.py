"""
Database Initializer.
Executes schema.sql against PostgreSQL to set up tables, views, and indexes.
"""

import os
from db_connection import get_connection, test_connection


def initialize_database():
    """Reads schema.sql and executes all DDL statements."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print("[*] Initializing Database Schema...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    print("[✓] Schema initialized successfully: Tables 'departments', 'roles', 'employees' created!")


if __name__ == "__main__":
    if test_connection():
        initialize_database()
