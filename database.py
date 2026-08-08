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

def get_connection():
    """Returns a connection to the PostgreSQL database with DictCursor factory."""
    if "postgres" not in st.secrets:
        raise ConnectionError(
            "PostgreSQL credentials not found in Streamlit Secrets! "
            "Please configure `[postgres]` in `.streamlit/secrets.toml` locally, "
            "or in your Streamlit Cloud dashboard settings."
        )
    
    pg_secrets = st.secrets["postgres"]
    
    # Try using connection URL/URI first, otherwise use key-value fields
    if "url" in pg_secrets:
        conn = psycopg2.connect(pg_secrets["url"])
    elif "uri" in pg_secrets:
        conn = psycopg2.connect(pg_secrets["uri"])
    else:
        conn = psycopg2.connect(
            host=pg_secrets.get("host"),
            database=pg_secrets.get("database"),
            user=pg_secrets.get("user"),
            password=pg_secrets.get("password"),
            port=pg_secrets.get("port", 5432)
        )
    
    return conn


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
