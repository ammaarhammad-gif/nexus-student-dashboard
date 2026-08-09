"""
models.py — Data access layer for all database operations using PostgreSQL.
Includes user authentication and isolates data by user_id.
"""

import bcrypt  # type: ignore[import-not-found]
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


@st.cache_data(ttl=60, show_spinner=False)
def get_user_profile(user_id: int) -> dict:
    """Retrieve all user profile fields in a single fast query."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT key, value FROM settings WHERE user_id = %s", (user_id,))
            rows = cursor.fetchall()
            st_dict = dict(rows)
            return {
                "name": st_dict.get("user_name", ""),
                "academic_year": st_dict.get("academic_year", ""),
                "board": st_dict.get("board", ""),
                "class_name": st_dict.get("class_name", ""),
                "theme_mode": st_dict.get("theme_mode", "Light"),
                "is_setup_completed": st_dict.get("is_setup_completed", "0") == "1"
            }
    finally:
        conn.close()


@st.cache_data(ttl=60, show_spinner=False)
def get_user_theme(user_id: int) -> str:
    """Return user's preferred theme mode: 'Light', 'Dark', or 'Default' (defaults to 'Light')."""
    return get_setting(user_id, "theme_mode", "Light")


def set_user_theme(user_id: int, theme: str):
    """Save user's preferred theme mode."""
    set_setting(user_id, "theme_mode", theme)
    st.cache_data.clear()


@st.cache_data(ttl=60, show_spinner=False)
def get_user_wallpaper_config(user_id: int) -> dict:
    """Retrieve user's active wallpaper mode, URL, blur, and opacity configuration."""
    mode = get_setting(user_id, "wallpaper_mode", "none")
    preset_id = get_setting(user_id, "wallpaper_preset_id", "")
    custom_url = get_setting(user_id, "wallpaper_custom_url", "")
    blur = int(get_setting(user_id, "wallpaper_blur", "0") or 0)
    opacity = float(get_setting(user_id, "wallpaper_opacity", "0.82") or 0.82)

    url = None
    if mode == "preset" and preset_id:
        from styles import WALLPAPER_PRESETS
        for wp in WALLPAPER_PRESETS:
            if wp["id"] == preset_id:
                url = wp["url"]
                break
    elif mode == "custom" and custom_url:
        url = custom_url

    return {
        "mode": mode,
        "preset_id": preset_id,
        "custom_url": custom_url,
        "url": url,
        "blur": blur,
        "opacity": opacity
    }


def set_user_wallpaper_config(user_id: int, mode: str, preset_id: str = "", custom_url: str = "", blur: int = 0, opacity: float = 0.82):
    """Save user's wallpaper settings."""
    set_setting(user_id, "wallpaper_mode", mode)
    set_setting(user_id, "wallpaper_preset_id", preset_id)
    if custom_url:
        set_setting(user_id, "wallpaper_custom_url", custom_url)
    set_setting(user_id, "wallpaper_blur", str(blur))
    set_setting(user_id, "wallpaper_opacity", str(opacity))
    st.cache_data.clear()


def clear_user_wallpaper_config(user_id: int):
    """Reset user's wallpaper back to solid theme mode."""
    set_setting(user_id, "wallpaper_mode", "none")
    set_setting(user_id, "wallpaper_preset_id", "")
    set_setting(user_id, "wallpaper_custom_url", "")
    st.cache_data.clear()



# ══════════════════════════════════════════════
# TERMS MANAGEMENT
# ══════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
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


@st.cache_data(ttl=60, show_spinner=False)
def get_active_upcoming_terms(user_id: int):
    """Return all active (not marked as already done) terms for a user."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM terms 
                WHERE user_id = %s AND COALESCE(is_already_done, 0) = 0 
                ORDER BY display_order ASC, id ASC
            """, (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()



def add_term(user_id: int, name: str, exam_date: str, display_order: int = 0, is_already_done: int = 0):
    """Create a new academic term with optional is_already_done status."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO terms (user_id, name, exam_date, display_order, is_already_done) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (user_id, name, exam_date, display_order, 1 if is_already_done else 0)
            )
            term_id = cursor.fetchone()[0]
            conn.commit()
            return term_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_term(user_id: int, term_id: int, name: str, exam_date: str, is_already_done: int = 0):
    """Update an existing term's name, exam date, and is_already_done status."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE terms SET name = %s, exam_date = %s, is_already_done = %s WHERE user_id = %s AND id = %s",
                (name, exam_date, 1 if is_already_done else 0, user_id, term_id)
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

@st.cache_data(ttl=30, show_spinner=False)
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


def get_subject_by_name(user_id: int, name: str):
    """Find a subject by name for a user."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM subjects WHERE user_id = %s AND name = %s", (user_id, name.strip()))
            row = cursor.fetchone()
            return dict(row) if row else None
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
            # Clean up associated progress explicitly since item_id points to topics/subtopics
            # but has no actual hard foreign key inside topic_progress schema
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


def clear_user_syllabus(user_id: int):
    """
    Cleans up all subjects, chapters, topics, subtopics, topic_progress, and term_chapters
    for a user, enabling clean switching to a new class or board curriculum without orphaned subjects.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM topic_progress WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM term_chapters WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM subtopics WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM topics WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM chapters WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM subjects WHERE user_id = %s", (user_id,))
            conn.commit()
            st.cache_data.clear()
            return True
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
# HIGH-SPEED SYLLABUS STATISTICS & BATCH QUERIES
# ══════════════════════════════════════════════

@st.cache_data(ttl=30, show_spinner=False)
def get_overall_stats(user_id: int) -> dict:
    """Calculate overall syllabus progress statistics in a single high-speed database call."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM subjects WHERE user_id = %(uid)s) AS total_subjects,
                    (SELECT COUNT(*) FROM chapters WHERE user_id = %(uid)s) AS total_chapters,
                    (SELECT COUNT(*) FROM topics WHERE user_id = %(uid)s) AS total_topics,
                    (SELECT COUNT(*) FROM subtopics WHERE user_id = %(uid)s) AS total_subtopics,
                    COALESCE(SUM(CASE WHEN tp.status IN ('Completed', 'Revision Done') THEN 1 ELSE 0 END), 0) AS completed,
                    COALESCE(SUM(CASE WHEN tp.status = 'In Progress' THEN 1 ELSE 0 END), 0) AS in_progress,
                    COALESCE(SUM(CASE WHEN tp.status = 'Not Started' THEN 1 ELSE 0 END), 0) AS not_started,
                    COALESCE(SUM(CASE WHEN tp.status = 'Revision Done' THEN 1 ELSE 0 END), 0) AS revision_done,
                    COALESCE(AVG(tp.understanding), 0.0) AS avg_understanding
                FROM topics t
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = t.user_id
                WHERE t.user_id = %(uid)s
            """, {"uid": user_id})
            row = cursor.fetchone()
            if not row or row[0] == 0:
                total_subs = row[0] if row else 0
                return {
                    "total_subjects": total_subs, "total_chapters": 0, "total_topics": 0, "total_subtopics": 0,
                    "completed": 0, "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "remaining": 0, "percent_completed": 0.0, "avg_understanding": 0.0
                }

            tot_subs, tot_chaps, tot_topics, tot_subtops, comp, in_prog, not_start, rev_done, avg_und = row
            actual_not_started = not_start + max(0, tot_topics - (comp + in_prog + not_start))
            pct = round((comp / tot_topics * 100), 1) if tot_topics > 0 else 0.0

            return {
                "total_subjects": tot_subs,
                "total_chapters": tot_chaps,
                "total_topics": tot_topics,
                "total_subtopics": tot_subtops,
                "completed": comp,
                "in_progress": in_prog,
                "not_started": actual_not_started,
                "revision_done": rev_done,
                "remaining": max(0, tot_topics - comp),
                "percent_completed": pct,
                "avg_understanding": round(float(avg_und), 1) if avg_und else 0.0
            }
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_all_subjects_with_stats(user_id: int) -> list:
    """
    High-speed single query to get all subjects for a user along with full aggregated statistics:
    total_chapters, total_topics, completed, in_progress, not_started, revision_done, percent_completed, avg_understanding.
    Replaces 50+ individual queries with 1 single high-speed database roundtrip.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.color,
                    s.display_order,
                    COUNT(DISTINCT c.id) AS total_chapters,
                    COUNT(DISTINCT t.id) AS total_topics,
                    COUNT(DISTINCT CASE WHEN tp.status IN ('Completed', 'Revision Done') THEN t.id END) AS completed,
                    COUNT(DISTINCT CASE WHEN tp.status = 'In Progress' THEN t.id END) AS in_progress,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Not Started' OR tp.status IS NULL THEN t.id END) AS not_started,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Revision Done' THEN t.id END) AS revision_done,
                    COALESCE(AVG(CASE WHEN tp.understanding IS NOT NULL THEN tp.understanding END), 0.0) AS avg_understanding
                FROM subjects s
                LEFT JOIN chapters c ON c.subject_id = s.id AND c.user_id = s.user_id
                LEFT JOIN topics t ON t.chapter_id = c.id AND t.user_id = s.user_id
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = s.user_id
                WHERE s.user_id = %s
                GROUP BY s.id, s.name, s.color, s.display_order
                ORDER BY s.display_order ASC, s.name ASC
            """, (user_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                tot_topics = r["total_topics"]
                comp = r["completed"]
                pct = round((comp / tot_topics * 100), 1) if tot_topics > 0 else 0.0
                avg_und = round(float(r["avg_understanding"]), 1) if r["avg_understanding"] else 0.0
                result.append({
                    "id": r["id"],
                    "name": r["name"],
                    "color": r["color"] or "#6366F1",
                    "display_order": r["display_order"],
                    "total_chapters": r["total_chapters"],
                    "total_topics": tot_topics,
                    "completed": comp,
                    "in_progress": r["in_progress"],
                    "not_started": r["not_started"],
                    "revision_done": r["revision_done"],
                    "remaining": max(0, tot_topics - comp),
                    "percent_completed": pct,
                    "avg_understanding": avg_und
                })
            return result
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_subject_stats(user_id: int, subject_id: int) -> dict:
    """Calculate progress statistics for a single subject using 1 single query."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT c.id) AS total_chapters,
                    COUNT(DISTINCT t.id) AS total_topics,
                    COUNT(DISTINCT CASE WHEN tp.status IN ('Completed', 'Revision Done') THEN t.id END) AS completed,
                    COUNT(DISTINCT CASE WHEN tp.status = 'In Progress' THEN t.id END) AS in_progress,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Not Started' OR tp.status IS NULL THEN t.id END) AS not_started,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Revision Done' THEN t.id END) AS revision_done,
                    COALESCE(AVG(tp.understanding), 0.0) AS avg_understanding
                FROM chapters c
                LEFT JOIN topics t ON t.chapter_id = c.id AND t.user_id = c.user_id
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = c.user_id
                WHERE c.user_id = %s AND c.subject_id = %s
            """, (user_id, subject_id))
            r = cursor.fetchone()
            if not r or r["total_chapters"] == 0:
                return {
                    "total_chapters": 0, "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "remaining": 0, "percent_completed": 0.0, "avg_understanding": 0.0
                }
            tot_topics = r["total_topics"]
            comp = r["completed"]
            pct = round((comp / tot_topics * 100), 1) if tot_topics > 0 else 0.0
            avg_und = round(float(r["avg_understanding"]), 1) if r["avg_understanding"] else 0.0
            return {
                "total_chapters": r["total_chapters"],
                "total_topics": tot_topics,
                "completed": comp,
                "in_progress": r["in_progress"],
                "not_started": r["not_started"],
                "revision_done": r["revision_done"],
                "remaining": max(0, tot_topics - comp),
                "percent_completed": pct,
                "avg_understanding": avg_und
            }
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_subject_hierarchy(user_id: int, subject_id: int) -> list:
    """
    Returns the complete list of chapters with embedded topics, subtopics, and progress
    in a structured tree using a single high-speed database call.
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 1. Fetch all chapters, topics, and their progress in one shot
            cursor.execute("""
                SELECT 
                    c.id AS chapter_id,
                    c.name AS chapter_name,
                    c.display_order AS chapter_order,
                    t.id AS topic_id,
                    t.name AS topic_name,
                    t.display_order AS topic_order,
                    COALESCE(tp.status, 'Not Started') AS status,
                    COALESCE(tp.understanding, 3) AS understanding,
                    COALESCE(tp.notes, '') AS notes,
                    COALESCE(tp.is_important, 0) AS is_important,
                    COALESCE(tp.is_difficult, 0) AS is_difficult,
                    COALESCE(tp.needs_practice, 0) AS needs_practice,
                    tp.updated_at
                FROM chapters c
                LEFT JOIN topics t ON t.chapter_id = c.id AND t.user_id = c.user_id
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = c.user_id
                WHERE c.user_id = %s AND c.subject_id = %s
                ORDER BY c.display_order ASC, c.id ASC, t.display_order ASC, t.id ASC
            """, (user_id, subject_id))
            rows = cursor.fetchall()

            # 2. Fetch all subtopics for these topics in one shot
            cursor.execute("""
                SELECT 
                    st.id AS subtopic_id,
                    st.topic_id,
                    st.name AS subtopic_name,
                    st.display_order,
                    COALESCE(tp.status, 'Not Started') AS status,
                    COALESCE(tp.understanding, 3) AS understanding,
                    COALESCE(tp.notes, '') AS notes,
                    COALESCE(tp.is_important, 0) AS is_important,
                    COALESCE(tp.is_difficult, 0) AS is_difficult,
                    COALESCE(tp.needs_practice, 0) AS needs_practice
                FROM subtopics st
                JOIN topics t ON t.id = st.topic_id AND t.user_id = st.user_id
                JOIN chapters c ON c.id = t.chapter_id AND c.user_id = st.user_id
                LEFT JOIN topic_progress tp ON tp.item_id = st.id AND tp.item_type = 'subtopic' AND tp.user_id = st.user_id
                WHERE st.user_id = %s AND c.subject_id = %s
                ORDER BY st.display_order ASC, st.id ASC
            """, (user_id, subject_id))
            subtopic_rows = cursor.fetchall()
            subtopics_by_topic = {}
            for str_row in subtopic_rows:
                tid = str_row["topic_id"]
                if tid not in subtopics_by_topic:
                    subtopics_by_topic[tid] = []
                subtopics_by_topic[tid].append(dict(str_row))

            chapters_map = {}
            for r in rows:
                cid = r["chapter_id"]
                if cid not in chapters_map:
                    chapters_map[cid] = {
                        "id": cid,
                        "name": r["chapter_name"],
                        "display_order": r["chapter_order"],
                        "topics": [],
                        "total_topics": 0,
                        "completed_topics": 0
                    }

                tid = r["topic_id"]
                if tid is not None:
                    chapters_map[cid]["total_topics"] += 1
                    is_done = (r["status"] in ["Completed", "Revision Done"])
                    if is_done:
                        chapters_map[cid]["completed_topics"] += 1

                    topic_dict = {
                        "id": tid,
                        "chapter_id": cid,
                        "name": r["topic_name"],
                        "display_order": r["topic_order"],
                        "status": r["status"],
                        "understanding": r["understanding"],
                        "notes": r["notes"],
                        "is_important": r["is_important"],
                        "is_difficult": r["is_difficult"],
                        "needs_practice": r["needs_practice"],
                        "updated_at": r["updated_at"],
                        "subtopics": subtopics_by_topic.get(tid, [])
                    }
                    chapters_map[cid]["topics"].append(topic_dict)

            return list(chapters_map.values())
    finally:
        conn.close()


def bulk_create_syllabus(user_id: int, syllabus_list: list) -> bool:
    """
    High-speed transactional bulk syllabus preloader using execute_values batching.
    Creates all subjects, chapters, topics, and initial topic_progress rows
    in a single database transaction in seconds.
    """
    if not syllabus_list:
        return False
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for s_idx, sub_data in enumerate(syllabus_list):
                sub_name = sub_data["name"].strip()
                sub_color = sub_data.get("color", "#6366F1")
                cursor.execute("""
                    INSERT INTO subjects (user_id, name, color, display_order)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(user_id, name) DO UPDATE SET color = EXCLUDED.color
                    RETURNING id
                """, (user_id, sub_name, sub_color, s_idx + 1))
                sub_id = cursor.fetchone()[0]

                # Fetch existing chapters for this subject
                cursor.execute("SELECT id, name FROM chapters WHERE user_id = %s AND subject_id = %s", (user_id, sub_id))
                existing_chap_map = {r[1]: r[0] for r in cursor.fetchall()}

                chaps_data = sub_data.get("chapters", [])
                if not chaps_data:
                    continue

                chap_tuples = [
                    (user_id, sub_id, ch["name"].strip(), c_idx + 1)
                    for c_idx, ch in enumerate(chaps_data)
                    if ch["name"].strip() not in existing_chap_map
                ]
                if chap_tuples:
                    inserted_chaps = psycopg2.extras.execute_values(
                        cursor,
                        "INSERT INTO chapters (user_id, subject_id, name, display_order) VALUES %s RETURNING id, name",
                        chap_tuples,
                        fetch=True
                    )
                    for r in inserted_chaps:
                        existing_chap_map[r[1]] = r[0]

                # Collect and batch insert all topics across all chapters for this subject
                all_topic_tuples = []
                for ch in chaps_data:
                    chap_name = ch["name"].strip()
                    chap_id = existing_chap_map.get(chap_name)
                    if chap_id:
                        for t_idx, t_name in enumerate(ch.get("topics", [])):
                            if t_name.strip():
                                all_topic_tuples.append((user_id, chap_id, t_name.strip(), t_idx + 1))

                if all_topic_tuples:
                    inserted_topics = psycopg2.extras.execute_values(
                        cursor,
                        "INSERT INTO topics (user_id, chapter_id, name, display_order) VALUES %s RETURNING id",
                        all_topic_tuples,
                        fetch=True
                    )
                    new_topic_ids = [r[0] for r in inserted_topics]

                    if new_topic_ids:
                        prog_tuples = [(user_id, 'topic', tid, 'Not Started', 3, '', 0, 0, 0) for tid in new_topic_ids]
                        psycopg2.extras.execute_values(
                            cursor,
                            """INSERT INTO topic_progress (user_id, item_type, item_id, status, understanding, notes, is_important, is_difficult, needs_practice, updated_at)
                               VALUES %s ON CONFLICT (user_id, item_type, item_id) DO NOTHING""",
                            prog_tuples,
                            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                        )

            conn.commit()
            st.cache_data.clear()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()




# ══════════════════════════════════════════════
# TERM STATS
# ══════════════════════════════════════════════

def get_term_stats(user_id: int, term_id: int) -> dict:
    """Calculate progress statistics for chapters assigned to a term in 1 single query."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT tc.chapter_id) AS total_chapters,
                    COUNT(DISTINCT t.id) AS total_topics,
                    COUNT(DISTINCT CASE WHEN tp.status IN ('Completed', 'Revision Done') THEN t.id END) AS completed,
                    COUNT(DISTINCT CASE WHEN tp.status = 'In Progress' THEN t.id END) AS in_progress,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Not Started' OR tp.status IS NULL THEN t.id END) AS not_started,
                    COUNT(DISTINCT CASE WHEN tp.status = 'Revision Done' THEN t.id END) AS revision_done
                FROM term_chapters tc
                LEFT JOIN topics t ON t.chapter_id = tc.chapter_id AND t.user_id = tc.user_id
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = tc.user_id
                WHERE tc.user_id = %s AND tc.term_id = %s
            """, (user_id, term_id))
            r = cursor.fetchone()
            if not r or r["total_chapters"] == 0:
                return {
                    "total_chapters": 0, "total_topics": 0, "completed": 0,
                    "in_progress": 0, "not_started": 0, "revision_done": 0,
                    "percent_completed": 0.0
                }
            tot_topics = r["total_topics"]
            comp = r["completed"]
            pct = round((comp / tot_topics * 100), 1) if tot_topics > 0 else 0.0
            return {
                "total_chapters": r["total_chapters"],
                "total_topics": tot_topics,
                "completed": comp,
                "in_progress": r["in_progress"],
                "not_started": r["not_started"],
                "revision_done": r["revision_done"],
                "percent_completed": pct
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# DAILY STUDY PLANS
# ══════════════════════════════════════════════

@st.cache_data(ttl=30, show_spinner=False)
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
            st.cache_data.clear()
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
            st.cache_data.clear()
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
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════

@st.cache_data(ttl=30, show_spinner=False)
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
            st.cache_data.clear()
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
            st.cache_data.clear()
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
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



# ══════════════════════════════════════════════
# CSV SYLLABUS IMPORT
# ══════════════════════════════════════════════

def import_syllabus_from_csv(user_id: int, rows: list) -> dict:
    """
    Import syllabus from a list of dicts with keys: Subject, Chapter, Topic.
    Skips duplicates. Returns summary counts.
    """
    created_subjects = 0
    created_chapters = 0
    created_topics = 0
    skipped = 0

    # Cache lookups to avoid repeated DB calls
    subject_cache = {}  # name -> id
    chapter_cache = {}  # (subject_id, name) -> id

    for row in rows:
        sub_name = str(row.get("Subject", "")).strip()
        chap_name = str(row.get("Chapter", "")).strip()
        topic_name = str(row.get("Topic", "")).strip()

        if not sub_name or not chap_name or not topic_name:
            skipped += 1
            continue

        # Get or create subject
        if sub_name not in subject_cache:
            existing = get_subject_by_name(user_id, sub_name)
            if existing:
                subject_cache[sub_name] = existing["id"]
            else:
                sid = add_subject(user_id, sub_name)
                if sid:
                    subject_cache[sub_name] = sid
                    created_subjects += 1
                else:
                    # Race condition fallback
                    existing = get_subject_by_name(user_id, sub_name)
                    subject_cache[sub_name] = existing["id"] if existing else None

        subject_id = subject_cache.get(sub_name)
        if not subject_id:
            skipped += 1
            continue

        # Get or create chapter
        chap_key = (subject_id, chap_name)
        if chap_key not in chapter_cache:
            chapters = get_chapters_for_subject(user_id, subject_id)
            found = next((c for c in chapters if c["name"] == chap_name), None)
            if found:
                chapter_cache[chap_key] = found["id"]
            else:
                cid = add_chapter(user_id, subject_id, chap_name)
                chapter_cache[chap_key] = cid
                created_chapters += 1

        chapter_id = chapter_cache.get(chap_key)
        if not chapter_id:
            skipped += 1
            continue

        # Get or create topic
        topics = get_topics_for_chapter(user_id, chapter_id)
        existing_topic = next((t for t in topics if t["name"] == topic_name), None)
        if existing_topic:
            skipped += 1
        else:
            add_topic(user_id, chapter_id, topic_name)
            created_topics += 1

    return {
        "subjects": created_subjects,
        "chapters": created_chapters,
        "topics": created_topics,
        "skipped": skipped
    }


# ══════════════════════════════════════════════
# STUDY SESSIONS
# ══════════════════════════════════════════════

def add_study_session(user_id: int, subject_id: int = None, chapter_id: int = None,
                      topic_id: int = None, duration_minutes: int = 30,
                      session_date: str = None, notes: str = ""):
    """Log a study session."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO study_sessions (user_id, subject_id, chapter_id, topic_id,
                    duration_minutes, session_date, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, subject_id, chapter_id, topic_id, duration_minutes,
                  session_date, notes.strip() if notes else ""))
            session_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            return session_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_study_sessions(user_id: int, limit: int = 20):
    """Retrieve recent study sessions with subject/chapter/topic names."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT ss.*, s.name as subject_name, s.color as subject_color,
                       c.name as chapter_name, t.name as topic_name
                FROM study_sessions ss
                LEFT JOIN subjects s ON ss.subject_id = s.id
                LEFT JOIN chapters c ON ss.chapter_id = c.id
                LEFT JOIN topics t ON ss.topic_id = t.id
                WHERE ss.user_id = %s
                ORDER BY ss.session_date DESC, ss.created_at DESC
                LIMIT %s
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_study_session(user_id: int, session_id: int):
    """Delete a study session."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM study_sessions WHERE user_id = %s AND id = %s",
                           (user_id, session_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_weekly_study_summary(user_id: int):
    """Return total minutes studied per day for the last 7 days."""
    import datetime
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=6)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT session_date, SUM(duration_minutes) as total_mins
                FROM study_sessions
                WHERE user_id = %s AND session_date >= %s AND session_date <= %s
                GROUP BY session_date
                ORDER BY session_date ASC
            """, (user_id, week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()
            data = {r[0]: r[1] for r in rows}

            # Fill in missing days with 0
            result = []
            for i in range(7):
                d = week_ago + datetime.timedelta(days=i)
                ds = d.strftime("%Y-%m-%d")
                result.append({
                    "date": ds,
                    "day_label": d.strftime("%a"),
                    "minutes": data.get(ds, 0)
                })
            return result
    finally:
        conn.close()


# ══════════════════════════════════════════════
# SPACED REVISION REMINDERS
# ══════════════════════════════════════════════

REVISION_INTERVALS = [1, 3, 7, 14, 30]  # days after completion


def schedule_revisions(user_id: int, item_type: str, item_id: int):
    """Schedule spaced revision reminders for a completed topic/subtopic.
    Clears any existing revisions for this item first, then creates new ones.
    """
    import datetime
    today = datetime.date.today()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Remove old revisions for this item
            cursor.execute(
                "DELETE FROM revisions WHERE user_id = %s AND item_type = %s AND item_id = %s",
                (user_id, item_type, item_id)
            )
            for interval in REVISION_INTERVALS:
                due = today + datetime.timedelta(days=interval)
                cursor.execute("""
                    INSERT INTO revisions (user_id, item_type, item_id, due_date, interval_days, is_completed)
                    VALUES (%s, %s, %s, %s, %s, 0)
                """, (user_id, item_type, item_id, due.strftime("%Y-%m-%d"), interval))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_due_revisions(user_id: int, date_str: str):
    """Return revisions that are due on or before the given date and not yet completed.
    Includes the topic/subtopic name for display.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT r.*,
                    CASE
                        WHEN r.item_type = 'topic' THEN t.name
                        WHEN r.item_type = 'subtopic' THEN st.name
                    END as item_name,
                    CASE
                        WHEN r.item_type = 'topic' THEN s.name
                        WHEN r.item_type = 'subtopic' THEN s2.name
                    END as subject_name
                FROM revisions r
                LEFT JOIN topics t ON r.item_type = 'topic' AND r.item_id = t.id
                LEFT JOIN chapters c ON t.chapter_id = c.id
                LEFT JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN subtopics st ON r.item_type = 'subtopic' AND r.item_id = st.id
                LEFT JOIN topics t2 ON st.topic_id = t2.id
                LEFT JOIN chapters c2 ON t2.chapter_id = c2.id
                LEFT JOIN subjects s2 ON c2.subject_id = s2.id
                WHERE r.user_id = %s AND r.due_date <= %s AND r.is_completed = 0
                ORDER BY r.due_date ASC, r.interval_days ASC
            """, (user_id, date_str))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def complete_revision(user_id: int, revision_id: int):
    """Mark a revision reminder as completed."""
    import datetime
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE revisions SET is_completed = 1, completed_at = %s
                WHERE user_id = %s AND id = %s
            """, (datetime.date.today().strftime("%Y-%m-%d"), user_id, revision_id))
            conn.commit()
            st.cache_data.clear()
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
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

