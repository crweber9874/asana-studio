"""
database.py — SQLite setup for Asana Studio.
Pure sqlite3, no ORM. Clean, readable SQL.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "asana_studio.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS poses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            english_name    TEXT NOT NULL,
            sanskrit_name   TEXT,
            slug            TEXT UNIQUE NOT NULL,
            description     TEXT,
            category        TEXT NOT NULL,
            difficulty      INTEGER NOT NULL DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 5),
            is_bilateral    INTEGER NOT NULL DEFAULT 0,
            default_hold_seconds INTEGER NOT NULL DEFAULT 30,
            parent_pose_id  INTEGER REFERENCES poses(id)
        );

        CREATE TABLE IF NOT EXISTS pose_tags (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            pose_id INTEGER NOT NULL REFERENCES poses(id) ON DELETE CASCADE,
            tag     TEXT NOT NULL,
            UNIQUE(pose_id, tag)
        );

        CREATE TABLE IF NOT EXISTS sequences (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT,
            style       TEXT,
            difficulty  INTEGER DEFAULT 2,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sequence_poses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence_id INTEGER NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
            pose_id     INTEGER NOT NULL REFERENCES poses(id),
            position    INTEGER NOT NULL,
            side        TEXT DEFAULT 'both',
            hold_seconds INTEGER NOT NULL DEFAULT 30
        );

        CREATE TABLE IF NOT EXISTS practices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS practice_poses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            practice_id INTEGER NOT NULL REFERENCES practices(id) ON DELETE CASCADE,
            pose_id     INTEGER NOT NULL REFERENCES poses(id),
            position    INTEGER NOT NULL,
            side        TEXT DEFAULT 'both',
            hold_seconds INTEGER NOT NULL DEFAULT 30
        );

        CREATE INDEX IF NOT EXISTS idx_poses_category ON poses(category);
        CREATE INDEX IF NOT EXISTS idx_poses_difficulty ON poses(difficulty);
        CREATE INDEX IF NOT EXISTS idx_pose_tags_tag ON pose_tags(tag);
        CREATE INDEX IF NOT EXISTS idx_sequence_poses_seq ON sequence_poses(sequence_id);
        CREATE INDEX IF NOT EXISTS idx_practice_poses_prac ON practice_poses(practice_id);
    """)
    conn.commit()
    conn.close()


def db_is_seeded() -> bool:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM poses").fetchone()[0]
    conn.close()
    return count > 0
