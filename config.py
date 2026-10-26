"""
Configuration Module for Employee Management System.
Handles PostgreSQL database connection parameters and environment settings.
"""

import os
import getpass
from typing import Dict, Any

# Database connection settings with intelligent fallbacks
DB_CONFIG: Dict[str, Any] = {
    # If host is empty or 'localhost' with peer auth, psycopg2 connects via unix socket
    "dbname": os.getenv("PGDATABASE", "employee_db"),
    "user": os.getenv("PGUSER", os.getenv("USER", getpass.getuser())),
    "password": os.getenv("PGPASSWORD", ""),
    "host": os.getenv("PGHOST", ""),       # Blank default uses local Unix domain socket
    "port": int(os.getenv("PGPORT", "5432"))
}

# Clean connection dictionary by omitting empty password/host if not set
def get_db_params() -> Dict[str, Any]:
    params = {"dbname": DB_CONFIG["dbname"]}
    if DB_CONFIG["user"]:
        params["user"] = DB_CONFIG["user"]
    if DB_CONFIG["host"]:
        params["host"] = DB_CONFIG["host"]
    if DB_CONFIG["port"]:
        params["port"] = DB_CONFIG["port"]
    if DB_CONFIG["password"]:
        params["password"] = DB_CONFIG["password"]
    return params
