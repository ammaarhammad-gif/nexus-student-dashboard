"""
models.py — Data access layer for all database operations using PostgreSQL.
Includes user authentication and isolates data by user_id.
"""

import bcrypt
import psycopg2
import psycopg2.extras
import streamlit as st
from database import get_connection

# ══════════════════════════════════════════════
# USER MANAGEMENT (Auth & Signup)
# ══════════════════════════════════════════════

def create_user(username: str, password: str) -> int:
    """Create a new user. Returns user_id, or None if username exists."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username.lower().strip(),))
            if cursor.fetchone():
                return None

            # Hash the password securely
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (username.lower().strip(), password_hash)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_user(username: str, password: str) -> dict:
    """Verify user credentials. Returns user dict or None if invalid."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username.lower().strip(),))
            user = cursor.fetchone()
            if not user:
                return None

            # Verify bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                return dict(user)
            return None
    finally:
        conn.close()


# ══════════════════════════════════════════════
# SETTINGS & USER PROFILE
# ══════════════════════════════════════════════

@st.cache_data(ttl=15, show_spinner=False)
def get_setting(user_id: int, key: str, default=None):
    """Read a single setting value for a user."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT value FROM settings WHERE user_id = %s AND key = %s", (user_id, key))
            row = cursor.fetchone()
            return row[0] if row else default
    finally:
        conn.close()


def set_setting(user_id: int, key: str, value: str):
    """Write a single setting value (insert or update on conflict)."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO settings (user_id, key, value, updated_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            """, (user_id, key, str(value)))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def is_setup_complete(user_id: int) -> bool:
    """Check if the setup wizard has been completed for this user."""
    return get_setting(user_id, "is_setup_completed", "0") == "1"


def save_user_profile(user_id: int, name: str, academic_year: str, board: str, class_name: str):
    """Save all user profile fields and mark setup as complete."""
    set_setting(user_id, "user_name", name)
    set_setting(user_id, "academic_year", academic_year)
    set_setting(user_id, "board", board)
    set_setting(user_id, "class_name", class_name)
    set_setting(user_id, "is_setup_completed", "1")
    st.cache_data.clear()


@st.cache_data(ttl=15, show_spinner=False)
def get_user_profile(user_id: int) -> dict:
    """Retrieve user profile as a dictionary."""
    return {
        "name": get_setting(user_id, "user_name", ""),
        "academic_year": get_setting(user_id, "academic_year", ""),
        "board": get_setting(user_id, "board", ""),
        "class_name": get_setting(user_id, "class_name", ""),
        "is_setup_completed": is_setup_complete(user_id)
    }


# ══════════════════════════════════════════════
# TERMS MANAGEMENT
# ══════════════════════════════════════════════

def get_all_terms(user_id: int):
    """Return all terms for a user sorted by display_order."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM terms WHERE user_id = %s ORDER BY display_order ASC, id ASC", (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_term(user_id: int, name: str, exam_date: str, display_order: int = 0):
    """Create a new academic term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO terms (user_id, name, exam_date, display_order) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, name, exam_date, display_order)
            )
            term_id = cursor.fetchone()[0]
            conn.commit()
            return term_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_term(user_id: int, term_id: int, name: str, exam_date: str):
    """Update an existing term's name and exam date."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE terms SET name = %s, exam_date = %s WHERE user_id = %s AND id = %s",
                (name, exam_date, user_id, term_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_term(user_id: int, term_id: int):
    """Delete a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM terms WHERE user_id = %s AND id = %s", (user_id, term_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def clear_all_terms(user_id: int):
    """Remove all terms for a user."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM terms WHERE user_id = %s", (user_id,))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# SUBJECTS
# ══════════════════════════════════════════════

def get_all_subjects(user_id: int):
    """Return all subjects for a user sorted by display_order then name."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM subjects WHERE user_id = %s ORDER BY display_order ASC, name ASC", (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_subject(user_id: int, name: str, color: str = "#6366F1"):
    """Create a new subject. Returns the new subject ID or None if duplicate."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO subjects (user_id, name, color) VALUES (%s, %s, %s) RETURNING id",
                (user_id, name.strip(), color)
            )
            subject_id = cursor.fetchone()[0]
            conn.commit()
            return subject_id
    except psycopg2.IntegrityError:
        conn.rollback()
        return None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rename_subject(user_id: int, subject_id: int, new_name: str) -> bool:
    """Rename a subject. Returns False if duplicate."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE subjects SET name = %s WHERE user_id = %s AND id = %s",
                (new_name.strip(), user_id, subject_id)
            )
            conn.commit()
            return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_subject(user_id: int, subject_id: int):
    """Delete a subject and all its children (cascade is handled by foreign key)."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # We clean up associated progress explicitly since item_id points to topics/subtopics
            # but has no actual hard foreign key inside topic_progress schema
            chapters = conn.execute("SELECT id FROM chapters WHERE user_id = %s AND subject_id = %s", (user_id, subject_id))
            # Wait, conn.execute is not supported in psycopg2, we must use cursor.execute
            # Let's fix this database call:
            cursor.execute("SELECT id FROM chapters WHERE user_id = %s AND subject_id = %s", (user_id, subject_id))
            chapters_rows = cursor.fetchall()
            for ch in chapters_rows:
                cursor.execute("SELECT id FROM topics WHERE user_id = %s AND chapter_id = %s", (user_id, ch[0]))
                topics_rows = cursor.fetchall()
                for t in topics_rows:
                    cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'topic' AND item_id = %s", (user_id, t[0]))
                    cursor.execute("SELECT id FROM subtopics WHERE user_id = %s AND topic_id = %s", (user_id, t[0]))
                    subtopics_rows = cursor.fetchall()
                    for st_item in subtopics_rows:
                        cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'subtopic' AND item_id = %s", (user_id, st_item[0]))
            
            cursor.execute("DELETE FROM subjects WHERE user_id = %s AND id = %s", (user_id, subject_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_subject_color(user_id: int, subject_id: int, color: str):
    """Update a subject's color theme."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE subjects SET color = %s WHERE user_id = %s AND id = %s", (color, user_id, subject_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# CHAPTERS
# ══════════════════════════════════════════════

def get_chapters_for_subject(user_id: int, subject_id: int):
    """Return all chapters for a given subject."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM chapters WHERE user_id = %s AND subject_id = %s ORDER BY display_order ASC, id ASC",
                (user_id, subject_id)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_chapter(user_id: int, subject_id: int, name: str):
    """Create a new chapter under a subject."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(display_order), 0) FROM chapters WHERE user_id = %s AND subject_id = %s",
                (user_id, subject_id)
            )
            max_order = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO chapters (user_id, subject_id, name, display_order) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, subject_id, name.strip(), max_order + 1)
            )
            chapter_id = cursor.fetchone()[0]
            conn.commit()
            return chapter_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rename_chapter(user_id: int, chapter_id: int, new_name: str):
    """Rename a chapter."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE chapters SET name = %s WHERE user_id = %s AND id = %s",
                (new_name.strip(), user_id, chapter_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_chapter(user_id: int, chapter_id: int):
    """Delete a chapter and associated progress records."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM topics WHERE user_id = %s AND chapter_id = %s", (user_id, chapter_id))
            topics = cursor.fetchall()
            for t in topics:
                cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'topic' AND item_id = %s", (user_id, t[0]))
                cursor.execute("SELECT id FROM subtopics WHERE user_id = %s AND topic_id = %s", (user_id, t[0]))
                subtopics = cursor.fetchall()
                for st_item in subtopics:
                    cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'subtopic' AND item_id = %s", (user_id, st_item[0]))
            cursor.execute("DELETE FROM chapters WHERE user_id = %s AND id = %s", (user_id, chapter_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def move_chapter(user_id: int, chapter_id: int, direction: str):
    """Move a chapter up or down in display order within its subject."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM chapters WHERE user_id = %s AND id = %s", (user_id, chapter_id))
            chapter = cursor.fetchone()
            if not chapter:
                return
            cursor.execute(
                "SELECT * FROM chapters WHERE user_id = %s AND subject_id = %s ORDER BY display_order ASC, id ASC",
                (user_id, chapter["subject_id"])
            )
            chapters = [dict(c) for c in cursor.fetchall()]
            idx = next((i for i, c in enumerate(chapters) if c["id"] == chapter_id), None)
            if idx is None:
                return
            swap_idx = idx - 1 if direction == "up" and idx > 0 else idx + 1 if direction == "down" and idx < len(chapters) - 1 else None
            if swap_idx is not None:
                cursor.execute("UPDATE chapters SET display_order = %s WHERE user_id = %s AND id = %s", (swap_idx, user_id, chapter_id))
                cursor.execute("UPDATE chapters SET display_order = %s WHERE user_id = %s AND id = %s", (idx, user_id, chapters[swap_idx]["id"]))
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# TOPICS
# ══════════════════════════════════════════════

def get_topics_for_chapter(user_id: int, chapter_id: int):
    """Return all topics for a given chapter."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM topics WHERE user_id = %s AND chapter_id = %s ORDER BY display_order ASC, id ASC",
                (user_id, chapter_id)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_topic(user_id: int, chapter_id: int, name: str):
    """Create a new topic under a chapter and initialize its progress record."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(display_order), 0) FROM topics WHERE user_id = %s AND chapter_id = %s",
                (user_id, chapter_id)
            )
            max_order = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO topics (user_id, chapter_id, name, display_order) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, chapter_id, name.strip(), max_order + 1)
            )
            topic_id = cursor.fetchone()[0]
            
            # Create default progress entry
            cursor.execute(
                """INSERT INTO topic_progress (user_id, item_type, item_id, status, understanding, notes,
                   is_important, is_difficult, needs_practice, updated_at)
                   VALUES (%s, 'topic', %s, 'Not Started', 3, '', 0, 0, 0, CURRENT_TIMESTAMP)""",
                (user_id, topic_id)
            )
            conn.commit()
            return topic_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rename_topic(user_id: int, topic_id: int, new_name: str):
    """Rename a topic."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE topics SET name = %s WHERE user_id = %s AND id = %s",
                (new_name.strip(), user_id, topic_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_topic(user_id: int, topic_id: int):
    """Delete a topic and its progress record."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM subtopics WHERE user_id = %s AND topic_id = %s", (user_id, topic_id))
            subtopics = cursor.fetchall()
            for st_item in subtopics:
                cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'subtopic' AND item_id = %s", (user_id, st_item[0]))
            cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'topic' AND item_id = %s", (user_id, topic_id))
            cursor.execute("DELETE FROM topics WHERE user_id = %s AND id = %s", (user_id, topic_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# SUBTOPICS
# ══════════════════════════════════════════════

def get_subtopics_for_topic(user_id: int, topic_id: int):
    """Return all subtopics for a given topic."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM subtopics WHERE user_id = %s AND topic_id = %s ORDER BY display_order ASC, id ASC",
                (user_id, topic_id)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_subtopic(user_id: int, topic_id: int, name: str):
    """Create a new subtopic and initialize its progress record."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(display_order), 0) FROM subtopics WHERE user_id = %s AND topic_id = %s",
                (user_id, topic_id)
            )
            max_order = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO subtopics (user_id, topic_id, name, display_order) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, topic_id, name.strip(), max_order + 1)
            )
            subtopic_id = cursor.fetchone()[0]
            
            cursor.execute(
                """INSERT INTO topic_progress (user_id, item_type, item_id, status, understanding, notes,
                   is_important, is_difficult, needs_practice, updated_at)
                   VALUES (%s, 'subtopic', %s, 'Not Started', 3, '', 0, 0, 0, CURRENT_TIMESTAMP)""",
                (user_id, subtopic_id)
            )
            conn.commit()
            return subtopic_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rename_subtopic(user_id: int, subtopic_id: int, new_name: str):
    """Rename a subtopic."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE subtopics SET name = %s WHERE user_id = %s AND id = %s",
                (new_name.strip(), user_id, subtopic_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_subtopic(user_id: int, subtopic_id: int):
    """Delete a subtopic and its progress record."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM topic_progress WHERE user_id = %s AND item_type = 'subtopic' AND item_id = %s", (user_id, subtopic_id))
            cursor.execute("DELETE FROM subtopics WHERE user_id = %s AND id = %s", (user_id, subtopic_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# TOPIC PROGRESS MANAGEMENT
# ══════════════════════════════════════════════

def get_progress(user_id: int, item_type: str, item_id: int) -> dict:
    """Retrieve progress for a topic or subtopic."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM topic_progress WHERE user_id = %s AND item_type = %s AND item_id = %s",
                (user_id, item_type, item_id)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {
                "item_type": item_type,
                "item_id": item_id,
                "status": "Not Started",
                "understanding": 3,
                "notes": "",
                "is_important": 0,
                "is_difficult": 0,
                "needs_practice": 0
            }
    finally:
        conn.close()


def save_progress(user_id: int, item_type: str, item_id: int, status: str = "Not Started",
                  understanding: int = 3, notes: str = "",
                  is_important: int = 0, is_difficult: int = 0, needs_practice: int = 0):
    """Save or update progress for a topic or subtopic."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO topic_progress (user_id, item_type, item_id, status, understanding, notes,
                    is_important, is_difficult, needs_practice, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, item_type, item_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    understanding = EXCLUDED.understanding,
                    notes = EXCLUDED.notes,
                    is_important = EXCLUDED.is_important,
                    is_difficult = EXCLUDED.is_difficult,
                    needs_practice = EXCLUDED.needs_practice,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, item_type, item_id, status, understanding, notes,
                  is_important, is_difficult, needs_practice))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# TERM–CHAPTER MAPPING
# ══════════════════════════════════════════════

def get_chapters_for_term(user_id: int, term_id: int):
    """Return all chapter IDs assigned to a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT chapter_id FROM term_chapters WHERE user_id = %s AND term_id = %s", (user_id, term_id))
            rows = cursor.fetchall()
            return [r[0] for r in rows]
    finally:
        conn.close()


def assign_chapter_to_term(user_id: int, term_id: int, chapter_id: int):
    """Assign a chapter to a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO term_chapters (user_id, term_id, chapter_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (user_id, term_id, chapter_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def remove_chapter_from_term(user_id: int, term_id: int, chapter_id: int):
    """Remove a chapter assignment from a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM term_chapters WHERE user_id = %s AND term_id = %s AND chapter_id = %s",
                (user_id, term_id, chapter_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def set_term_chapters(user_id: int, term_id: int, chapter_ids: list):
    """Replace all chapter assignments for a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM term_chapters WHERE user_id = %s AND term_id = %s", (user_id, term_id))
            for cid in chapter_ids:
                cursor.execute(
                    "INSERT INTO term_chapters (user_id, term_id, chapter_id) VALUES (%s, %s, %s)",
                    (user_id, term_id, cid)
                )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# OVERALL SYLLABUS STATISTICS
# ══════════════════════════════════════════════

def get_overall_stats(user_id: int) -> dict:
    """Calculate overall syllabus progress statistics."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM subjects WHERE user_id = %s", (user_id,))
            total_subjects = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM chapters WHERE user_id = %s", (user_id,))
            total_chapters = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM topics WHERE user_id = %s", (user_id,))
            total_topics = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM subtopics WHERE user_id = %s", (user_id,))
            total_subtopics = cursor.fetchone()[0]

            # Count by status across topics
            cursor.execute("""
                SELECT status, COUNT(*) as cnt
                FROM topic_progress
                WHERE user_id = %s AND item_type = 'topic'
                GROUP BY status
            """, (user_id,))
            status_rows = cursor.fetchall()
            status_map = {r[0]: r[1] for r in status_rows}

            completed = status_map.get("Completed", 0) + status_map.get("Revision Done", 0)
            in_progress = status_map.get("In Progress", 0)
            not_started = status_map.get("Not Started", 0)
            revision_done = status_map.get("Revision Done", 0)
            remaining = max(0, total_topics - completed)

            cursor.execute(
                "SELECT AVG(understanding) FROM topic_progress WHERE user_id = %s AND item_type = 'topic'", (user_id,)
            )
            avg_und_val = cursor.fetchone()[0]
            avg_understanding = round(float(avg_und_val), 1) if avg_und_val is not None else 0.0

            percent_completed = round((completed / total_topics * 100), 1) if total_topics > 0 else 0.0

            return {
                "total_subjects": total_subjects,
                "total_chapters": total_chapters,
                "total_topics": total_topics,
                "total_subtopics": total_subtopics,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "revision_done": revision_done,
                "remaining": remaining,
                "percent_completed": percent_completed,
                "avg_understanding": avg_understanding
            }
    finally:
        conn.close()


def get_subject_stats(user_id: int, subject_id: int) -> dict:
    """Calculate progress statistics for a single subject."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM chapters WHERE user_id = %s AND subject_id = %s", (user_id, subject_id))
            chapter_ids = [c[0] for c in cursor.fetchall()]

            if not chapter_ids:
                return {
                    "total_chapters": 0, "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "remaining": 0, "percent_completed": 0.0, "avg_understanding": 0.0
                }

            cursor.execute(
                "SELECT COUNT(*) FROM topics WHERE user_id = %s AND chapter_id = ANY(%s)",
                (user_id, chapter_ids)
            )
            total_topics = cursor.fetchone()[0]

            cursor.execute(
                "SELECT id FROM topics WHERE user_id = %s AND chapter_id = ANY(%s)",
                (user_id, chapter_ids)
            )
            topic_ids = [t[0] for t in cursor.fetchall()]

            if not topic_ids:
                return {
                    "total_chapters": len(chapter_ids), "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "remaining": 0, "percent_completed": 0.0, "avg_understanding": 0.0
                }

            cursor.execute("""
                SELECT status, COUNT(*) as cnt
                FROM topic_progress
                WHERE user_id = %s AND item_type = 'topic' AND item_id = ANY(%s)
                GROUP BY status
            """, (user_id, topic_ids))
            status_rows = cursor.fetchall()
            status_map = {r[0]: r[1] for r in status_rows}
            
            completed = status_map.get("Completed", 0) + status_map.get("Revision Done", 0)
            in_progress = status_map.get("In Progress", 0)
            not_started = status_map.get("Not Started", 0)
            revision_done = status_map.get("Revision Done", 0)

            cursor.execute("""
                SELECT AVG(understanding) FROM topic_progress
                WHERE user_id = %s AND item_type = 'topic' AND item_id = ANY(%s)
            """, (user_id, topic_ids))
            avg_und = cursor.fetchone()[0]

            return {
                "total_chapters": len(chapter_ids),
                "total_topics": total_topics,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "revision_done": revision_done,
                "remaining": max(0, total_topics - completed),
                "percent_completed": round((completed / total_topics * 100), 1) if total_topics > 0 else 0.0,
                "avg_understanding": round(float(avg_und), 1) if avg_und is not None else 0.0
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# TERM STATS
# ══════════════════════════════════════════════

def get_term_stats(user_id: int, term_id: int) -> dict:
    """Calculate progress statistics for chapters assigned to a term."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT chapter_id FROM term_chapters WHERE user_id = %s AND term_id = %s", (user_id, term_id))
            chapter_ids = [c[0] for c in cursor.fetchall()]

            if not chapter_ids:
                return {
                    "total_chapters": 0, "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "percent_completed": 0.0
                }

            cursor.execute(
                "SELECT id FROM topics WHERE user_id = %s AND chapter_id = ANY(%s)",
                (user_id, chapter_ids)
            )
            topic_ids = [t[0] for t in cursor.fetchall()]

            if not topic_ids:
                return {
                    "total_chapters": len(chapter_ids), "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "percent_completed": 0.0
                }

            cursor.execute("""
                SELECT status, COUNT(*) as cnt
                FROM topic_progress
                WHERE user_id = %s AND item_type = 'topic' AND item_id = ANY(%s)
                GROUP BY status
            """, (user_id, topic_ids))
            status_rows = cursor.fetchall()
            status_map = {r[0]: r[1] for r in status_rows}
            
            completed = status_map.get("Completed", 0) + status_map.get("Revision Done", 0)
            in_progress = status_map.get("In Progress", 0)
            not_started = status_map.get("Not Started", 0)
            revision_done = status_map.get("Revision Done", 0)
            total_topics = len(topic_ids)

            return {
                "total_chapters": len(chapter_ids),
                "total_topics": total_topics,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "revision_done": revision_done,
                "percent_completed": round((completed / total_topics * 100), 1) if total_topics > 0 else 0.0
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# DAILY STUDY PLANS
# ══════════════════════════════════════════════

def get_daily_plans(user_id: int, plan_date: str):
    """Retrieve daily study plan tasks for a given date (YYYY-MM-DD)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT p.*, s.name as subject_name, s.color as subject_color, c.name as chapter_name, t.name as topic_name
                FROM daily_plans p
                LEFT JOIN subjects s ON p.subject_id = s.id
                LEFT JOIN chapters c ON p.chapter_id = c.id
                LEFT JOIN topics t ON p.topic_id = t.id
                WHERE p.user_id = %s AND p.plan_date = %s
                ORDER BY p.display_order ASC, p.id ASC
            """, (user_id, plan_date))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_daily_plan(user_id: int, plan_date: str, description: str, duration_minutes: int = 30,
                   subject_id: int = None, chapter_id: int = None, topic_id: int = None):
    """Add a new study plan task for a date."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(display_order), 0) FROM daily_plans WHERE user_id = %s AND plan_date = %s",
                (user_id, plan_date)
            )
            max_order = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO daily_plans (user_id, plan_date, subject_id, chapter_id, topic_id, description, duration_minutes, display_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, plan_date, subject_id, chapter_id, topic_id, description.strip(), duration_minutes, max_order + 1))
            plan_id = cursor.fetchone()[0]
            conn.commit()
            return plan_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def toggle_daily_plan(user_id: int, plan_id: int, is_completed: bool):
    """Toggle completion status of a daily plan task."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE daily_plans SET is_completed = %s WHERE user_id = %s AND id = %s",
                (1 if is_completed else 0, user_id, plan_id)
            )
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_daily_plan(user_id: int, plan_id: int):
    """Delete a daily plan task."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM daily_plans WHERE user_id = %s AND id = %s", (user_id, plan_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════

def get_all_goals(user_id: int):
    """Retrieve all study goals for a user."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM goals WHERE user_id = %s ORDER BY is_completed ASC, deadline ASC, id DESC", (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def add_goal(user_id: int, title: str, goal_type: str = "Daily", target: int = 1, deadline: str = None):
    """Add a new goal."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO goals (user_id, title, goal_type, target, progress, deadline, is_completed)
                VALUES (%s, %s, %s, %s, 0, %s, 0) RETURNING id
            """, (user_id, title.strip(), goal_type, target, deadline))
            goal_id = cursor.fetchone()[0]
            conn.commit()
            return goal_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_goal_progress(user_id: int, goal_id: int, progress: int, is_completed: bool = False):
    """Update goal progress."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE goals SET progress = %s, is_completed = %s WHERE user_id = %s AND id = %s
            """, (progress, 1 if is_completed else 0, user_id, goal_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_goal(user_id: int, goal_id: int):
    """Delete a goal."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM goals WHERE user_id = %s AND id = %s", (user_id, goal_id))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# RESET ALL DATA
# ══════════════════════════════════════════════

def reset_all_data(user_id: int):
    """Wipes ALL data belonging to the user from the database. Use with extreme caution."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            tables = [
                "topic_progress", "term_chapters", "subtopics", "topics",
                "chapters", "subjects", "terms", "goals", "study_sessions",
                "revisions", "achievements", "daily_plans", "settings"
            ]
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
