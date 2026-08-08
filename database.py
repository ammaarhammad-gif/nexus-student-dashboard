"""
database.py — PostgreSQL database connection manager and schema initialization.

The connection credentials are read from Streamlit Secrets (st.secrets["postgres"]).
Supports both a direct connection URL or individual host/user/password parameters.
"""

import psycopg2
import psycopg2.extras
import streamlit as st
import logging

logger = logging.getLogger(__name__)

from psycopg2.pool import ThreadedConnectionPool

@st.cache_resource
def _get_db_pool():
    """Initializes and caches a ThreadedConnectionPool for PostgreSQL."""
    if "postgres" not in st.secrets:
        raise ConnectionError(
            "PostgreSQL credentials not found in Streamlit Secrets! "
            "Please configure `[postgres]` in `.streamlit/secrets.toml` locally, "
            "or in your Streamlit Cloud dashboard settings."
        )
    
    pg_secrets = st.secrets["postgres"]
    url = pg_secrets.get("url") or pg_secrets.get("uri")
    
    if url:
        return ThreadedConnectionPool(1, 15, dsn=url)
    else:
        return ThreadedConnectionPool(
            1, 15,
            host=pg_secrets.get("host"),
            database=pg_secrets.get("database"),
            user=pg_secrets.get("user"),
            password=pg_secrets.get("password"),
            port=int(pg_secrets.get("port", 5432))
        )


class PooledConnectionWrapper:
    """Wraps a pooled psycopg2 connection so calling conn.close() puts it back in the pool."""
    def __init__(self, pool, conn):
        self._pool = pool
        self._conn = conn

    def close(self):
        try:
            if self._conn and self._conn.closed == 0:
                self._pool.putconn(self._conn)
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._conn, name)


def get_connection():
    """Returns a high-speed pooled connection to PostgreSQL."""
    pool = _get_db_pool()
    conn = pool.getconn()
    if conn.closed != 0:
        pool.putconn(conn, close=True)
        conn = pool.getconn()
    return PooledConnectionWrapper(pool, conn)


def init_db():
    """Initializes all required database tables for the Student Dashboard in PostgreSQL."""
    try:
        conn = get_connection()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False
        
    cursor = conn.cursor()

    try:
        # ── 1. Users table (New for multi-user support) ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 2. Settings table ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            key VARCHAR(100) NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, key)
        );
        """)

        # ── 3. Academic Terms / Major Exams ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            exam_date VARCHAR(50),
            display_order INTEGER DEFAULT 0
        );
        """)

        # ── 4. Subjects ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            color VARCHAR(50) DEFAULT '#6366F1',
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        );
        """)

        # ── 5. Chapters ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 6. Topics ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 7. Subtopics ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 8. Progress tracking for topics and subtopics ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_type VARCHAR(50) NOT NULL CHECK(item_type IN ('topic', 'subtopic')),
            item_id INTEGER NOT NULL,
            status VARCHAR(50) DEFAULT 'Not Started' CHECK(status IN ('Not Started', 'In Progress', 'Completed', 'Revision Done')),
            understanding INTEGER DEFAULT 3 CHECK(understanding BETWEEN 1 AND 5),
            notes TEXT DEFAULT '',
            is_important INTEGER DEFAULT 0,
            is_difficult INTEGER DEFAULT 0,
            needs_practice INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_type, item_id)
        );
        """)

        # ── 9. Term to Chapter Mappings ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS term_chapters (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            term_id INTEGER NOT NULL REFERENCES terms(id) ON DELETE CASCADE,
            chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
            UNIQUE(user_id, term_id, chapter_id)
        );
        """)

        # ── 10. Goals ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            goal_type VARCHAR(50) DEFAULT 'Daily',
            target INTEGER DEFAULT 1,
            progress INTEGER DEFAULT 0,
            deadline VARCHAR(50),
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 11. Study Sessions ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            duration_minutes INTEGER DEFAULT 0,
            session_date VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 12. Revisions ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS revisions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_type VARCHAR(50) DEFAULT 'topic',
            item_id INTEGER NOT NULL,
            due_date VARCHAR(50) NOT NULL,
            interval_days INTEGER DEFAULT 1,
            is_completed INTEGER DEFAULT 0,
            completed_at VARCHAR(50)
        );
        """)

        # ── 13. Achievements ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            code VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            icon VARCHAR(50),
            unlocked_at VARCHAR(50),
            UNIQUE(user_id, code)
        );
        """)

        # ── 14. Daily Study Plans ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_plans (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_date VARCHAR(50) NOT NULL,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            description VARCHAR(255) NOT NULL,
            duration_minutes INTEGER DEFAULT 30,
            display_order INTEGER DEFAULT 0,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Database schema initialization failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
