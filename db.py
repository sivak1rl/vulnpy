import sqlite3
import os
import config


def get_db():
    """Get a database connection with row factory."""
    db = sqlite3.connect(config.DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize the database from schema and seed data."""
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")

    with open(schema_path) as f:
        db.executescript(f.read())
    with open(seed_path) as f:
        db.executescript(f.read())

    db.close()


def query_db(query, args=(), one=False):
    """Execute a query and return results as dicts."""
    db = get_db()
    cur = db.execute(query, args)
    results = cur.fetchall()
    db.close()
    return (results[0] if results else None) if one else results


def execute_db(query, args=()):
    """Execute a write query (INSERT, UPDATE, DELETE)."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    lastrowid = cur.lastrowid
    db.close()
    return lastrowid
