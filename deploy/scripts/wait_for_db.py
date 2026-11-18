#!/usr/bin/env python3
"""
Pre-flight database connectivity check.
Polls the configured database until it becomes available or until timeout.
"""
import os
import sys
import time
from app.config import build_database_uri
from sqlalchemy import create_engine, text


def wait_for_database(timeout_seconds: int = 60, interval: int = 2):
    uri, is_mysql = build_database_uri()
    print(f"Checking database connection ({'MySQL' if is_mysql else 'SQLite/Other'})...")

    # In local SQLite mode, no waiting is required
    if not is_mysql:
        print("Using SQLite fallback; database is immediately ready.")
        return True

    engine = create_engine(uri, pool_pre_ping=True)
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection successfully established!")
            return True
        except Exception as e:
            remaining = int(deadline - time.time())
            print(f"Waiting for database... ({remaining}s remaining) - {e}")
            time.sleep(interval)

    print(f"Error: Timed out after {timeout_seconds} seconds waiting for database.", file=sys.stderr)
    return False


if __name__ == "__main__":
    timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))
    success = wait_for_database(timeout_seconds=timeout)
    sys.exit(0 if success else 1)
