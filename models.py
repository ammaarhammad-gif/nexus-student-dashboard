"""
models.py — Data access layer for all database operations using PostgreSQL.
Includes user authentication and isolates data by user_id.
"""

import json
import datetime
import random
import bcrypt  # type: ignore[import-not-found]
import psycopg2
import psycopg2.extras
import psycopg2.sql
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
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict:
    """Retrieve basic user credentials record by ID."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT id, username, created_at FROM users WHERE id = %s", (user_id,))
            r = cursor.fetchone()
            return dict(r) if r else {"id": user_id, "username": "Student"}
    finally:
        conn.close()


def get_user_settings(user_id: int) -> dict:
    """Convenience alias for get_user_profile."""
    return get_user_profile(user_id)


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


def has_completed_guide(user_id: int) -> bool:
    """Check if the user has completed or skipped the initial full app guide."""
    return get_setting(user_id, "has_completed_guide", "0") == "1"


def set_completed_guide(user_id: int, completed: bool = True):
    """Mark the initial full app guide as completed or skipped."""
    set_setting(user_id, "has_completed_guide", "1" if completed else "0")
    st.cache_data.clear()


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
    opacity = float(get_setting(user_id, "wallpaper_opacity", "0.30") or 0.30)

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


def set_user_wallpaper_config(user_id: int, mode: str, preset_id: str = "", custom_url: str = "", blur: int = 0, opacity: float = 0.30):
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
    """Return all active (not marked as already done) terms for a user with calculated days_remaining."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM terms 
                WHERE user_id = %s AND COALESCE(is_already_done, 0) = 0 
                ORDER BY display_order ASC, id ASC
            """, (user_id,))
            rows = cursor.fetchall()
            today = datetime.date.today()
            res = []
            for r in rows:
                d = dict(r)
                exam_date_val = d.get("exam_date")
                days_left = 0
                if exam_date_val:
                    if isinstance(exam_date_val, str):
                        try:
                            exam_dt = datetime.datetime.strptime(exam_date_val[:10], "%Y-%m-%d").date()
                            days_left = (exam_dt - today).days
                        except Exception:
                            days_left = 0
                    elif isinstance(exam_date_val, (datetime.date, datetime.datetime)):
                        exam_dt = exam_date_val if isinstance(exam_date_val, datetime.date) else exam_date_val.date()
                        days_left = (exam_dt - today).days
                d["days_remaining"] = max(0, days_left)
                d["days_left"] = max(0, days_left)
                res.append(d)
            return res
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
    """Save or update progress for a topic or subtopic, and automatically schedule spaced revisions."""
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
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    # Automatically schedule adaptive spaced repetition revisions & award XP on completion
    if status in ["Completed", "Revision Done"]:
        try:
            schedule_adaptive_revisions(user_id, item_type, item_id, understanding)
            award_user_xp(user_id, "topic_completed", 30, f"Completed {item_type} #{item_id}")
            update_user_streak(user_id)
        except Exception:
            pass


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
                "completed_topics": comp,
                "in_progress": r["in_progress"],
                "not_started": r["not_started"],
                "revision_done": r["revision_done"],
                "percent_completed": pct,
                "completion_pct": pct
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# DAILY STUDY PLANS
# ══════════════════════════════════════════════

@st.cache_data(ttl=30, show_spinner=False)
def get_daily_plans(user_id: int, plan_date: str = None):
    """Retrieve daily study plan tasks for a given date (YYYY-MM-DD). Defaults to today if not provided."""
    if not plan_date:
        plan_date = datetime.date.today().strftime("%Y-%m-%d")
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


def auto_generate_study_plan(user_id: int, term_id: int = None, days_count: int = 14,
                             topics_per_day: int = 3, start_date: str = None) -> dict:
    """
    Intelligent Auto-Scheduler:
    - Finds all unfinished/in-progress topics (or topics belonging to chapters mapped to a specific term).
    - Sorts topics using Priority Engine (weak understanding, high importance, exam proximity).
    - Distributes topics across upcoming days starting from start_date (default today), balancing subjects.
    - Adds tasks to daily_plans avoiding duplicates.
    - Returns summary dictionary.
    """
    import datetime
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.date.today()
    
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 1. Fetch relevant unfinished topics
            if term_id:
                cursor.execute("""
                    SELECT t.id as topic_id, t.name as topic_name, c.id as chapter_id, c.name as chapter_name,
                           s.id as subject_id, s.name as subject_name,
                           COALESCE(tp.status, 'Not Started') as status,
                           COALESCE(tp.understanding, 3) as understanding,
                           COALESCE(tp.is_important, 0) as is_important,
                           COALESCE(tp.is_difficult, 0) as is_difficult
                    FROM topics t
                    JOIN chapters c ON t.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    JOIN term_chapters tc ON c.id = tc.chapter_id AND tc.term_id = %s
                    LEFT JOIN topic_progress tp ON tp.user_id = %s AND tp.item_type = 'topic' AND tp.item_id = t.id
                    WHERE t.user_id = %s AND COALESCE(tp.status, 'Not Started') != 'Completed'
                """, (term_id, user_id, user_id))
            else:
                cursor.execute("""
                    SELECT t.id as topic_id, t.name as topic_name, c.id as chapter_id, c.name as chapter_name,
                           s.id as subject_id, s.name as subject_name,
                           COALESCE(tp.status, 'Not Started') as status,
                           COALESCE(tp.understanding, 3) as understanding,
                           COALESCE(tp.is_important, 0) as is_important,
                           COALESCE(tp.is_difficult, 0) as is_difficult
                    FROM topics t
                    JOIN chapters c ON t.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    LEFT JOIN topic_progress tp ON tp.user_id = %s AND tp.item_type = 'topic' AND tp.item_id = t.id
                    WHERE t.user_id = %s AND COALESCE(tp.status, 'Not Started') != 'Completed'
                """, (user_id, user_id))
            
            topics = [dict(r) for r in cursor.fetchall()]
            
            if not topics:
                return {"scheduled_count": 0, "days_used": 0, "message": "All topics in this scope are already completed! 🎉"}
            
            # Fetch existing planned topic IDs to avoid duplicate planning
            cursor.execute("""
                SELECT topic_id FROM daily_plans 
                WHERE user_id = %s AND topic_id IS NOT NULL AND plan_date >= %s AND is_completed = 0
            """, (user_id, start.strftime("%Y-%m-%d")))
            already_planned = {r[0] for r in cursor.fetchall()}
            
            # Filter out already planned topics
            unplanned_topics = [t for t in topics if t["topic_id"] not in already_planned]
            if not unplanned_topics:
                return {"scheduled_count": 0, "days_used": 0, "message": "All remaining topics are already scheduled in your planner!"}
            
            # 2. Sort by intelligent priority (low understanding first, high importance first, difficult first)
            def topic_sort_key(t):
                u_score = 5 - t["understanding"]
                imp = t["is_important"] * 10
                diff = t["is_difficult"] * 5
                return -(u_score * 10 + imp + diff)
            
            unplanned_topics.sort(key=topic_sort_key)
            
            # 3. Distribute across days (interleaving subjects for balanced cognitive load)
            by_subject = {}
            for t in unplanned_topics:
                by_subject.setdefault(t["subject_name"], []).append(t)
            
            interleaved = []
            while any(by_subject.values()):
                for sub_name in list(by_subject.keys()):
                    if by_subject[sub_name]:
                        interleaved.append(by_subject[sub_name].pop(0))
            
            scheduled_count = 0
            curr_day_offset = 0
            day_topic_count = 0
            
            for t in interleaved:
                target_date = start + datetime.timedelta(days=curr_day_offset)
                date_str = target_date.strftime("%Y-%m-%d")
                
                cursor.execute(
                    "SELECT COALESCE(MAX(display_order), 0) FROM daily_plans WHERE user_id = %s AND plan_date = %s",
                    (user_id, date_str)
                )
                max_order = cursor.fetchone()[0]
                
                desc = f"Study: {t['topic_name']} ({t['subject_name']})"
                cursor.execute("""
                    INSERT INTO daily_plans (user_id, plan_date, subject_id, chapter_id, topic_id, description, duration_minutes, display_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, date_str, t["subject_id"], t["chapter_id"], t["topic_id"], desc, 45, max_order + 1))
                
                scheduled_count += 1
                day_topic_count += 1
                
                if day_topic_count >= topics_per_day:
                    day_topic_count = 0
                    curr_day_offset += 1
                    if curr_day_offset >= days_count:
                        curr_day_offset = days_count - 1
            
            conn.commit()
            st.cache_data.clear()
            return {
                "scheduled_count": scheduled_count,
                "days_used": min(days_count, curr_day_offset + 1),
                "message": f"Successfully scheduled {scheduled_count} topics across {min(days_count, curr_day_offset + 1)} days!"
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_overdue_study_tasks(user_id: int) -> list:
    """Returns all daily study tasks scheduled for dates prior to today that remain uncompleted."""
    import datetime
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT dp.*, s.name as subject_name, s.color as subject_color
                FROM daily_plans dp
                LEFT JOIN subjects s ON dp.subject_id = s.id
                WHERE dp.user_id = %s AND dp.plan_date < %s AND dp.is_completed = 0
                ORDER BY dp.plan_date ASC, dp.display_order ASC
            """, (user_id, today_str))
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def reschedule_overdue_tasks(user_id: int, target_strategy: str = "today_forward", max_per_day: int = 3) -> int:
    """
    Intelligently reschedules all uncompleted past study tasks to today and upcoming days.
    """
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    overdue = get_overdue_study_tasks(user_id)
    if not overdue:
        return 0
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            day_offset = 0
            
            # Count existing uncompleted tasks on today
            cursor.execute("SELECT COUNT(*) FROM daily_plans WHERE user_id = %s AND plan_date = %s AND is_completed = 0", (user_id, today_str))
            count_in_day = cursor.fetchone()[0]
            
            for task in overdue:
                if target_strategy == "today":
                    new_date_str = today_str
                else:
                    if count_in_day >= max_per_day:
                        day_offset += 1
                        count_in_day = 0
                    target_date = today + datetime.timedelta(days=day_offset)
                    new_date_str = target_date.strftime("%Y-%m-%d")
                
                cursor.execute(
                    "SELECT COALESCE(MAX(display_order), 0) FROM daily_plans WHERE user_id = %s AND plan_date = %s",
                    (user_id, new_date_str)
                )
                max_order = cursor.fetchone()[0]
                
                cursor.execute("""
                    UPDATE daily_plans 
                    SET plan_date = %s, display_order = %s
                    WHERE user_id = %s AND id = %s
                """, (new_date_str, max_order + 1, user_id, task["id"]))
                
                count_in_day += 1
                
            conn.commit()
            st.cache_data.clear()
            return len(overdue)
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
                "revisions", "achievements", "daily_plans", "mistakes",
                "notes", "formulas", "quizzes", "quiz_attempts",
                "recall_responses", "user_xp_events", "settings"
            ]
            for table in tables:
                cursor.execute(psycopg2.sql.SQL("DELETE FROM {} WHERE user_id = %s").format(psycopg2.sql.Identifier(table)), (user_id,))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# GLOBAL NEXUS SEARCH ENGINE (Phase 2)
# ══════════════════════════════════════════════

@st.cache_data(ttl=10, show_spinner=False)
def global_nexus_search(user_id: int, query: str) -> dict:
    """
    Performs a fast, case-insensitive global search across 8 student entities:
    Subjects, Chapters, Topics, Notes, Mistakes, Exams/Terms, Daily Tasks, and Goals.
    """
    if not query or len(query.strip()) < 2:
        return {}
    
    term = f"%{query.strip().lower()}%"
    conn = get_connection()
    results = {
        "topics": [],
        "chapters": [],
        "subjects": [],
        "notes": [],
        "mistakes": [],
        "exams": [],
        "tasks": [],
        "goals": []
    }
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 1. Search Topics
            cursor.execute("""
                SELECT t.id, t.name as topic_name, c.name as chapter_name, s.name as subject_name,
                       COALESCE(tp.status, 'Not Started') as status,
                       COALESCE(tp.understanding, 3) as understanding
                FROM topics t
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN topic_progress tp ON tp.user_id = %s AND tp.item_type = 'topic' AND tp.item_id = t.id
                WHERE t.user_id = %s AND LOWER(t.name) LIKE %s
                ORDER BY s.name, c.name, t.name
                LIMIT 10
            """, (user_id, user_id, term))
            for row in cursor.fetchall():
                results["topics"].append(dict(row))

            # 2. Search Chapters
            cursor.execute("""
                SELECT c.id, c.name as chapter_name, s.name as subject_name
                FROM chapters c
                JOIN subjects s ON c.subject_id = s.id
                WHERE c.user_id = %s AND LOWER(c.name) LIKE %s
                ORDER BY s.name, c.name
                LIMIT 10
            """, (user_id, term))
            for row in cursor.fetchall():
                results["chapters"].append(dict(row))

            # 3. Search Subjects
            cursor.execute("""
                SELECT id, name as subject_name, color
                FROM subjects
                WHERE user_id = %s AND LOWER(name) LIKE %s
                ORDER BY name
                LIMIT 5
            """, (user_id, term))
            for row in cursor.fetchall():
                results["subjects"].append(dict(row))

            # 4. Search Notes
            cursor.execute("""
                SELECT n.id, n.title, n.tags, t.name as topic_name, s.name as subject_name
                FROM notes n
                LEFT JOIN topics t ON n.topic_id = t.id
                LEFT JOIN subjects s ON n.subject_id = s.id
                WHERE n.user_id = %s AND (LOWER(n.title) LIKE %s OR LOWER(n.content) LIKE %s OR LOWER(n.tags) LIKE %s)
                ORDER BY n.updated_at DESC
                LIMIT 8
            """, (user_id, term, term, term))
            for row in cursor.fetchall():
                results["notes"].append(dict(row))

            # 5. Search Mistakes
            cursor.execute("""
                SELECT m.id, m.question, m.mistake_type, m.explanation, s.name as subject_name
                FROM mistakes m
                LEFT JOIN subjects s ON m.subject_id = s.id
                WHERE m.user_id = %s AND (LOWER(m.question) LIKE %s OR LOWER(m.explanation) LIKE %s OR LOWER(m.mistake_type) LIKE %s)
                ORDER BY m.created_at DESC
                LIMIT 8
            """, (user_id, term, term, term))
            for row in cursor.fetchall():
                results["mistakes"].append(dict(row))

            # 6. Search Exams / Terms
            cursor.execute("""
                SELECT id, name as exam_name, exam_date, is_already_done
                FROM terms
                WHERE user_id = %s AND LOWER(name) LIKE %s
                ORDER BY exam_date ASC
                LIMIT 5
            """, (user_id, term))
            for row in cursor.fetchall():
                results["exams"].append(dict(row))

            # 7. Search Daily Tasks
            cursor.execute("""
                SELECT dp.id, dp.description, dp.plan_date, dp.is_completed, s.name as subject_name
                FROM daily_plans dp
                LEFT JOIN subjects s ON dp.subject_id = s.id
                WHERE dp.user_id = %s AND LOWER(dp.description) LIKE %s
                ORDER BY dp.plan_date DESC
                LIMIT 8
            """, (user_id, term))
            for row in cursor.fetchall():
                results["tasks"].append(dict(row))

            # 8. Search Goals
            cursor.execute("""
                SELECT id, title, goal_type, target, progress, is_completed
                FROM goals
                WHERE user_id = %s AND LOWER(title) LIKE %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (user_id, term))
            for row in cursor.fetchall():
                results["goals"].append(dict(row))

            return results
    finally:
        conn.close()


# ══════════════════════════════════════════════
# SMART PRIORITY ENGINE (Phase 3)
# ══════════════════════════════════════════════

def get_top_nexus_priorities(user_id: int, limit: int = 8) -> list:
    """
    Calculates dynamic priority score (0-100) for all unfinished or weak topics.
    Considers: Exam proximity (days left), Understanding rating (1-5),
    Topic completion status, Overdue revisions, and Topic importance/difficulty.
    Returns categorized items: 🔴 Critical (>=70), 🟠 High (50-69), 🟡 Medium (30-49), 🟢 Low (<30).
    """
    import datetime
    today = datetime.date.today()
    
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Fetch active upcoming exams and their chapter mappings
            cursor.execute("""
                SELECT t.id as term_id, t.name as term_name, t.exam_date, tc.chapter_id
                FROM terms t
                JOIN term_chapters tc ON t.id = tc.term_id
                WHERE t.user_id = %s AND t.is_already_done = 0 AND t.exam_date IS NOT NULL AND t.exam_date != ''
            """, (user_id,))
            term_rows = cursor.fetchall()
            
            # Map chapter_id -> minimum days until exam
            chapter_exam_proximity = {}
            for r in term_rows:
                try:
                    ex_date = datetime.datetime.strptime(r["exam_date"], "%Y-%m-%d").date()
                    days_left = (ex_date - today).days
                    if days_left >= 0:
                        chap_id = r["chapter_id"]
                        if chap_id not in chapter_exam_proximity or days_left < chapter_exam_proximity[chap_id]["days"]:
                            chapter_exam_proximity[chap_id] = {
                                "days": days_left,
                                "term_name": r["term_name"],
                                "date": r["exam_date"]
                            }
                except Exception:
                    pass

            # Fetch all topics with their status, understanding, and overdue revisions
            cursor.execute("""
                SELECT t.id as topic_id, t.name as topic_name, c.id as chapter_id, c.name as chapter_name,
                       s.id as subject_id, s.name as subject_name, s.color as subject_color,
                       COALESCE(tp.status, 'Not Started') as status,
                       COALESCE(tp.understanding, 3) as understanding,
                       COALESCE(tp.is_important, 0) as is_important,
                       COALESCE(tp.is_difficult, 0) as is_difficult,
                       COALESCE(tp.needs_practice, 0) as needs_practice,
                       (SELECT COUNT(*) FROM revisions r WHERE r.user_id = %s AND r.item_id = t.id AND r.is_completed = 0 AND r.due_date <= %s) as overdue_revisions
                FROM topics t
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN topic_progress tp ON tp.user_id = %s AND tp.item_type = 'topic' AND tp.item_id = t.id
                WHERE t.user_id = %s
            """, (user_id, today.strftime("%Y-%m-%d"), user_id, user_id))
            
            topic_rows = cursor.fetchall()
            prioritized_list = []
            
            for row in topic_rows:
                topic_id = row["topic_id"]
                chap_id = row["chapter_id"]
                status = row["status"]
                understanding = row["understanding"]
                is_important = row["is_important"]
                is_difficult = row["is_difficult"]
                needs_practice = row["needs_practice"]
                overdue_revs = row["overdue_revisions"]
                
                # Priority Score Algorithm (0 to 100)
                score = 0
                reasons = []
                
                # Factor 1: Topic status
                if status == "Not Started":
                    score += 30
                    reasons.append("Topic not started")
                elif status == "In Progress":
                    score += 20
                    reasons.append("Study in progress")
                elif status == "Completed" and understanding <= 2:
                    score += 15
                    reasons.append("Low understanding")
                
                # Factor 2: Understanding rating (Lower understanding = Higher urgency)
                if understanding == 1:
                    score += 35
                    reasons.append("Critical understanding rating (1/5)")
                elif understanding == 2:
                    score += 25
                    reasons.append("Weak understanding (2/5)")
                elif understanding == 3 and status != "Completed":
                    score += 10
                
                # Factor 3: Exam Proximity
                exam_info = chapter_exam_proximity.get(chap_id)
                if exam_info:
                    days_left = exam_info["days"]
                    if days_left <= 3:
                        score += 45
                        reasons.append(f"Exam in {days_left}d ({exam_info['term_name']})")
                    elif days_left <= 7:
                        score += 35
                        reasons.append(f"Exam in {days_left}d ({exam_info['term_name']})")
                    elif days_left <= 14:
                        score += 25
                        reasons.append(f"Exam in {days_left}d")
                    elif days_left <= 30:
                        score += 15
                        reasons.append(f"Upcoming exam ({days_left}d)")
                
                # Factor 4: Overdue revisions
                if overdue_revs > 0:
                    score += 25
                    reasons.append(f"{overdue_revs} revision(s) overdue")
                
                # Factor 5: Importance & Difficulty flags
                if is_important:
                    score += 15
                    reasons.append("Marked High Importance")
                if is_difficult:
                    score += 12
                    reasons.append("Marked Difficult")
                if needs_practice:
                    score += 10
                    reasons.append("Practice needed")
                
                # Cap score at 100
                score = min(100, score)
                
                # Only include topics that need student attention (score >= 25 or incomplete or low understanding)
                if score >= 25 or status != "Completed" or overdue_revs > 0 or understanding <= 2:
                    # Categorize
                    if score >= 70:
                        tier = "Critical"
                        badge_color = "#EF4444"
                        tier_icon = "🔴"
                    elif score >= 50:
                        tier = "High"
                        badge_color = "#F97316"
                        tier_icon = "🟠"
                    elif score >= 30:
                        tier = "Medium"
                        badge_color = "#EAB308"
                        tier_icon = "🟡"
                    else:
                        tier = "Low"
                        badge_color = "#22C55E"
                        tier_icon = "🟢"
                        
                    prioritized_list.append({
                        "topic_id": topic_id,
                        "topic_name": row["topic_name"],
                        "chapter_id": chap_id,
                        "chapter_name": row["chapter_name"],
                        "subject_id": row["subject_id"],
                        "subject_name": row["subject_name"],
                        "subject_color": row["subject_color"],
                        "status": status,
                        "understanding": understanding,
                        "score": score,
                        "tier": tier,
                        "tier_icon": tier_icon,
                        "badge_color": badge_color,
                        "reasons": reasons[:3],
                        "exam_info": exam_info
                    })
            
            # Sort descending by priority score
            prioritized_list.sort(key=lambda x: x["score"], reverse=True)
            return prioritized_list[:limit]
    finally:
        conn.close()


# ══════════════════════════════════════════════
# ADAPTIVE SPACED REPETITION ENGINE (Phase 5)
# ══════════════════════════════════════════════

def schedule_adaptive_revisions(user_id: int, item_type: str, item_id: int, understanding: int = 3):
    """
    Schedules future revision sessions for a completed topic.
    Adaptive Intervals based on understanding rating (1 to 5):
    - Understanding 1-2 (Weak): Review in 1d, 3d, 7d
    - Understanding 3 (Moderate): Review in 2d, 5d, 10d, 21d
    - Understanding 4-5 (Strong): Review in 3d, 7d, 14d, 30d
    """
    import datetime
    today = datetime.date.today()
    
    if understanding <= 2:
        intervals = [1, 3, 7]
    elif understanding == 3:
        intervals = [2, 5, 10, 21]
    else:
        intervals = [3, 7, 14, 30]
        
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Delete any incomplete old revisions for this item
            cursor.execute("""
                DELETE FROM revisions 
                WHERE user_id = %s AND item_type = %s AND item_id = %s AND is_completed = 0
            """, (user_id, item_type, item_id))
            
            for step, days in enumerate(intervals, 1):
                due = today + datetime.timedelta(days=days)
                cursor.execute("""
                    INSERT INTO revisions (user_id, item_type, item_id, due_date, interval_days, interval_number, is_completed)
                    VALUES (%s, %s, %s, %s, %s, %s, 0)
                """, (user_id, item_type, item_id, due.strftime("%Y-%m-%d"), days, step))
                
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=15, show_spinner=False)
def get_revision_queue(user_id: int) -> dict:
    """
    Returns the student's revision queue categorized into:
    - Overdue (due < today)
    - Due Today (due == today)
    - Due This Week (today < due <= today + 7d)
    - Upcoming (due > today + 7d)
    - Recent Completed
    """
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    week_str = (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    conn = get_connection()
    queue = {
        "overdue": [],
        "due_today": [],
        "due_this_week": [],
        "upcoming": [],
        "recent_completed": []
    }
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT r.id, r.item_type, r.item_id, r.due_date, r.interval_days, r.interval_number,
                       r.is_completed, r.completed_at,
                       t.name as topic_name, c.name as chapter_name, s.name as subject_name, s.color as subject_color,
                       COALESCE(tp.understanding, 3) as understanding
                FROM revisions r
                JOIN topics t ON r.item_type = 'topic' AND r.item_id = t.id
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN topic_progress tp ON tp.user_id = %s AND tp.item_type = 'topic' AND tp.item_id = t.id
                WHERE r.user_id = %s
                ORDER BY r.due_date ASC, s.name ASC
            """, (user_id, user_id))
            
            for row in cursor.fetchall():
                item = dict(row)
                due_date_str = item["due_date"]
                is_done = item["is_completed"] == 1
                
                if is_done:
                    if len(queue["recent_completed"]) < 10:
                        queue["recent_completed"].append(item)
                else:
                    if due_date_str < today_str:
                        queue["overdue"].append(item)
                    elif due_date_str == today_str:
                        queue["due_today"].append(item)
                    elif due_date_str <= week_str:
                        queue["due_this_week"].append(item)
                    else:
                        queue["upcoming"].append(item)
                        
            return queue
    finally:
        conn.close()


def complete_adaptive_revision(user_id: int, revision_id: int, new_understanding: int = None):
    """Marks a revision as completed, updates topic progress & awards XP."""
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Fetch revision details
            cursor.execute("SELECT * FROM revisions WHERE id = %s AND user_id = %s", (revision_id, user_id))
            rev = cursor.fetchone()
            if not rev:
                return
            
            # Mark revision completed
            cursor.execute("""
                UPDATE revisions SET is_completed = 1, completed_at = %s
                WHERE id = %s AND user_id = %s
            """, (today_str, revision_id, user_id))
            
            item_type = rev["item_type"]
            item_id = rev["item_id"]
            
            # Update topic progress last_revised_at and status
            if new_understanding is not None:
                cursor.execute("""
                    UPDATE topic_progress 
                    SET status = 'Revision Done', understanding = %s, last_revised_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND item_type = %s AND item_id = %s
                """, (new_understanding, user_id, item_type, item_id))
            else:
                cursor.execute("""
                    UPDATE topic_progress 
                    SET status = 'Revision Done', last_revised_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND item_type = %s AND item_id = %s
                """, (user_id, item_type, item_id))
                
            conn.commit()
            st.cache_data.clear()
            
            # Award +50 XP for revision
            award_user_xp(user_id, "revision_completed", 50, f"Completed revision #{rev.get('interval_number', 1)}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# EXAM READINESS SCORE ENGINE (Phase 6)
# ══════════════════════════════════════════════

@st.cache_data(ttl=15, show_spinner=False)
def calculate_exam_readiness_score(user_id: int, term_id: int = None) -> dict:
    """
    Calculates composite Exam Readiness Score (0-100) using 5 core integrated metrics:
    - 1. Syllabus Coverage (30% weight)
    - 2. Conceptual Understanding & Quiz/Recall Index (25% weight)
    - 3. Spaced Repetition Adherence (20% weight)
    - 4. Mistake Resolution Rate (15% weight)
    - 5. Focus & Study Consistency (10% weight)
    Supports both overall curriculum readiness and specific exam term readiness.
    Includes dynamic actionable recommendations with page routing guidance.
    """
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    term_name = "Overall Curriculum"
    exam_date_str = ""
    days_left = None

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # ── 1. Syllabus & Topic Scope ──
            if term_id:
                cursor.execute("SELECT name, exam_date FROM terms WHERE id = %s AND user_id = %s", (term_id, user_id))
                t_row = cursor.fetchone()
                if t_row:
                    term_name = t_row["name"]
                    exam_date_str = t_row.get("exam_date", "") or ""
                    if exam_date_str:
                        try:
                            ex_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d").date()
                            days_left = (ex_date - today).days
                        except Exception:
                            pass

                cursor.execute("""
                    SELECT
                        COUNT(DISTINCT t.id) AS total_topics,
                        COUNT(DISTINCT CASE WHEN tp.status IN ('Completed', 'Revision Done') THEN t.id END) AS completed,
                        COALESCE(AVG(CASE WHEN tp.understanding IS NOT NULL THEN tp.understanding END), 3.0) AS avg_understanding
                    FROM term_chapters tc
                    JOIN topics t ON t.chapter_id = tc.chapter_id AND t.user_id = tc.user_id
                    LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = tc.user_id
                    WHERE tc.user_id = %s AND tc.term_id = %s
                """, (user_id, term_id))
                row = cursor.fetchone()
                total_topics = row["total_topics"] if row else 0
                completed_topics = row["completed"] if row else 0
                avg_understanding = float(row["avg_understanding"]) if row and row["avg_understanding"] else 3.0
            else:
                stats = get_overall_stats(user_id)
                total_topics = stats.get("total_topics", 0)
                completed_topics = stats.get("completed", 0)
                avg_understanding = float(stats.get("avg_understanding", 3.0))

            syllabus_pct = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0

            # ── 2. Conceptual Understanding Component (Blended with Quizzes & Recall) ──
            base_understanding_pct = min(100.0, max(0.0, ((avg_understanding - 1.0) / 4.0) * 100.0)) if total_topics > 0 else 0.0

            # Fetch Quiz performance
            cursor.execute("""
                SELECT COALESCE(AVG(accuracy_pct), -1) AS avg_quiz_acc, COUNT(*) AS quiz_count
                FROM quiz_attempts
                WHERE user_id = %s
            """, (user_id,))
            q_row = cursor.fetchone()
            avg_quiz_acc = float(q_row["avg_quiz_acc"]) if q_row and q_row["avg_quiz_acc"] is not None else -1
            quiz_count = q_row["quiz_count"] if q_row else 0

            # Fetch Active Recall performance
            cursor.execute("""
                SELECT COALESCE(AVG(understanding_score), -1) AS avg_recall_score, COUNT(*) AS recall_count
                FROM recall_responses
                WHERE user_id = %s
            """, (user_id,))
            rc_row = cursor.fetchone()
            avg_recall_score = float(rc_row["avg_recall_score"]) if rc_row and rc_row["avg_recall_score"] is not None else -1
            recall_count = rc_row["recall_count"] if rc_row else 0

            # Blend understanding signals
            if quiz_count > 0 and recall_count > 0:
                recall_pct = min(100.0, max(0.0, ((avg_recall_score - 1.0) / 4.0) * 100.0))
                understanding_pct = (base_understanding_pct * 0.50) + (avg_quiz_acc * 0.30) + (recall_pct * 0.20)
            elif quiz_count > 0:
                understanding_pct = (base_understanding_pct * 0.65) + (avg_quiz_acc * 0.35)
            elif recall_count > 0:
                recall_pct = min(100.0, max(0.0, ((avg_recall_score - 1.0) / 4.0) * 100.0))
                understanding_pct = (base_understanding_pct * 0.70) + (recall_pct * 0.30)
            else:
                understanding_pct = base_understanding_pct

            # ── 3. Spaced Repetition Adherence Component ──
            if term_id:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_revisions,
                        COUNT(CASE WHEN r.due_date < %s AND r.is_completed = 0 THEN 1 END) AS overdue,
                        COUNT(CASE WHEN r.is_completed = 1 THEN 1 END) AS completed_revs
                    FROM revisions r
                    JOIN topics t ON r.item_id = t.id
                    JOIN term_chapters tc ON tc.chapter_id = t.chapter_id AND tc.term_id = %s AND tc.user_id = %s
                    WHERE r.user_id = %s
                """, (today_str, term_id, user_id, user_id))
            else:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_revisions,
                        COUNT(CASE WHEN due_date < %s AND is_completed = 0 THEN 1 END) AS overdue,
                        COUNT(CASE WHEN is_completed = 1 THEN 1 END) AS completed_revs
                    FROM revisions
                    WHERE user_id = %s
                """, (today_str, user_id))
            rev_row = cursor.fetchone()
            total_revs = rev_row["total_revisions"] if rev_row else 0
            overdue_count = rev_row["overdue"] if rev_row else 0
            completed_revs = rev_row["completed_revs"] if rev_row else 0

            if total_revs > 0:
                revision_pct = max(0.0, min(100.0, ((total_revs - overdue_count) / total_revs) * 100.0))
            else:
                revision_pct = 85.0 if completed_topics > 0 else 0.0

            # ── 4. Mistake Resolution Component ──
            if term_id:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_mistakes,
                        COUNT(CASE WHEN m.is_reviewed = 1 THEN 1 END) AS reviewed
                    FROM mistakes m
                    JOIN topics t ON m.topic_id = t.id
                    JOIN term_chapters tc ON tc.chapter_id = t.chapter_id AND tc.term_id = %s AND tc.user_id = %s
                    WHERE m.user_id = %s
                """, (term_id, user_id, user_id))
            else:
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_mistakes,
                        COUNT(CASE WHEN is_reviewed = 1 THEN 1 END) AS reviewed
                    FROM mistakes
                    WHERE user_id = %s
                """, (user_id,))
            mis_row = cursor.fetchone()
            total_mistakes = mis_row["total_mistakes"] if mis_row else 0
            reviewed_mistakes = mis_row["reviewed"] if mis_row else 0
            unreviewed_mistakes = total_mistakes - reviewed_mistakes

            if total_mistakes > 0:
                mistake_pct = (reviewed_mistakes / total_mistakes * 100.0)
            else:
                mistake_pct = 100.0 if completed_topics > 0 else 0.0

            # ── 5. Focus & Study Consistency Component (Last 14 Days) ──
            two_weeks_ago = (today - datetime.timedelta(days=13)).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COUNT(DISTINCT session_date) AS study_days, COALESCE(SUM(duration_minutes), 0) AS total_focus_mins
                FROM study_sessions
                WHERE user_id = %s AND session_date >= %s AND session_date <= %s
            """, (user_id, two_weeks_ago, today_str))
            cons_row = cursor.fetchone()
            study_days = cons_row["study_days"] if cons_row else 0
            focus_mins = cons_row["total_focus_mins"] if cons_row else 0

            # Normalized consistency: 7+ study days or 300+ minutes focus gives high score
            day_score = min(100.0, (study_days / 10.0) * 100.0)
            min_score = min(100.0, (focus_mins / 300.0) * 100.0)
            consistency_pct = (day_score * 0.6) + (min_score * 0.4) if (study_days > 0 or focus_mins > 0) else (40.0 if completed_topics > 0 else 0.0)

            # ── Weighted Composite Readiness Score (0-100) ──
            readiness_score = int(round(
                (syllabus_pct * 0.30) +
                (understanding_pct * 0.25) +
                (revision_pct * 0.20) +
                (mistake_pct * 0.15) +
                (consistency_pct * 0.10)
            ))
            readiness_score = max(0, min(100, readiness_score))

            # ── Actionable Recommendations ──
            recommendations = []
            priorities = get_top_nexus_priorities(user_id, limit=3)
            critical_count = sum(1 for p in priorities if p["tier"] == "Critical")

            if overdue_count > 0:
                recommendations.append(f"⚠️ Clear {overdue_count} overdue revision(s) in Revision Queue.")
            if unreviewed_mistakes > 0:
                recommendations.append(f"❌ Review {unreviewed_mistakes} unmastered question(s) in Mistake Vault.")
            if critical_count > 0:
                top_crit = priorities[0]
                recommendations.append(f"🔴 Study critical topic: {top_crit['subject_name']} → {top_crit['topic_name']}.")
            if quiz_count == 0:
                recommendations.append("🎯 Take your first Quiz to benchmark conceptual mastery.")
            elif avg_quiz_acc < 70.0:
                recommendations.append("🎯 Take an adaptive practice quiz on your weak topics.")
            if recall_count == 0:
                recommendations.append("💡 Practice Active Recall on a key chapter using Feynman technique.")
            if syllabus_pct < 65.0:
                recommendations.append("📚 Complete remaining syllabus chapters to improve coverage.")
            factors_dict = {
                "completion": round(syllabus_pct, 1),
                "understanding": round(understanding_pct, 1),
                "revision_adherence": round(revision_pct, 1),
                "mistake_resolution": round(mistake_pct, 1),
                "study_consistency": round(consistency_pct, 1)
            }

            return {
                "readiness_score": readiness_score,
                "composite_score": readiness_score,
                "term_id": term_id,
                "term_name": term_name,
                "exam_date": exam_date_str,
                "days_left": days_left,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "syllabus_pct": round(syllabus_pct, 1),
                "understanding_pct": round(understanding_pct, 1),
                "revision_pct": round(revision_pct, 1),
                "mistake_pct": round(mistake_pct, 1),
                "practice_pct": round(consistency_pct, 1),
                "consistency_pct": round(consistency_pct, 1),
                "overdue_count": overdue_count,
                "unreviewed_mistakes": unreviewed_mistakes,
                "total_mistakes": total_mistakes,
                "critical_count": critical_count,
                "quiz_count": quiz_count,
                "avg_quiz_acc": round(avg_quiz_acc, 1) if avg_quiz_acc >= 0 else None,
                "recall_count": recall_count,
                "factors": factors_dict,
                "breakdown": factors_dict,
                "recommendations": recommendations[:3]
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# NEXUS MISTAKE VAULT (Phase 7)
# ══════════════════════════════════════════════

def add_mistake(user_id: int, question: str, mistake_type: str, subject_id: int = None,
                chapter_id: int = None, topic_id: int = None, your_answer: str = "",
                correct_answer: str = "", explanation: str = "", prevention_strategy: str = "") -> int:
    """Adds a new recorded mistake into the student's Mistake Vault."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO mistakes (user_id, subject_id, chapter_id, topic_id, question, your_answer,
                                      correct_answer, mistake_type, explanation, prevention_strategy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, subject_id, chapter_id, topic_id, question.strip(), your_answer.strip(),
                  correct_answer.strip(), mistake_type, explanation.strip(), prevention_strategy.strip()))
            mistake_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            award_user_xp(user_id, "logged_mistake", 20, "Logged mistake in Vault")
            return mistake_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=15, show_spinner=False)
def get_all_mistakes(user_id: int, subject_id: int = None, mistake_type: str = None, is_reviewed: int = None) -> list:
    """Retrieves mistakes with optional subject, type, and review status filtering."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                SELECT m.*, s.name as subject_name, s.color as subject_color, c.name as chapter_name, t.name as topic_name
                FROM mistakes m
                LEFT JOIN subjects s ON m.subject_id = s.id
                LEFT JOIN chapters c ON m.chapter_id = c.id
                LEFT JOIN topics t ON m.topic_id = t.id
                WHERE m.user_id = %s
            """
            params = [user_id]
            if subject_id:
                query += " AND m.subject_id = %s"
                params.append(subject_id)
            if mistake_type and mistake_type != "All":
                query += " AND m.mistake_type = %s"
                params.append(mistake_type)
            if is_reviewed is not None:
                query += " AND m.is_reviewed = %s"
                params.append(1 if is_reviewed else 0)
            query += " ORDER BY m.created_at DESC"
            
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def add_mistake_batch(user_id: int, mistakes_list: list) -> int:
    """Batch adds multiple recorded mistakes into the student's Mistake Vault."""
    if not mistakes_list:
        return 0
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            inserted_count = 0
            for m in mistakes_list:
                cursor.execute("""
                    INSERT INTO mistakes (user_id, subject_id, chapter_id, topic_id, question, your_answer,
                                          correct_answer, mistake_type, explanation, prevention_strategy)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, m.get("subject_id"), m.get("chapter_id"), m.get("topic_id"),
                      m["question"].strip(), m.get("your_answer", "").strip(),
                      m.get("correct_answer", "").strip(), m.get("mistake_type", "Conceptual"),
                      m.get("explanation", "").strip(), m.get("prevention_strategy", "").strip()))
                inserted_count += 1
            conn.commit()
            st.cache_data.clear()
            award_user_xp(user_id, "logged_mistakes_batch", inserted_count * 20, f"Logged {inserted_count} mistakes in Vault")
            return inserted_count
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_mistake_analytics(user_id: int) -> dict:
    """Computes distribution, unreviewed vs reviewed counts, and percentage breakdown of mistake types."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN is_reviewed = 0 THEN 1 END) as unreviewed,
                    COUNT(CASE WHEN is_reviewed = 1 THEN 1 END) as reviewed
                FROM mistakes
                WHERE user_id = %s
            """, (user_id,))
            totals_row = cursor.fetchone()
            total = totals_row["total"] or 0
            unreviewed = totals_row["unreviewed"] or 0
            reviewed = totals_row["reviewed"] or 0

            cursor.execute("""
                SELECT mistake_type, COUNT(*) as count
                FROM mistakes
                WHERE user_id = %s
                GROUP BY mistake_type
                ORDER BY count DESC
            """, (user_id,))
            rows = cursor.fetchall()
            breakdown = []
            for r in rows:
                pct = round((r["count"] / total * 100), 1) if total > 0 else 0
                breakdown.append({
                    "type": r["mistake_type"],
                    "count": r["count"],
                    "pct": pct
                })
            return {
                "total": total,
                "unreviewed": unreviewed,
                "reviewed": reviewed,
                "breakdown": breakdown
            }
    finally:
        conn.close()


def toggle_mistake_reviewed(user_id: int, mistake_id: int, is_reviewed: int = None):
    """Toggles reviewed status of a mistake and awards mastery XP."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if is_reviewed is None:
                cursor.execute("SELECT is_reviewed FROM mistakes WHERE id = %s AND user_id = %s", (mistake_id, user_id))
                curr = cursor.fetchone()
                new_val = 0 if curr and curr[0] == 1 else 1
            else:
                new_val = 1 if is_reviewed else 0

            cursor.execute("UPDATE mistakes SET is_reviewed = %s WHERE id = %s AND user_id = %s", (new_val, mistake_id, user_id))
            conn.commit()
            st.cache_data.clear()
            if new_val == 1:
                award_user_xp(user_id, "mastered_mistake", 15, "Mastered mistake in Vault")
            return new_val
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_mistake(user_id: int, mistake_id: int):
    """Deletes a mistake from the vault."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM mistakes WHERE id = %s AND user_id = %s", (mistake_id, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# NEXUS NOTES SYSTEM (Phase 12)
# ══════════════════════════════════════════════

def add_note(user_id: int, subject_id: int, chapter_id: int, topic_id: int,
             title: str, content: str, tags: str = "", is_pinned: int = 0) -> int:
    """Creates a new rich note linked to a subject, chapter, and topic."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO notes (user_id, subject_id, chapter_id, topic_id, title, content, tags, is_pinned)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, subject_id, chapter_id, topic_id, title.strip(), content.strip(), tags.strip(), is_pinned))
            note_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            award_user_xp(user_id, "created_note", 25, f"Created note: {title}")
            return note_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=15, show_spinner=False)
def get_all_notes(user_id: int, subject_id: int = None, topic_id: int = None) -> list:
    """Retrieves all notes with optional subject or topic filters."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                SELECT n.*, s.name as subject_name, s.color as subject_color, c.name as chapter_name, t.name as topic_name
                FROM notes n
                JOIN subjects s ON n.subject_id = s.id
                JOIN chapters c ON n.chapter_id = c.id
                JOIN topics t ON n.topic_id = t.id
                WHERE n.user_id = %s
            """
            params = [user_id]
            if subject_id:
                query += " AND n.subject_id = %s"
                params.append(subject_id)
            if topic_id:
                query += " AND n.topic_id = %s"
                params.append(topic_id)
            query += " ORDER BY n.is_pinned DESC, n.updated_at DESC"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def delete_note(user_id: int, note_id: int):
    """Deletes a note."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# FORMULA VAULT (Phase 13)
# ══════════════════════════════════════════════

def add_formula(user_id: int, subject_id: int, chapter_id: int, title: str,
                formula_latex: str, topic_id: int = None, description: str = "") -> int:
    """Adds a mathematical/scientific formula with LaTeX rendering to the vault."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO formulas (user_id, subject_id, chapter_id, topic_id, title, formula_latex, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, subject_id, chapter_id, topic_id, title.strip(), formula_latex.strip(), description.strip()))
            formula_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            return formula_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=20, show_spinner=False)
def get_all_formulas(user_id: int, subject_id: int = None) -> list:
    """Retrieves all formulas with optional subject filtering."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                SELECT f.*, s.name as subject_name, s.color as subject_color, c.name as chapter_name
                FROM formulas f
                JOIN subjects s ON f.subject_id = s.id
                JOIN chapters c ON f.chapter_id = c.id
                WHERE f.user_id = %s
            """
            params = [user_id]
            if subject_id:
                query += " AND f.subject_id = %s"
                params.append(subject_id)
            query += " ORDER BY f.is_favorite DESC, s.name, c.name, f.title"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def toggle_formula_favorite(user_id: int, formula_id: int, is_fav: int):
    """Toggles favorite bookmark for a formula."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE formulas SET is_favorite = %s WHERE id = %s AND user_id = %s", (is_fav, formula_id, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_formula(user_id: int, formula_id: int):
    """Deletes a formula from the vault."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM formulas WHERE id = %s AND user_id = %s", (formula_id, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# GAMIFICATION & STREAKS (Phase 11)
# ══════════════════════════════════════════════

def award_user_xp(user_id: int, action_type: str, xp_amount: int, description: str = ""):
    """Awards XP to a student and recalculates their Nexus Level."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Log XP Event
            cursor.execute("""
                INSERT INTO user_xp_events (user_id, action_type, xp_amount, description)
                VALUES (%s, %s, %s, %s)
            """, (user_id, action_type, xp_amount, description))
            
            # 2. Update User Total XP
            cursor.execute("""
                UPDATE users 
                SET total_xp = COALESCE(total_xp, 0) + %s
                WHERE id = %s
                RETURNING total_xp
            """, (xp_amount, user_id))
            new_total = cursor.fetchone()[0]
            
            # 3. Calculate New Level
            # Level 1 (0 XP), Level 5 (1000 XP), Level 10 (3000 XP), Level 20 (7500 XP), Level 30 (15000 XP), Level 50 (30000 XP)
            if new_total >= 30000:
                level = 50
            elif new_total >= 15000:
                level = 30
            elif new_total >= 7500:
                level = 20
            elif new_total >= 3000:
                level = 10
            elif new_total >= 1000:
                level = 5
            elif new_total >= 300:
                level = 2
            else:
                level = 1
                
            cursor.execute("UPDATE users SET nexus_level = %s WHERE id = %s", (level, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_user_xp_summary(user_id: int) -> dict:
    """Returns total XP, current Level, level title, and progress to next level."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT total_xp, nexus_level, current_streak, longest_streak FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                return {"total_xp": 0, "level": 1, "title": "Recruit", "streak": 0, "longest_streak": 0}
            
            total_xp = row["total_xp"] or 0
            level = row["nexus_level"] or 1
            streak = row["current_streak"] or 0
            longest = row["longest_streak"] or 0
            
            if level >= 50:
                title = "Nexus Elite"
                next_xp = 50000
            elif level >= 30:
                title = "Master Scholar"
                next_xp = 30000
            elif level >= 20:
                title = "Strategist"
                next_xp = 15000
            elif level >= 10:
                title = "Senior Scholar"
                next_xp = 7500
            elif level >= 5:
                title = "Explorer"
                next_xp = 3000
            elif level >= 2:
                title = "Apprentice"
                next_xp = 1000
            else:
                title = "Recruit"
                next_xp = 300
                
            progress_pct = min(100, int((total_xp / next_xp) * 100)) if next_xp > 0 else 100
            return {
                "total_xp": total_xp,
                "level": level,
                "title": title,
                "streak": streak,
                "longest_streak": longest,
                "next_xp": next_xp,
                "progress_pct": progress_pct
            }
    finally:
        conn.close()


def update_user_streak(user_id: int):
    """Updates the student's daily study streak."""
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT last_active_date, current_streak, longest_streak FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return
            
            last_date = user["last_active_date"]
            curr_streak = user["current_streak"] or 0
            longest = user["longest_streak"] or 0
            
            if last_date == today_str:
                # Already active today
                return
            elif last_date == yesterday_str:
                # Consecutive day active!
                new_streak = curr_streak + 1
            else:
                # Broken streak, reset to 1
                new_streak = 1
                
            new_longest = max(longest, new_streak)
            cursor.execute("""
                UPDATE users 
                SET last_active_date = %s, current_streak = %s, longest_streak = %s
                WHERE id = %s
            """, (today_str, new_streak, new_longest, user_id))
            conn.commit()
            st.cache_data.clear()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════
# EXAM READINESS SCORE & TERM INTEGRATION
# ══════════════════════════════════════════════

def compute_exam_readiness(user_id: int, term_id: int) -> dict:
    """
    Computes a weighted Exam Readiness Score (0-100) for a specific term.
    Delegates to the 5-factor composite calculate_exam_readiness_score engine.
    """
    return calculate_exam_readiness_score(user_id, term_id=term_id)


def get_all_readiness_scores(user_id: int) -> list:
    """Compute readiness scores for all active (non-done) terms."""
    terms = get_active_upcoming_terms(user_id)
    results = []
    for t in terms:
        score = calculate_exam_readiness_score(user_id, term_id=t["id"])
        results.append(score)
    return results


# ══════════════════════════════════════════════
# ENHANCED MISTAKE VAULT & RE-QUIZ ENGINE
# ══════════════════════════════════════════════

def get_mistake_trend(user_id: int) -> list:
    """Returns weekly mistake counts over last 8 weeks for trend analysis."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    DATE_TRUNC('week', created_at)::DATE AS week_start,
                    COUNT(*) AS count
                FROM mistakes
                WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '56 days'
                GROUP BY DATE_TRUNC('week', created_at)
                ORDER BY week_start ASC
            """, (user_id,))
            rows = cursor.fetchall()
            return [{"week": str(r[0]), "count": r[1]} for r in rows]
    finally:
        conn.close()


def get_unreviewed_mistakes_for_quiz(user_id: int, limit: int = 10) -> list:
    """Fetches unreviewed mistakes to generate a targeted re-quiz."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT m.*, s.name as subject_name, s.color as subject_color,
                       c.name as chapter_name, t.name as topic_name
                FROM mistakes m
                LEFT JOIN subjects s ON m.subject_id = s.id
                LEFT JOIN chapters c ON m.chapter_id = c.id
                LEFT JOIN topics t ON m.topic_id = t.id
                WHERE m.user_id = %s AND m.is_reviewed = 0
                ORDER BY m.created_at DESC
                LIMIT %s
            """, (user_id, limit))
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def generate_mistake_requiz(user_id: int, limit: int = 5, count: int = None) -> dict:
    """Generates an interactive re-quiz payload directly from unreviewed Mistake Vault items."""
    effective_limit = count if count is not None else limit
    mistakes = get_unreviewed_mistakes_for_quiz(user_id, limit=effective_limit)
    if not mistakes:
        return None

    questions = []
    for idx, m in enumerate(mistakes, 1):
        corr = m.get("correct_answer", "").strip() or "Standard definition/solution"
        wrong = m.get("your_answer", "").strip() or "Common misconception"
        
        # Build 4 options if feasible
        opts = [corr, wrong]
        alt1 = f"Inverted {corr[:20]}" if len(corr) > 5 else "Alternate incorrect formulation"
        alt2 = "None of the above"
        if alt1 not in opts:
            opts.append(alt1)
        if alt2 not in opts:
            opts.append(alt2)
        import random
        random.shuffle(opts)
        
        questions.append({
            "id": idx,
            "mistake_id": m["id"],
            "topic_id": m.get("topic_id"),
            "subject_id": m.get("subject_id"),
            "subject_name": m.get("subject_name", "General"),
            "question": m["question"],
            "options": opts,
            "correct_answer": corr,
            "explanation": m.get("explanation") or f"Prevention rule: {m.get('prevention_strategy') or 'Review fundamental concept carefully.'}",
            "prevention_strategy": m.get("prevention_strategy", "")
        })

    import json
    title = f"🎯 Mistake Vault Re-Quiz ({len(questions)} items)"
    quiz_id = create_quiz(
        user_id=user_id,
        title=title,
        subject_id=mistakes[0].get("subject_id"),
        chapter_id=mistakes[0].get("chapter_id"),
        topic_id=mistakes[0].get("topic_id"),
        difficulty="Adaptive",
        questions_json=json.dumps(questions)
    )

    return {
        "quiz_id": quiz_id,
        "title": title,
        "questions": questions
    }


def mark_mistakes_reviewed_from_quiz(user_id: int, mistake_ids: list):
    """Marks mistakes as reviewed after student gets them right on a re-quiz."""
    if not mistake_ids:
        return
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE mistakes SET is_reviewed = 1 
                WHERE user_id = %s AND id = ANY(%s)
            """, (user_id, mistake_ids))
            conn.commit()
            st.cache_data.clear()
            award_user_xp(user_id, "mastered_mistakes_requiz", len(mistake_ids) * 25, f"Mastered {len(mistake_ids)} mistakes on Re-Quiz")
    finally:
        conn.close()


# ══════════════════════════════════════════════
# COMPREHENSIVE QUIZ ENGINE
# ══════════════════════════════════════════════

CURATED_QUESTION_BANK = {
    "Physics": [
        {
            "topic_keywords": ["force", "newton", "motion", "gravity", "work", "energy"],
            "question": "What is the SI unit of Force and its dimensional definition?",
            "options": ["Newton (kg·m/s²)", "Joule (kg·m²/s²)", "Pascal (N/m²)", "Watt (J/s)"],
            "correct_answer": "Newton (kg·m/s²)",
            "explanation": "1 Newton is the force required to give a mass of 1 kg an acceleration of 1 m/s² (F = ma)."
        },
        {
            "topic_keywords": ["lens", "refraction", "light", "optics", "focal"],
            "question": "A lens has a power of -2.5 D. What is its focal length and nature?",
            "options": ["-40 cm, Concave lens", "+40 cm, Convex lens", "-25 cm, Concave lens", "+25 cm, Convex lens"],
            "correct_answer": "-40 cm, Concave lens",
            "explanation": "Power P = 1/f(m) -> f = 1/(-2.5) = -0.4 m = -40 cm. Negative focal length indicates a diverging (concave) lens."
        },
        {
            "topic_keywords": ["ohm", "current", "circuit", "electricity", "resistance"],
            "question": "If three 6-ohm resistors are connected in parallel, what is the equivalent resistance?",
            "options": ["2 Ω", "18 Ω", "3 Ω", "0.5 Ω"],
            "correct_answer": "2 Ω",
            "explanation": "1/R_eq = 1/6 + 1/6 + 1/6 = 3/6 = 1/2 -> R_eq = 2 Ω."
        },
        {
            "topic_keywords": ["sound", "echo", "frequency", "wave"],
            "question": "What is the minimum distance between source and reflector to hear a distinct echo in air at 20°C?",
            "options": ["17.2 meters", "34.4 meters", "10.0 meters", "5.0 meters"],
            "correct_answer": "17.2 meters",
            "explanation": "Persistence of hearing is 0.1s. Speed of sound is ~344 m/s. Total distance = 344 * 0.1 = 34.4m -> Distance to wall = 34.4 / 2 = 17.2m."
        }
    ],
    "Chemistry": [
        {
            "topic_keywords": ["periodic", "element", "table", "atomic", "trend"],
            "question": "Across a period from left to right in the modern periodic table, what happens to atomic radius?",
            "options": ["Decreases due to increasing effective nuclear charge", "Increases due to extra shells", "Remains constant", "First increases then decreases"],
            "correct_answer": "Decreases due to increasing effective nuclear charge",
            "explanation": "Electrons are added to the same principal shell while protons increase, pulling the valence electrons closer to the nucleus."
        },
        {
            "topic_keywords": ["acid", "base", "salt", "ph"],
            "question": "What is the pH of a neutral aqueous solution at 25°C?",
            "options": ["7.0", "1.0", "14.0", "0.0"],
            "correct_answer": "7.0",
            "explanation": "At 25°C, [H+] = [OH-] = 10^-7 M, giving pH = -log(10^-7) = 7.0."
        },
        {
            "topic_keywords": ["mole", "avogadro", "stoichiometry"],
            "question": "How many atoms are present in 1 mole of any monoatomic element?",
            "options": ["6.022 × 10²³ atoms", "3.011 × 10²³ atoms", "1.204 × 10²⁴ atoms", "6.022 × 10²² atoms"],
            "correct_answer": "6.022 × 10²³ atoms",
            "explanation": "Avogadro's constant is exactly 6.02214076 × 10²³ particles per mole."
        },
        {
            "topic_keywords": ["organic", "carbon", "alkane", "alkene", "isomer"],
            "question": "What is the general molecular formula for homologous series of Alkenes?",
            "options": ["CnH2n", "CnH2n+2", "CnH2n-2", "CnH2n+1OH"],
            "correct_answer": "CnH2n",
            "explanation": "Alkenes contain one carbon-carbon double bond and conform to the general formula CnH2n."
        }
    ],
    "Biology": [
        {
            "topic_keywords": ["photosynthesis", "chlorophyll", "plant", "light"],
            "question": "During the light-dependent reaction of photosynthesis, what is the primary source of released oxygen?",
            "options": ["Photolysis of water (H2O)", "Breakdown of carbon dioxide (CO2)", "Decomposition of glucose", "Atmospheric air"],
            "correct_answer": "Photolysis of water (H2O)",
            "explanation": "Light energy splits water molecules (2H2O -> 4H+ + 4e- + O2) releasing oxygen gas into the atmosphere."
        },
        {
            "topic_keywords": ["cell", "mitosis", "meiosis", "division", "chromosome"],
            "question": "In which phase of mitosis do sister chromatids separate and move toward opposite poles?",
            "options": ["Anaphase", "Prophase", "Metaphase", "Telophase"],
            "correct_answer": "Anaphase",
            "explanation": "During Anaphase, centromeres split and spindle fibers contract, pulling sister chromatids to opposite poles."
        },
        {
            "topic_keywords": ["genetics", "mendel", "dna", "heredity", "gene"],
            "question": "What is the classic monohybrid phenotypic ratio observed in Mendel's F2 generation?",
            "options": ["3 : 1", "1 : 2 : 1", "9 : 3 : 3 : 1", "1 : 1"],
            "correct_answer": "3 : 1",
            "explanation": "Cross of two heterozygous individuals (Tt x Tt) yields 3 dominant to 1 recessive phenotype."
        }
    ],
    "Mathematics": [
        {
            "topic_keywords": ["quadratic", "equation", "roots", "discriminant"],
            "question": "If the discriminant b² - 4ac of a quadratic equation is greater than zero and not a perfect square, what are the roots?",
            "options": ["Real, unequal, and irrational", "Real, equal, and rational", "Complex/imaginary", "Real, unequal, and rational"],
            "correct_answer": "Real, unequal, and irrational",
            "explanation": "D > 0 indicates two real distinct roots; non-perfect square means square root is irrational."
        },
        {
            "topic_keywords": ["trigonometry", "sin", "cos", "tan", "identity"],
            "question": "What is the value of sin²(θ) + cos²(θ) for any angle θ?",
            "options": ["1", "0", "tan²(θ)", "2"],
            "correct_answer": "1",
            "explanation": "Fundamental Pythagorean trigonometric identity: sin²θ + cos²θ = 1."
        },
        {
            "topic_keywords": ["circle", "tangent", "radius", "chord"],
            "question": "What is the angle between a tangent to a circle and the radius drawn through the point of contact?",
            "options": ["90° (Perpendicular)", "45°", "60°", "180°"],
            "correct_answer": "90° (Perpendicular)",
            "explanation": "Theorem: The tangent at any point of a circle is perpendicular to the radius through the point of contact."
        }
    ]
}


def get_question_bank_for_topic(user_id: int, subject_id: int = None, chapter_id: int = None,
                                topic_id: int = None, difficulty: str = "Mixed", count: int = 5) -> list:
    """
    Generates or retrieves structured multiple-choice questions for a specific topic, chapter, or subject.
    Combines curated high-yield syllabus question banks with smart dynamic generators.
    """
    questions = []
    subj_name = ""
    chap_name = ""
    top_name = ""
    
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            if topic_id:
                cursor.execute("""
                    SELECT t.name as topic_name, c.name as chapter_name, s.name as subject_name
                    FROM topics t
                    JOIN chapters c ON t.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    WHERE t.id = %s AND t.user_id = %s
                """, (topic_id, user_id))
                r = cursor.fetchone()
                if r:
                    top_name = r["topic_name"]
                    chap_name = r["chapter_name"]
                    subj_name = r["subject_name"]
            elif chapter_id:
                cursor.execute("""
                    SELECT c.name as chapter_name, s.name as subject_name
                    FROM chapters c
                    JOIN subjects s ON c.subject_id = s.id
                    WHERE c.id = %s AND c.user_id = %s
                """, (chapter_id, user_id))
                r = cursor.fetchone()
                if r:
                    chap_name = r["chapter_name"]
                    subj_name = r["subject_name"]
            elif subject_id:
                cursor.execute("SELECT name as subject_name FROM subjects WHERE id = %s AND user_id = %s", (subject_id, user_id))
                r = cursor.fetchone()
                if r:
                    subj_name = r["subject_name"]
    finally:
        conn.close()

    # Search curated bank for subject match
    matched_questions = []
    for s_key, q_list in CURATED_QUESTION_BANK.items():
        if s_key.lower() in subj_name.lower() or subj_name.lower() in s_key.lower():
            for q in q_list:
                # Check keyword relevance
                q_keywords = q.get("topic_keywords", [])
                target_str = f"{top_name} {chap_name}".lower()
                if any(kw in target_str for kw in q_keywords):
                    matched_questions.append(q)
            if not matched_questions:
                matched_questions = list(q_list)

    # Dynamic generation from syllabus topics & notes if bank has fewer questions
    import random
    if matched_questions:
        random.shuffle(matched_questions)
        for q in matched_questions[:count]:
            opts = list(q["options"])
            random.shuffle(opts)
            questions.append({
                "id": len(questions) + 1,
                "topic_id": topic_id,
                "subject_id": subject_id,
                "question": q["question"],
                "options": opts,
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"]
            })

    # Fill remaining count with dynamic conceptual questions
    while len(questions) < count:
        curr_idx = len(questions) + 1
        t_label = top_name or chap_name or subj_name or "Core Concept"
        
        dynamic_q_types = [
            {
                "question": f"Which of the following is the fundamental governing principle of '{t_label}'?",
                "correct_answer": f"Conservation laws and direct systematic relations governing {t_label}",
                "distractors": [
                    f"Spontaneous arbitrary changes without conservation in {t_label}",
                    f"Inverse exponential decay without energy transfer",
                    f"Uniform non-responsive equilibrium in all conditions"
                ],
                "explanation": f"The core framework of {t_label} relies on established fundamental physical/chemical/mathematical conservation principles."
            },
            {
                "question": f"When analyzing '{t_label}', what is the primary consequence of changing standard baseline conditions?",
                "correct_answer": f"Proportional reaction governed by equilibrium and rate constants of {t_label}",
                "distractors": [
                    "Complete cessation of all molecular or mathematical interactions",
                    "Independent random fluctuations unrelated to initial parameters",
                    "Immediate inversion of all sign conventions"
                ],
                "explanation": f"According to fundamental laws, variations in {t_label} shift equilibrium or outputs in predictable proportional ways."
            },
            {
                "question": f"What is the standard methodology to verify and solve problems in '{t_label}'?",
                "correct_answer": f"State given variables, apply governing formula/theorem, verify units, and compute solution",
                "distractors": [
                    "Estimate values without unit verification or formula derivation",
                    "Apply unrelated trigonometric identities without checking assumptions",
                    "Assume zero resistance or zero mass in all real-world contexts"
                ],
                "explanation": f"Systematic problem solving in {t_label} requires disciplined variable identification, formula application, and unit consistency."
            },
            {
                "question": f"Which common misconception must be avoided when studying '{t_label}'?",
                "correct_answer": f"Confusing scalar magnitudes with directional vector quantities or rate with total quantity",
                "distractors": [
                    "Checking dimensional consistency before finalizing solutions",
                    "Maintaining proper sign conventions in coordinate geometry and optics",
                    "Balancing both sides of mathematical or chemical equations"
                ],
                "explanation": f"A primary source of exam errors in {t_label} is confusing rate vs total quantity or forgetting sign and unit conventions."
            }
        ]
        
        template = dynamic_q_types[(curr_idx - 1) % len(dynamic_q_types)]
        opts = [template["correct_answer"]] + template["distractors"]
        random.shuffle(opts)
        
        questions.append({
            "id": curr_idx,
            "topic_id": topic_id,
            "subject_id": subject_id,
            "question": template["question"],
            "options": opts,
            "correct_answer": template["correct_answer"],
            "explanation": template["explanation"]
        })

    return questions[:count]


def create_quiz(user_id: int, title: str, subject_id: int = None,
                chapter_id: int = None, topic_id: int = None,
                difficulty: str = "Mixed", questions_json = "[]", questions = None) -> int:
    """Creates a new quiz record and returns its ID."""
    if questions is not None:
        q_payload = json.dumps(questions) if isinstance(questions, (list, dict)) else str(questions)
    elif isinstance(questions_json, (list, dict)):
        q_payload = json.dumps(questions_json)
    else:
        q_payload = str(questions_json or "[]")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO quizzes (user_id, title, subject_id, chapter_id, topic_id, difficulty, questions_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, title.strip(), subject_id, chapter_id, topic_id, difficulty, q_payload))
            quiz_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            return quiz_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def save_quiz_attempt(user_id: int, quiz_id: int, score: int, total_questions: int,
                      accuracy_pct: float, time_taken_seconds: int = 0,
                      weak_topics_json: str = "[]") -> int:
    """Records a quiz attempt."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, accuracy_pct,
                                           time_taken_seconds, weak_topics_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, quiz_id, score, total_questions, accuracy_pct,
                  time_taken_seconds, weak_topics_json))
            attempt_id = cursor.fetchone()[0]
            conn.commit()
            st.cache_data.clear()
            return attempt_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def submit_quiz_and_sync_nexus(user_id: int, quiz_id: int, user_answers: dict,
                               time_taken_seconds: int = 0, auto_save_mistakes: bool = True) -> dict:
    """
    Evaluates quiz answers, updates topic understanding, auto-saves wrong answers to Mistake Vault,
    schedules adaptive revisions for weak areas, awards XP, and updates daily study streak.
    """
    quiz = get_quiz_by_id(user_id, quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")

    import json
    questions = json.loads(quiz.get("questions_json", "[]"))
    total_q = len(questions)
    if total_q == 0:
        return {"score": 0, "total": 0, "accuracy_pct": 0, "xp_earned": 0, "mistakes_logged": 0}

    correct_count = 0
    mistakes_to_log = []
    solved_mistake_ids = []

    for q in questions:
        q_id = str(q["id"])
        selected_ans = user_answers.get(q_id, "").strip()
        correct_ans = q.get("correct_answer", "").strip()

        if selected_ans == correct_ans:
            correct_count += 1
            if q.get("mistake_id"):
                solved_mistake_ids.append(q["mistake_id"])
        else:
            # Wrong answer -> prepare mistake entry
            mistakes_to_log.append({
                "subject_id": q.get("subject_id") or quiz.get("subject_id"),
                "chapter_id": quiz.get("chapter_id"),
                "topic_id": q.get("topic_id") or quiz.get("topic_id"),
                "question": q["question"],
                "your_answer": selected_ans or "No answer submitted",
                "correct_answer": correct_ans,
                "mistake_type": "Conceptual" if "principle" in q["question"].lower() else "Calculation",
                "explanation": q.get("explanation", "Review core concept fundamentals."),
                "prevention_strategy": q.get("prevention_strategy") or "Double-check units, definitions, and question conditions before answering."
            })

    accuracy_pct = round((correct_count / total_q * 100.0), 1)

    # 1. Auto-save mistakes to Mistake Vault
    mistakes_logged = 0
    if auto_save_mistakes and mistakes_to_log:
        mistakes_logged = add_mistake_batch(user_id, mistakes_to_log)

    # 2. If solved items came from a Mistake Re-Quiz, mark them reviewed
    if solved_mistake_ids:
        mark_mistakes_reviewed_from_quiz(user_id, solved_mistake_ids)

    # 3. Update topic understanding & Spaced Repetition sync
    topic_id = quiz.get("topic_id")
    if topic_id:
        if accuracy_pct >= 80.0:
            save_progress(user_id, "topic", topic_id, understanding=5)
        elif accuracy_pct >= 60.0:
            save_progress(user_id, "topic", topic_id, understanding=4)
        else:
            # Low accuracy (<60%) -> mark topic as understanding 2 and trigger revisions
            save_progress(user_id, "topic", topic_id, understanding=2)
            try:
                schedule_adaptive_revisions(user_id, "topic", topic_id, 2)
            except Exception:
                pass

    # 4. Award XP and update streak
    earned_xp = max(25, int(accuracy_pct * 0.75) + (correct_count * 10))
    award_user_xp(user_id, "quiz_completed", earned_xp, f"Completed quiz: {quiz.get('title')} ({accuracy_pct}%)")
    update_user_streak(user_id)

    # 5. Record attempt
    attempt_id = save_quiz_attempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=correct_count,
        total_questions=total_q,
        accuracy_pct=accuracy_pct,
        time_taken_seconds=time_taken_seconds,
        weak_topics_json=json.dumps([m["question"][:30] for m in mistakes_to_log])
    )

    return {
        "attempt_id": attempt_id,
        "score": correct_count,
        "total": total_q,
        "accuracy_pct": accuracy_pct,
        "earned_xp": earned_xp,
        "mistakes_logged": mistakes_logged,
        "solved_mistakes_count": len(solved_mistake_ids),
        "incorrect_questions": mistakes_to_log
    }


@st.cache_data(ttl=30, show_spinner=False)
def get_quiz_history(user_id: int, limit: int = 20) -> list:
    """Retrieves quiz attempt history with quiz metadata."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT qa.*, q.title as quiz_title, q.difficulty,
                       s.name as subject_name, s.color as subject_color
                FROM quiz_attempts qa
                JOIN quizzes q ON qa.quiz_id = q.id
                LEFT JOIN subjects s ON q.subject_id = s.id
                WHERE qa.user_id = %s
                ORDER BY qa.created_at DESC
                LIMIT %s
            """, (user_id, limit))
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_quiz_by_id(user_id: int, quiz_id: int) -> dict:
    """Retrieves a specific quiz with its questions JSON."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT q.*, s.name as subject_name, c.name as chapter_name, t.name as topic_name
                FROM quizzes q
                LEFT JOIN subjects s ON q.subject_id = s.id
                LEFT JOIN chapters c ON q.chapter_id = c.id
                LEFT JOIN topics t ON q.topic_id = t.id
                WHERE q.id = %s AND q.user_id = %s
            """, (quiz_id, user_id))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


# ══════════════════════════════════════════════
# COMPREHENSIVE ACTIVE RECALL ENGINE
# ══════════════════════════════════════════════

def get_active_recall_prompt(user_id: int, topic_id: int) -> dict:
    """
    Generates a structured Feynman Technique Active Recall prompt, key concept checklist,
    and reference cues for a topic.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT t.name as topic_name, c.name as chapter_name, s.name as subject_name,
                       COALESCE(tp.understanding, 3) as understanding, COALESCE(tp.notes, '') as user_notes
                FROM topics t
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = %s
                WHERE t.id = %s AND t.user_id = %s
            """, (user_id, topic_id, user_id))
            row = cursor.fetchone()
            if not row:
                return None

            # Fetch any notes or formulas for reference rubric
            cursor.execute("SELECT title, content FROM notes WHERE topic_id = %s AND user_id = %s", (topic_id, user_id))
            note_rows = cursor.fetchall()
            notes_text = " ".join([f"{n['title']}: {n['content']}" for n in note_rows])

            cursor.execute("SELECT title, formula_latex FROM formulas WHERE topic_id = %s AND user_id = %s", (topic_id, user_id))
            form_rows = cursor.fetchall()
            formulas_text = ", ".join([f"{f['title']} (${f['formula_latex']}$)" for f in form_rows])

            t_name = row["topic_name"]
            c_name = row["chapter_name"]
            s_name = row["subject_name"]

            prompt_text = f"Explain the core principles of **{t_name}** ({c_name}) as if teaching a classmate. Describe the underlying mechanisms, key formulas/laws, and common problem-solving rules without looking at your notes."

            rubric_points = [
                f"Accurate formal definition and physical/theoretical significance of {t_name}",
                f"Key governing laws, statements, formulas, or chemical reactions",
                f"Essential assumptions, conditions, and sign conventions",
                f"Real-world application or sample numerical setup",
                f"Common pitfalls and misconceptions to avoid"
            ]

            return {
                "topic_id": topic_id,
                "topic_name": t_name,
                "chapter_name": c_name,
                "subject_name": s_name,
                "prompt_text": prompt_text,
                "rubric_points": rubric_points,
                "has_notes": bool(notes_text),
                "formulas_text": formulas_text
            }
    finally:
        conn.close()


def save_active_recall_session(user_id: int, topic_id: int, prompt_text: str,
                               user_response: str, evaluation_feedback: str = "",
                               understanding_score: int = 3, score: int = None,
                               ai_feedback: str = None) -> int:
    """
    Saves an active recall session, synchronizes topic understanding, triggers
    adaptive spaced repetition for weak scores, awards XP, and updates streak.
    """
    effective_feedback = ai_feedback if ai_feedback is not None else evaluation_feedback
    effective_score = score if score is not None else understanding_score
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO recall_responses (user_id, topic_id, prompt_text, user_response,
                                              evaluation_feedback, understanding_score)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_id, topic_id, prompt_text.strip(), user_response.strip(),
                  effective_feedback.strip(), effective_score))
            recall_id = cursor.fetchone()[0]
            conn.commit()

        # 1. Update understanding in topic_progress
        save_progress(user_id, "topic", topic_id, understanding=effective_score)

        # 2. Adaptive Spaced Repetition trigger
        if effective_score <= 2:
            # Weak recall -> review soon in 1d, 3d, 7d
            try:
                schedule_adaptive_revisions(user_id, "topic", topic_id, effective_score)
            except Exception:
                pass
        elif understanding_score >= 4:
            # Strong recall -> schedule next spaced repetition milestones
            try:
                schedule_adaptive_revisions(user_id, "topic", topic_id, understanding_score)
            except Exception:
                pass

        # 3. Award XP & update streak
        earned_xp = 35 if understanding_score >= 4 else (25 if understanding_score == 3 else 15)
        award_user_xp(user_id, "active_recall", earned_xp, f"Active Recall on Topic #{topic_id} ({understanding_score}/5 stars)")
        update_user_streak(user_id)
        st.cache_data.clear()
        return recall_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def save_recall_response(user_id: int, topic_id: int, prompt_text: str,
                         user_response: str, evaluation_feedback: str = "",
                         understanding_score: int = 3) -> int:
    """Wrapper delegating to save_active_recall_session."""
    return save_active_recall_session(user_id, topic_id, prompt_text, user_response, evaluation_feedback, understanding_score)


@st.cache_data(ttl=30, show_spinner=False)
def get_recall_history(user_id: int, topic_id: int = None, limit: int = 20) -> list:
    """Retrieves recall history, optionally filtered by topic."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                SELECT rr.*, t.name as topic_name, c.name as chapter_name,
                       s.name as subject_name, s.color as subject_color
                FROM recall_responses rr
                JOIN topics t ON rr.topic_id = t.id
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                WHERE rr.user_id = %s
            """
            params = [user_id]
            if topic_id:
                query += " AND rr.topic_id = %s"
                params.append(topic_id)
            query += " ORDER BY rr.created_at DESC LIMIT %s"
            params.append(limit)
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


@st.cache_data(ttl=30, show_spinner=False)
def get_recall_stats(user_id: int) -> dict:
    """Aggregated recall statistics for a user."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_sessions,
                    COALESCE(AVG(understanding_score), 0) AS avg_score,
                    COUNT(DISTINCT topic_id) AS unique_topics,
                    COUNT(CASE WHEN understanding_score >= 4 THEN 1 END) AS strong_recalls,
                    COUNT(CASE WHEN understanding_score <= 2 THEN 1 END) AS weak_recalls
                FROM recall_responses
                WHERE user_id = %s
            """, (user_id,))
            row = cursor.fetchone()
            return {
                "total_sessions": row[0] or 0,
                "avg_score": round(float(row[1]), 1) if row[1] else 0,
                "unique_topics": row[2] or 0,
                "strong_recalls": row[3] or 0,
                "weak_recalls": row[4] or 0
            }
    finally:
        conn.close()


# ══════════════════════════════════════════════
# COMPREHENSIVE FOCUS MODE & ANALYTICS
# ══════════════════════════════════════════════

def log_focus_session_and_sync(user_id: int, duration_minutes: int, subject_id: int = None,
                               chapter_id: int = None, topic_id: int = None, notes: str = "",
                               update_topic_status: str = None, planner_task_id: int = None) -> int:
    """
    Logs a deep focus study session, optionally updates linked topic progress or planner task,
    awards XP (+2 XP per minute, +50 XP bonus for >= 50m), and updates streak.
    """
    import datetime
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    session_id = add_study_session(
        user_id=user_id,
        subject_id=subject_id,
        duration_minutes=duration_minutes,
        session_date=today_str,
        notes=notes,
        chapter_id=chapter_id,
        topic_id=topic_id
    )

    # 1. If topic status update requested
    if topic_id and update_topic_status:
        try:
            save_progress(user_id, "topic", topic_id, status=update_topic_status)
        except Exception:
            pass

    # 2. If planner task completed
    if planner_task_id:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE daily_plans SET is_completed = 1 WHERE id = %s AND user_id = %s", (planner_task_id, user_id))
                conn.commit()
        finally:
            conn.close()

    # 3. Calculate and award XP
    base_xp = duration_minutes * 2
    bonus_xp = 50 if duration_minutes >= 50 else 0
    total_xp = base_xp + bonus_xp
    award_user_xp(user_id, "focus_session", total_xp, f"Completed {duration_minutes}m Deep Focus (+{total_xp} XP)")
    update_user_streak(user_id)
    st.cache_data.clear()
    return session_id


@st.cache_data(ttl=30, show_spinner=False)
def get_focus_analytics(user_id: int, days: int = None) -> dict:
    """Comprehensive focus session analytics: totals, weekly breakdown, subject distribution."""
    import datetime
    today = datetime.date.today()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Totals
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_sessions,
                    COALESCE(SUM(duration_minutes), 0) AS total_minutes,
                    COALESCE(AVG(duration_minutes), 0) AS avg_duration
                FROM study_sessions WHERE user_id = %s
            """, (user_id,))
            totals = cursor.fetchone()

            # This week
            week_start = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COALESCE(SUM(duration_minutes), 0) AS week_minutes,
                       COUNT(*) AS week_sessions
                FROM study_sessions
                WHERE user_id = %s AND session_date >= %s
            """, (user_id, week_start))
            week_row = cursor.fetchone()

            # Subject distribution
            cursor.execute("""
                SELECT s.name, s.color, COALESCE(SUM(ss.duration_minutes), 0) AS minutes
                FROM study_sessions ss
                JOIN subjects s ON ss.subject_id = s.id
                WHERE ss.user_id = %s
                GROUP BY s.name, s.color
                ORDER BY minutes DESC
            """, (user_id,))
            subj_dist = [dict(r) for r in cursor.fetchall()]

            # Daily breakdown for last 14 days
            two_weeks_ago = (today - datetime.timedelta(days=13)).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT session_date, SUM(duration_minutes) AS minutes
                FROM study_sessions
                WHERE user_id = %s AND session_date >= %s
                GROUP BY session_date ORDER BY session_date ASC
            """, (user_id, two_weeks_ago))
            daily_rows = cursor.fetchall()
            daily_data = {r["session_date"]: r["minutes"] for r in daily_rows}
            daily_trend = []
            for i in range(14):
                d = today - datetime.timedelta(days=13 - i)
                ds = d.strftime("%Y-%m-%d")
                daily_trend.append({
                    "date": ds,
                    "day_label": d.strftime("%a %d"),
                    "minutes": daily_data.get(ds, 0)
                })

            # Focus streak
            cursor.execute("""
                SELECT DISTINCT session_date FROM study_sessions
                WHERE user_id = %s ORDER BY session_date DESC
            """, (user_id,))
            all_dates = [r["session_date"] for r in cursor.fetchall()]
            focus_streak = 0
            check_date = today
            for _ in range(365):
                if check_date.strftime("%Y-%m-%d") in all_dates:
                    focus_streak += 1
                    check_date -= datetime.timedelta(days=1)
                else:
                    break

            return {
                "total_sessions": totals["total_sessions"] or 0,
                "total_minutes": totals["total_minutes"] or 0,
                "total_hours": round((totals["total_minutes"] or 0) / 60, 1),
                "avg_duration": round(float(totals["avg_duration"] or 0), 0),
                "week_minutes": week_row["week_minutes"] or 0,
                "week_sessions": week_row["week_sessions"] or 0,
                "subject_distribution": subj_dist,
                "daily_trend": daily_trend,
                "focus_streak": focus_streak
            }
    finally:
        conn.close()


log_focus_session = log_focus_session_and_sync
get_all_quizzes = get_quiz_history


def get_recent_activity_stream(user_id: int, limit: int = 6) -> list:
    """Fetches a unified chronologically ordered stream of recent study activity."""
    conn = get_connection()
    try:
        activities = []
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 1. Recent Quizzes
            cursor.execute("""
                SELECT qa.id, q.title, qa.score, qa.total_questions, qa.created_at, s.name as subject_name, s.color as subject_color
                FROM quiz_attempts qa
                JOIN quizzes q ON qa.quiz_id = q.id
                LEFT JOIN subjects s ON q.subject_id = s.id
                WHERE qa.user_id = %s
                ORDER BY qa.created_at DESC LIMIT %s
            """, (user_id, limit))
            for r in cursor.fetchall():
                pct = round((r["score"] / r["total_questions"] * 100)) if r["total_questions"] else 0
                activities.append({
                    "type": "quiz",
                    "icon": "🎯",
                    "title": f"Completed Quiz: {r['title']}",
                    "subtitle": f"{r['score']}/{r['total_questions']} correct ({pct}%) • {r['subject_name'] or 'General'}",
                    "timestamp": str(r["created_at"])[:16],
                    "raw_time": str(r["created_at"]),
                    "tag": f"{pct}% Accuracy",
                    "tag_color": "#22C55E" if pct >= 75 else ("#38BDF8" if pct >= 50 else "#EF4444")
                })

            # 2. Recent Focus Sessions
            cursor.execute("""
                SELECT ss.id, ss.duration_minutes, ss.notes, ss.created_at, ss.session_date, s.name as subject_name, t.name as topic_name
                FROM study_sessions ss
                LEFT JOIN subjects s ON ss.subject_id = s.id
                LEFT JOIN topics t ON ss.topic_id = t.id
                WHERE ss.user_id = %s
                ORDER BY ss.created_at DESC LIMIT %s
            """, (user_id, limit))
            for r in cursor.fetchall():
                topic_str = f"on {r['topic_name']}" if r["topic_name"] else ""
                activities.append({
                    "type": "focus",
                    "icon": "⏱️",
                    "title": f"Focus Session: {r['duration_minutes']} min {topic_str}",
                    "subtitle": f"{r['subject_name'] or 'Focused Study'} • {r['session_date']}",
                    "timestamp": str(r["created_at"])[:16],
                    "raw_time": str(r["created_at"]),
                    "tag": f"{r['duration_minutes']}m Deep Work",
                    "tag_color": "#38BDF8"
                })

            # 3. Recent Completed Revisions
            cursor.execute("""
                SELECT r.id, r.completed_at, t.name as topic_name, s.name as subject_name
                FROM revisions r
                JOIN topics t ON r.item_id = t.id AND r.item_type = 'topic'
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                WHERE r.user_id = %s AND r.is_completed = 1
                ORDER BY r.completed_at DESC LIMIT %s
            """, (user_id, limit))
            for r in cursor.fetchall():
                activities.append({
                    "type": "revision",
                    "icon": "🧠",
                    "title": f"Spaced Revision: {r['topic_name']}",
                    "subtitle": f"{r['subject_name']} • Retention reinforced",
                    "timestamp": str(r["completed_at"])[:16],
                    "raw_time": str(r["completed_at"]),
                    "tag": "+50 XP",
                    "tag_color": "#A855F7"
                })

        activities.sort(key=lambda x: x.get("raw_time", ""), reverse=True)
        return activities[:limit]
    finally:
        conn.close()


def get_weak_areas(user_id: int, limit: int = 5) -> list:
    """Identifies topics requiring urgent remediation based on understanding level, difficult flags, and mistake counts."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT t.id, t.name as topic_name, c.name as chapter_name, s.name as subject_name, s.color as subject_color,
                       COALESCE(p.understanding, 3) as understanding,
                       COALESCE(p.is_difficult, 0) as is_difficult,
                       COALESCE(p.needs_practice, 0) as needs_practice,
                       (SELECT COUNT(*) FROM mistakes m WHERE m.topic_id = t.id AND m.user_id = %s AND m.is_reviewed = 0) as mistake_count
                FROM topics t
                JOIN chapters c ON t.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                LEFT JOIN topic_progress p ON p.item_id = t.id AND p.item_type = 'topic' AND p.user_id = %s
                WHERE s.user_id = %s AND (COALESCE(p.understanding, 3) <= 2 OR COALESCE(p.is_difficult, 0) = 1 OR (SELECT COUNT(*) FROM mistakes m WHERE m.topic_id = t.id AND m.user_id = %s AND m.is_reviewed = 0) > 0)
                ORDER BY mistake_count DESC, COALESCE(p.understanding, 3) ASC, COALESCE(p.is_difficult, 0) DESC
                LIMIT %s
            """, (user_id, user_id, user_id, user_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


