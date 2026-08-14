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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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


@st.cache_resource
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
            display_order INTEGER DEFAULT 0,
            is_already_done INTEGER DEFAULT 0
        );
        """)

        # Migration: ensure is_already_done exists if table was created previously
        cursor.execute("""
        ALTER TABLE terms ADD COLUMN IF NOT EXISTS is_already_done INTEGER DEFAULT 0;
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
            interval_number INTEGER DEFAULT 1,
            is_completed INTEGER DEFAULT 0,
            completed_at VARCHAR(50),
            scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Migration for existing revisions table
        cursor.execute("""
        ALTER TABLE revisions ADD COLUMN IF NOT EXISTS interval_number INTEGER DEFAULT 1;
        ALTER TABLE revisions ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
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

        # ── 15. Mistake Vault ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mistakes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
            topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
            question TEXT NOT NULL,
            your_answer TEXT DEFAULT '',
            correct_answer TEXT DEFAULT '',
            mistake_type VARCHAR(50) DEFAULT 'Conceptual',
            explanation TEXT DEFAULT '',
            prevention_strategy TEXT DEFAULT '',
            is_reviewed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 16. Notes System ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            tags VARCHAR(255) DEFAULT '',
            is_pinned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 17. Formula Vault ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS formulas (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
            title VARCHAR(255) NOT NULL,
            formula_latex TEXT NOT NULL,
            description TEXT DEFAULT '',
            variables_json TEXT DEFAULT '{}',
            is_favorite INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 18. Quizzes & Attempts ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
            chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
            topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
            difficulty VARCHAR(50) DEFAULT 'Mixed',
            questions_json TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            accuracy_pct REAL DEFAULT 0.0,
            time_taken_seconds INTEGER DEFAULT 0,
            weak_topics_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 19. Active Recall Responses ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recall_responses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            prompt_text TEXT NOT NULL,
            user_response TEXT NOT NULL,
            evaluation_feedback TEXT DEFAULT '',
            understanding_score INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── 20. Gamification XP Events ──
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_xp_events (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            action_type VARCHAR(100) NOT NULL,
            xp_amount INTEGER DEFAULT 0,
            description VARCHAR(255) DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ── Migrations for Topic Progress & Users ──
        cursor.execute("""
        ALTER TABLE topic_progress ADD COLUMN IF NOT EXISTS difficulty VARCHAR(20) DEFAULT 'Medium';
        ALTER TABLE topic_progress ADD COLUMN IF NOT EXISTS importance VARCHAR(20) DEFAULT 'Medium';
        ALTER TABLE topic_progress ADD COLUMN IF NOT EXISTS estimated_minutes INTEGER DEFAULT 45;
        ALTER TABLE topic_progress ADD COLUMN IF NOT EXISTS last_studied_at TIMESTAMP;
        ALTER TABLE topic_progress ADD COLUMN IF NOT EXISTS last_revised_at TIMESTAMP;

        ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INTEGER DEFAULT 0;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS nexus_level INTEGER DEFAULT 1;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_date VARCHAR(20);

        -- Formula Vault enhanced metadata
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS units TEXT DEFAULT '';
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS conditions TEXT DEFAULT '';
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS category VARCHAR(100) DEFAULT 'Core Formulas';
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS is_core INTEGER DEFAULT 1;
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS is_custom INTEGER DEFAULT 0;
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS common_mistake TEXT DEFAULT '';
        ALTER TABLE formulas ADD COLUMN IF NOT EXISTS example_application TEXT DEFAULT '';
        """)

        # ── 21. Performance Indexes for Instant Screen Transitions (<100ms) ──
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_prog_user_item ON topic_progress (user_id, item_type, item_id);
        CREATE INDEX IF NOT EXISTS idx_topic_prog_user_status ON topic_progress (user_id, status);
        CREATE INDEX IF NOT EXISTS idx_chapters_user_sub ON chapters (user_id, subject_id, display_order);
        CREATE INDEX IF NOT EXISTS idx_topics_user_chap ON topics (user_id, chapter_id, display_order);
        CREATE INDEX IF NOT EXISTS idx_subtopics_user_top ON subtopics (user_id, topic_id, display_order);
        CREATE INDEX IF NOT EXISTS idx_daily_plans_user_date ON daily_plans (user_id, plan_date);
        CREATE INDEX IF NOT EXISTS idx_terms_user_order ON terms (user_id, display_order);
        CREATE INDEX IF NOT EXISTS idx_term_chaps_user_term ON term_chapters (user_id, term_id);
        CREATE INDEX IF NOT EXISTS idx_revisions_user_due ON revisions (user_id, is_completed, due_date);
        CREATE INDEX IF NOT EXISTS idx_study_sess_user ON study_sessions (user_id, session_date);
        CREATE INDEX IF NOT EXISTS idx_mistakes_user ON mistakes (user_id, mistake_type);
        CREATE INDEX IF NOT EXISTS idx_notes_user_topic ON notes (user_id, topic_id);
        CREATE INDEX IF NOT EXISTS idx_formulas_user ON formulas (user_id, subject_id);
        CREATE INDEX IF NOT EXISTS idx_formulas_user_chap ON formulas (user_id, chapter_id);
        CREATE INDEX IF NOT EXISTS idx_formulas_user_fav ON formulas (user_id, is_favorite);
        CREATE INDEX IF NOT EXISTS idx_quiz_user ON quizzes (user_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user ON quiz_attempts (user_id);
        CREATE INDEX IF NOT EXISTS idx_recall_user ON recall_responses (user_id, topic_id);
        CREATE INDEX IF NOT EXISTS idx_xp_user ON user_xp_events (user_id, created_at);
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
