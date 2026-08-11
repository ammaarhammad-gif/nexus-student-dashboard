"""
ai_tools.py — Nexus AI Autonomous Action & Tool Execution Layer.

Provides a safe, validated, deterministic execution layer connecting natural language
intents to models.py and Nexus application state.

Exposes:
1. Tool Registry & Schema Definitions (for Cloud LLM function calling)
2. Safe Execution Dispatcher (with argument validation & entity resolution)
3. Destructive Action Confirmation Guardrails
4. Direct Application Navigation & State Controllers
"""

import json
import datetime
import re
import streamlit as st
import psycopg2.extras
from database import get_connection
from models import (
    get_user_profile,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    save_progress,
    add_daily_plan,
    get_daily_plans,
    delete_daily_plan,
    schedule_adaptive_revisions,
    get_revision_queue,
    complete_adaptive_revision,
    add_note,
    get_all_notes,
    delete_note,
    add_formula,
    get_all_formulas,
    add_mistake,
    get_all_mistakes,
    toggle_mistake_reviewed,
    create_quiz,
    generate_mistake_requiz,
    get_question_bank_for_topic,
    calculate_exam_readiness_score,
    get_overall_stats,
    global_nexus_search,
    set_user_theme,
    set_user_wallpaper_config,
    get_user_wallpaper_config
)
from styles import WALLPAPER_PRESETS


# ══════════════════════════════════════════════════════════
# FUZZY ENTITY RESOLVER FOR SUBJECTS, CHAPTERS & TOPICS
# ══════════════════════════════════════════════════════════

def resolve_subject_by_name(user_id: int, name_query: str) -> dict:
    """Fuzzy-matches a subject name or keyword to a subject record."""
    if not name_query:
        return None
    subjects = get_all_subjects(user_id)
    if not subjects:
        return None
    q = name_query.lower().strip()
    
    # Exact match
    for s in subjects:
        if s["name"].lower() == q:
            return s
            
    # Substring match
    for s in subjects:
        if q in s["name"].lower() or s["name"].lower() in q:
            return s
            
    # Keyword heuristics (e.g. "bio" -> "Biology", "maths" -> "Mathematics", "phys" -> "Physics")
    aliases = {
        "math": "Mathematics", "maths": "Mathematics", "algebra": "Mathematics", "geometry": "Mathematics",
        "phys": "Physics", "physics": "Physics", "mechanics": "Physics",
        "chem": "Chemistry", "chemistry": "Chemistry",
        "bio": "Biology", "biology": "Biology", "botany": "Biology", "zoology": "Biology",
        "eng": "English", "english": "English", "grammar": "English", "literature": "English",
        "hist": "History", "history": "History", "civics": "Civics", "geo": "Geography",
        "geography": "Geography", "cs": "Computer Science", "computer": "Computer Science"
    }
    for alias, canonical in aliases.items():
        if alias in q:
            for s in subjects:
                if canonical.lower() in s["name"].lower():
                    return s
                    
    return subjects[0] if len(subjects) == 1 else None


def _normalize_tokens(text: str) -> set:
    """Helper to extract normalized, punctuation-free stemmed tokens."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = set()
    for w in cleaned.split():
        if w in ["chapter", "topic", "on", "about", "the", "concept", "of", "in", "and", "as", "for", "to", "my"]:
            continue
        tokens.add(w)
        # Add basic stemmed forms (remove trailing 's', 'es')
        if len(w) > 4 and w.endswith("es"):
            tokens.add(w[:-2])
        elif len(w) > 3 and w.endswith("s"):
            tokens.add(w[:-1])
    return tokens


def resolve_topic_by_name(user_id: int, topic_query: str, subject_hint: str = None) -> dict:
    """Fuzzy-matches a topic name to a topic record with subject & chapter details."""
    if not topic_query:
        return None
    q = topic_query.lower().strip()
    # Strip common noise words
    noise = ["chapter", "topic", "on", "about", "the", "concept", "of", "in", "my", "as", "teach", "me", "explain"]
    clean_q = " ".join([w for w in q.split() if w not in noise]) or q

    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT t.id as topic_id, t.name as topic_name,
                           COALESCE(tp.understanding, 3) as understanding,
                           COALESCE(tp.status, 'Not Started') as status,
                           c.id as chapter_id, c.name as chapter_name,
                           s.id as subject_id, s.name as subject_name
                    FROM topics t
                    JOIN chapters c ON t.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    LEFT JOIN topic_progress tp ON tp.item_id = t.id AND tp.item_type = 'topic' AND tp.user_id = t.user_id
                    WHERE t.user_id = %s
                """, (user_id,))
                rows = cursor.fetchall()
                if not rows:
                    return None

                # 1. Exact match on topic name
                for r in rows:
                    if r["topic_name"].lower() == q or r["topic_name"].lower() == clean_q:
                        return dict(r)

                # 2. Substring match on topic name
                for r in rows:
                    if clean_q in r["topic_name"].lower() or r["topic_name"].lower() in clean_q:
                        if not subject_hint or subject_hint.lower() in r["subject_name"].lower():
                            return dict(r)

                # 3. Match against chapter name
                for r in rows:
                    if clean_q in r["chapter_name"].lower() or r["chapter_name"].lower() in clean_q:
                        return dict(r)

                # 4. Normalized token overlap (handles plurals, punctuation, possessives)
                q_tokens = _normalize_tokens(clean_q)
                best_match = None
                max_overlap = 0
                for r in rows:
                    t_tokens = _normalize_tokens(r["topic_name"]) | _normalize_tokens(r["chapter_name"])
                    overlap = len(q_tokens & t_tokens)
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_match = dict(r)
                if max_overlap >= 1:
                    return best_match

                return None
        finally:
            conn.close()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error resolving topic '{topic_query}' for user {user_id}: {e}")
        return None


# ══════════════════════════════════════════════════════════
# NEXUS WORKSPACE TOOLS (20+ Deterministic Actions)
# ══════════════════════════════════════════════════════════

def tool_get_student_profile(user_id: int) -> dict:
    """Returns the student's name, class, board, and academic year."""
    p = get_user_profile(user_id)
    return {
        "success": True,
        "name": p.get("name", "Student"),
        "class": p.get("class_name", "Class 10"),
        "board": p.get("board", "CBSE"),
        "academic_year": p.get("academic_year", "")
    }


def tool_get_syllabus_overview(user_id: int) -> dict:
    """Returns overall curriculum coverage statistics and per-subject breakdown."""
    stats = get_overall_stats(user_id)
    subjects = get_all_subjects(user_id)
    return {
        "success": True,
        "total_topics": stats.get("total_topics", 0),
        "completed_topics": stats.get("completed_topics", 0),
        "percent_completed": stats.get("percent_completed", 0),
        "subjects": [s["name"] for s in subjects]
    }


def tool_get_topic_details(user_id: int, topic_name: str) -> dict:
    """Retrieves full details, subject, chapter, and understanding level for a topic."""
    topic = resolve_topic_by_name(user_id, topic_name)
    if not topic:
        return {"success": False, "error": f"Topic '{topic_name}' not found in syllabus."}
    return {
        "success": True,
        "topic_id": topic["topic_id"],
        "topic_name": topic["topic_name"],
        "chapter_name": topic["chapter_name"],
        "subject_name": topic["subject_name"],
        "understanding_rating": topic.get("understanding", 3)
    }


def tool_update_topic_status(user_id: int, topic_name: str, status: str = "Completed") -> dict:
    """Marks a topic as 'Not Started', 'In Progress', 'Completed', or 'Revision Done'."""
    topic = resolve_topic_by_name(user_id, topic_name)
    if not topic:
        return {"success": False, "error": f"Could not find topic '{topic_name}' in syllabus to update."}
    
    valid_statuses = ["Not Started", "In Progress", "Completed", "Revision Done"]
    target_status = status
    for vs in valid_statuses:
        if status.lower() in vs.lower():
            target_status = vs
            break

    save_progress(user_id, "topic", topic["topic_id"], status=target_status)
    return {
        "success": True,
        "message": f"Marked '{topic['topic_name']}' ({topic['subject_name']}) as {target_status}.",
        "topic_name": topic["topic_name"],
        "subject_name": topic["subject_name"],
        "new_status": target_status
    }


def tool_update_topic_confidence(user_id: int, topic_name: str, rating: int) -> dict:
    """Updates understanding rating (1 to 5 stars) for a topic."""
    topic = resolve_topic_by_name(user_id, topic_name)
    if not topic:
        return {"success": False, "error": f"Could not find topic '{topic_name}' in syllabus."}
    
    try:
        r = max(1, min(5, int(rating)))
    except Exception:
        r = 3

    save_progress(user_id, "topic", topic["topic_id"], understanding=r)
    return {
        "success": True,
        "message": f"Updated understanding confidence for '{topic['topic_name']}' to {r}/5 stars.",
        "topic_name": topic["topic_name"],
        "rating": r
    }


def tool_create_study_task(user_id: int, task_description: str, plan_date: str = None, duration_minutes: int = 45, subject_name: str = None) -> dict:
    """Adds a scheduled study task to the student's Daily Study Planner."""
    if not task_description:
        return {"success": False, "error": "Task description cannot be empty."}
    
    # Resolve date
    target_date = datetime.date.today()
    if plan_date:
        p_lower = plan_date.lower().strip()
        if "tomorrow" in p_lower:
            target_date = datetime.date.today() + datetime.timedelta(days=1)
        elif "today" in p_lower:
            target_date = datetime.date.today()
        else:
            try:
                target_date = datetime.datetime.strptime(plan_date, "%Y-%m-%d").date()
            except Exception:
                target_date = datetime.date.today()

    date_str = target_date.strftime("%Y-%m-%d")
    
    # Resolve subject
    subj_id = None
    if subject_name:
        subj = resolve_subject_by_name(user_id, subject_name)
        if subj:
            subj_id = subj["id"]

    try:
        dur = max(10, min(240, int(duration_minutes or 45)))
    except Exception:
        dur = 45

    add_daily_plan(
        user_id=user_id,
        plan_date=date_str,
        description=task_description,
        duration_minutes=dur,
        subject_id=subj_id
    )

    day_label = "today" if target_date == datetime.date.today() else ("tomorrow" if target_date == datetime.date.today() + datetime.timedelta(days=1) else date_str)
    return {
        "success": True,
        "message": f"Scheduled '{task_description}' ({dur} min) for {day_label} ({date_str}).",
        "task": task_description,
        "date": date_str,
        "duration_minutes": dur
    }


def tool_delete_study_task(user_id: int, task_query: str) -> dict:
    """Deletes or removes a task from the daily study planner by matching text."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    plans = get_daily_plans(user_id, today_str)
    if not plans:
        # Check tomorrow
        tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        plans = get_daily_plans(user_id, tomorrow_str)

    matched = None
    q = task_query.lower()
    for p in plans:
        desc = (p.get("description") or p.get("task", "")).lower()
        if q in desc or desc in q:
            matched = p
            break

    if not matched:
        return {"success": False, "error": f"No scheduled task matching '{task_query}' was found in upcoming plans."}

    delete_daily_plan(user_id, matched["id"])
    return {
        "success": True,
        "message": f"Removed task '{matched.get('description') or matched.get('task')}' from study plan."
    }


def tool_schedule_revision(user_id: int, topic_name: str, interval_strategy: str = "standard") -> dict:
    """Adds a topic to the Spaced Repetition Review Queue (1d, 3d, 7d, 14d)."""
    topic = resolve_topic_by_name(user_id, topic_name)
    if not topic:
        return {"success": False, "error": f"Topic '{topic_name}' not found in syllabus."}

    schedule_adaptive_revisions(user_id, "topic", topic["topic_id"], understanding=3)
    return {
        "success": True,
        "message": f"Added '{topic['topic_name']}' ({topic['subject_name']}) to the Spaced Repetition queue (1d, 3d, 7d, 14d).",
        "topic_name": topic["topic_name"],
        "subject_name": topic["subject_name"]
    }


def tool_mark_revision_complete(user_id: int, topic_name: str) -> dict:
    """Marks an active spaced repetition item as completed in the queue."""
    q = get_revision_queue(user_id)
    items = q.get("overdue", []) + q.get("due_today", []) + q.get("due_this_week", [])
    matched = None
    query = topic_name.lower()
    for item in items:
        t_name = (item.get("topic_name") or item.get("item_name", "")).lower()
        if query in t_name or t_name in query:
            matched = item
            break

    if not matched:
        return {"success": False, "error": f"No active revision for '{topic_name}' found in your queue."}

    complete_adaptive_revision(user_id, matched["id"])
    return {
        "success": True,
        "message": f"Completed spaced revision for '{matched.get('topic_name') or matched.get('item_name')}'. +50 XP awarded!"
    }


def tool_create_note(user_id: int, topic_name: str, title: str, content_markdown: str, tags: str = "AI Explanation") -> dict:
    """Saves a rich note linked to a syllabus topic in the student's Notes repository."""
    topic = resolve_topic_by_name(user_id, topic_name)
    if not topic:
        # Fallback to general subject note
        subjects = get_all_subjects(user_id)
        if not subjects:
            return {"success": False, "error": "Please set up at least one subject in Syllabus first."}
        s_id = subjects[0]["id"]
        c_id = None
        t_id = None
        t_label = "General Concept"
    else:
        s_id = topic["subject_id"]
        c_id = topic["chapter_id"]
        t_id = topic["topic_id"]
        t_label = topic["topic_name"]

    note_title = title or f"Summary: {t_label}"
    add_note(
        user_id=user_id,
        subject_id=s_id,
        chapter_id=c_id,
        topic_id=t_id,
        title=note_title,
        content=content_markdown,
        tags=tags
    )
    return {
        "success": True,
        "message": f"Saved note '{note_title}' to your Notes Repository (+25 XP).",
        "title": note_title,
        "topic_name": t_label
    }


def tool_create_formula(user_id: int, topic_name: str, title: str, formula_latex: str, explanation: str = "") -> dict:
    """Adds a mathematical/scientific formula to the student's Formula Vault."""
    topic = resolve_topic_by_name(user_id, topic_name)
    topic = resolve_topic_by_name(user_id, topic_name)
    s_id = topic["subject_id"] if topic else None
    c_id = topic["chapter_id"] if topic else None
    t_id = topic["topic_id"] if topic else None

    if not s_id:
        subjects = get_all_subjects(user_id)
        if subjects:
            s_id = subjects[0]["id"]

    clean_latex = formula_latex.strip().replace("$$", "").replace("$", "")
    f_title = title or (topic["topic_name"] if topic else "Governing Equation")

    add_formula(
        user_id=user_id,
        subject_id=s_id,
        chapter_id=c_id,
        title=f_title,
        formula_latex=clean_latex,
        topic_id=t_id,
        description=explanation
    )
    return {
        "success": True,
        "message": f"Added formula '{f_title}' ($${clean_latex}$$) to your Formula Vault.",
        "title": f_title,
        "formula_latex": clean_latex
    }


def tool_create_mistake(user_id: int, question: str, your_answer: str, correct_answer: str, mistake_type: str = "Conceptual Gap", topic_name: str = None, explanation: str = "", prevention_strategy: str = "") -> dict:
    """Logs an error with its root cause into the Mistake Vault for targeted re-testing."""
    topic = resolve_topic_by_name(user_id, topic_name) if topic_name else None
    s_id = topic["subject_id"] if topic else None
    c_id = topic["chapter_id"] if topic else None
    t_id = topic["topic_id"] if topic else None

    add_mistake(
        user_id=user_id,
        question=question,
        mistake_type=mistake_type or "Conceptual Gap",
        subject_id=s_id,
        chapter_id=c_id,
        topic_id=t_id,
        your_answer=your_answer,
        correct_answer=correct_answer,
        explanation=explanation,
        prevention_strategy=prevention_strategy
    )
    return {
        "success": True,
        "message": f"Logged mistake to Vault: '{question[:50]}...' under {mistake_type} (+20 XP).",
        "question": question,
        "mistake_type": mistake_type
    }


def tool_resolve_mistake(user_id: int, mistake_query: str) -> dict:
    """Marks a logged error in the Mistake Vault as resolved/mastered."""
    mistakes = get_all_mistakes(user_id, is_reviewed=False)
    if not mistakes:
        return {"success": False, "error": "No pending unresolved mistakes found in your Mistake Vault!"}

    matched = None
    q = mistake_query.lower()
    for m in mistakes:
        if q in m["question"].lower():
            matched = m
            break

    if not matched:
        matched = mistakes[0]  # Mark latest if query is general

    toggle_mistake_reviewed(user_id, matched["id"], 1)
    return {
        "success": True,
        "message": f"Resolved mistake in Vault: '{matched['question'][:40]}...'. Marked as mastered!"
    }


def tool_generate_and_launch_quiz(user_id: int, topic_or_subject: str = None, count: int = 5, difficulty: str = "Adaptive", focus_prompt: str = "") -> dict:
    """Generates an AI quiz and configures session state for immediate play in Practice Quiz Engine."""
    topic = resolve_topic_by_name(user_id, topic_or_subject) if topic_or_subject else None
    subj = resolve_subject_by_name(user_id, topic_or_subject) if not topic and topic_or_subject else None

    s_id = topic["subject_id"] if topic else (subj["id"] if subj else None)
    c_id = topic["chapter_id"] if topic else None
    t_id = topic["topic_id"] if topic else None

    # Fallback to first subject if none specified
    if not s_id:
        subjects = get_all_subjects(user_id)
        if subjects:
            s_id = subjects[0]["id"]

    from ai_service import nexus_ai
    quiz_data = nexus_ai.generate_ai_quiz(
        user_id=user_id,
        subject_id=s_id,
        chapter_id=c_id,
        topic_id=t_id,
        difficulty=difficulty,
        count=count,
        focus_prompt=focus_prompt
    )

    new_quiz_id = create_quiz(
        user_id=user_id,
        title=quiz_data["title"],
        subject_id=quiz_data["subject_id"],
        chapter_id=quiz_data["chapter_id"],
        topic_id=quiz_data["topic_id"],
        difficulty=quiz_data["difficulty"],
        questions_json=json.dumps(quiz_data["questions"])
    )

    st.session_state["active_quiz_id"] = new_quiz_id
    st.session_state["quiz_submitted"] = False
    st.session_state["quiz_results"] = None

    return {
        "success": True,
        "message": f"Generated '{quiz_data['title']}' with {len(quiz_data['questions'])} questions. Ready to play in Practice!",
        "quiz_id": new_quiz_id,
        "title": quiz_data["title"],
        "questions_count": len(quiz_data["questions"])
    }


def tool_generate_and_launch_mistake_requiz(user_id: int, limit: int = 10) -> dict:
    """Generates an interactive Re-Quiz targeting unresolved Mistake Vault errors."""
    req = generate_mistake_requiz(user_id, limit=limit)
    if not req or not req.get("quiz_id"):
        return {"success": False, "error": "No pending unresolved mistakes in your Vault to generate a re-quiz!"}

    st.session_state["active_quiz_id"] = req["quiz_id"]
    st.session_state["quiz_submitted"] = False
    st.session_state["quiz_results"] = None

    return {
        "success": True,
        "message": f"Generated Mistake Re-Quiz targeting {req.get('question_count', 5)} errors. Ready in Practice!",
        "quiz_id": req["quiz_id"]
    }


def tool_get_exam_readiness_and_analytics(user_id: int) -> dict:
    """Computes exam readiness score, syllabus coverage velocity, and priority weak points."""
    readiness = calculate_exam_readiness_score(user_id)
    stats = get_overall_stats(user_id)
    return {
        "success": True,
        "readiness_score": readiness.get("readiness_score", 0),
        "readiness_tier": readiness.get("readiness_tier", "Building Foundation"),
        "syllabus_completion_pct": stats.get("percent_completed", 0),
        "completed_topics": stats.get("completed_topics", 0),
        "total_topics": stats.get("total_topics", 0)
    }


def tool_start_focus_session(user_id: int, subject_name: str = None, chapter_name: str = None, topic_name: str = None, duration_minutes: int = 25) -> dict:
    """Preconfigures Focus Studio for a deep work sprint and switches navigation."""
    subj = resolve_subject_by_name(user_id, subject_name) if subject_name else None
    topic = resolve_topic_by_name(user_id, topic_name) if topic_name else None

    if topic:
        st.session_state["focus_target_subject_id"] = topic["subject_id"]
        st.session_state["focus_target_chapter_id"] = topic["chapter_id"]
        st.session_state["focus_target_topic_id"] = topic["topic_id"]
    elif subj:
        st.session_state["focus_target_subject_id"] = subj["id"]

    try:
        dur = max(5, min(180, int(duration_minutes or 25)))
    except Exception:
        dur = 25

    st.session_state["focus_target_duration"] = dur
    return {
        "success": True,
        "message": f"Configured Focus Studio for a {dur}-minute deep work sprint.",
        "duration_minutes": dur,
        "subject": subj["name"] if subj else "General Study"
    }


def tool_search_nexus_workspace(user_id: int, query: str) -> dict:
    """Performs an omnipresent search across topics, notes, formulas, mistakes, and tasks."""
    if not query:
        return {"success": False, "error": "Search query cannot be empty."}
    results = global_nexus_search(user_id, query)
    total_hits = sum(len(v) for v in results.values())
    return {
        "success": True,
        "query": query,
        "total_matches": total_hits,
        "topics_found": len(results.get("topics", [])),
        "notes_found": len(results.get("notes", [])),
        "mistakes_found": len(results.get("mistakes", [])),
        "tasks_found": len(results.get("tasks", [])),
        "sample_topics": [t["topic_name"] for t in results.get("topics", [])[:3]],
        "sample_notes": [n["title"] for n in results.get("notes", [])[:3]]
    }


def tool_set_wallpaper_theme(user_id: int, theme_or_preset: str) -> dict:
    """Switches the UI theme (Light/Dark) or active 4K wallpaper preset."""
    q = theme_or_preset.lower().strip()
    if q in ["light", "light mode"]:
        set_user_theme(user_id, "Light")
        st.session_state["theme_mode"] = "Light"
        return {"success": True, "message": "Switched application theme to Light Mode."}
    elif q in ["dark", "dark mode"]:
        set_user_theme(user_id, "Dark")
        st.session_state["theme_mode"] = "Dark"
        return {"success": True, "message": "Switched application theme to Dark Mode."}

    # Match wallpaper preset
    for p in WALLPAPER_PRESETS:
        if q in p["name"].lower() or q in p["id"].lower():
            set_user_wallpaper_config(user_id, mode="preset", preset_id=p["id"], blur=0, opacity=0.35)
            st.session_state["wallpaper_preset_id"] = p["id"]
            return {"success": True, "message": f"Set active wallpaper preset to '{p['name']}'."}

    return {"success": False, "error": f"Wallpaper preset or theme '{theme_or_preset}' not recognized."}


def tool_navigate_to_page(page_name: str) -> dict:
    """Navigates the user to a specific Nexus dashboard module."""
    page_map = {
        "dashboard": "🏠 Dashboard",
        "home": "🏠 Dashboard",
        "learn": "📚 Learn",
        "syllabus": "📚 Learn",
        "notes": "📚 Learn",
        "formulas": "📚 Learn",
        "planner": "🗓️ Planner",
        "schedule": "🗓️ Planner",
        "practice": "🎯 Practice",
        "quiz": "🎯 Practice",
        "quizzes": "🎯 Practice",
        "mistake": "🎯 Practice",
        "mistakes": "🎯 Practice",
        "active recall": "🎯 Practice",
        "review": "🧠 Review",
        "revisions": "🧠 Review",
        "spaced repetition": "🧠 Review",
        "focus": "⏱️ Focus",
        "timer": "⏱️ Focus",
        "ai": "🤖 Nexus AI",
        "nexus ai": "🤖 Nexus AI",
        "analytics": "📊 Analytics",
        "statistics": "📊 Analytics",
        "search": "🔍 Search",
        "settings": "⚙️ Settings",
        "wallpaper": "⚙️ Settings"
    }

    target = None
    q = page_name.lower().strip()
    for k, v in page_map.items():
        if k in q or q in k:
            target = v
            break

    if not target:
        target = "🏠 Dashboard"

    st.session_state["current_page"] = target
    st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
    return {
        "success": True,
        "message": f"Navigating to {target}...",
        "target_page": target
    }


def tool_delete_all_notes(user_id: int, confirmed: bool = False) -> dict:
    """Destructive action: deletes all notes. Requires explicit confirmation token."""
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "action_type": "DELETE_ALL_NOTES",
            "warning": "⚠️ CAUTION: This will permanently delete ALL study notes in your repository. Type 'confirm delete all notes' to proceed."
        }

    notes = get_all_notes(user_id)
    count = len(notes)
    for n in notes:
        delete_note(user_id, n["id"])

    return {
        "success": True,
        "message": f"Permanently deleted {count} study notes from repository."
    }


# ══════════════════════════════════════════════════════════
# TOOL SCHEMA DEFINITIONS FOR CLOUD LLM TOOL CALLING
# ══════════════════════════════════════════════════════════

NEXUS_TOOL_DEFINITIONS = [
    {
        "name": "update_topic_status",
        "description": "Marks a syllabus topic as Not Started, In Progress, Completed, or Revision Done.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_name": {"type": "string", "description": "Name of the topic to update"},
                "status": {"type": "string", "enum": ["Not Started", "In Progress", "Completed", "Revision Done"], "description": "Target status"}
            },
            "required": ["topic_name", "status"]
        }
    },
    {
        "name": "update_topic_confidence",
        "description": "Updates understanding confidence rating (1 to 5 stars) for a syllabus topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_name": {"type": "string", "description": "Name of the topic"},
                "rating": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Understanding score from 1 to 5"}
            },
            "required": ["topic_name", "rating"]
        }
    },
    {
        "name": "create_study_task",
        "description": "Schedules a study session or task into the student's Daily Study Planner.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_description": {"type": "string", "description": "Description of the study task"},
                "plan_date": {"type": "string", "description": "Date to schedule (e.g. 'today', 'tomorrow', or 'YYYY-MM-DD')"},
                "duration_minutes": {"type": "integer", "description": "Allocated study duration in minutes"},
                "subject_name": {"type": "string", "description": "Optional subject name"}
            },
            "required": ["task_description"]
        }
    },
    {
        "name": "schedule_revision",
        "description": "Adds a topic to the Spaced Repetition queue for adaptive review (1d, 3d, 7d, 14d).",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_name": {"type": "string", "description": "Name of the topic to schedule"}
            },
            "required": ["topic_name"]
        }
    },
    {
        "name": "create_note",
        "description": "Saves a study note or AI explanation directly into the student's Notes repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_name": {"type": "string", "description": "Associated syllabus topic"},
                "title": {"type": "string", "description": "Title of the note"},
                "content_markdown": {"type": "string", "description": "Markdown body of the note"}
            },
            "required": ["title", "content_markdown"]
        }
    },
    {
        "name": "create_formula",
        "description": "Adds a scientific or mathematical formula to the student's Formula Vault.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_name": {"type": "string", "description": "Associated topic"},
                "title": {"type": "string", "description": "Name of the formula"},
                "formula_latex": {"type": "string", "description": "KaTeX/LaTeX formula string without surrounding dollar signs"},
                "explanation": {"type": "string", "description": "Short explanation of variables and sign rules"}
            },
            "required": ["title", "formula_latex"]
        }
    },
    {
        "name": "create_mistake",
        "description": "Logs an exam or practice error into the Mistake Vault with root-cause categorization.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question text"},
                "your_answer": {"type": "string", "description": "Student's incorrect response"},
                "correct_answer": {"type": "string", "description": "Correct solution"},
                "mistake_type": {"type": "string", "enum": ["Conceptual Gap", "Calculation Slip", "Formula Confusion", "Memory Lapse", "Careless Reading", "Time Pressure", "Application Error"]},
                "topic_name": {"type": "string", "description": "Associated topic"},
                "prevention_strategy": {"type": "string", "description": "Rule to prevent repeating this mistake"}
            },
            "required": ["question", "your_answer", "correct_answer"]
        }
    },
    {
        "name": "generate_and_launch_quiz",
        "description": "Generates a customized AI quiz on a topic or subject and launches it in Practice.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic_or_subject": {"type": "string", "description": "Target topic or subject name"},
                "count": {"type": "integer", "description": "Number of questions (e.g. 5, 10)"},
                "difficulty": {"type": "string", "enum": ["Adaptive", "Foundational", "Board Exam Hard", "Tricky & Trap-Heavy"]},
                "focus_prompt": {"type": "string", "description": "Specific focus area e.g. 'numerical problem traps'"}
            },
            "required": []
        }
    },
    {
        "name": "start_focus_session",
        "description": "Configures Focus Studio for a deep work sprint.",
        "parameters": {
            "type": "object",
            "properties": {
                "subject_name": {"type": "string", "description": "Subject to focus on"},
                "topic_name": {"type": "string", "description": "Topic to focus on"},
                "duration_minutes": {"type": "integer", "description": "Duration in minutes (e.g. 25, 50, 90)"}
            },
            "required": []
        }
    },
    {
        "name": "search_nexus_workspace",
        "description": "Searches across topics, notes, formulas, mistakes, and study tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keyword to search"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "set_wallpaper_theme",
        "description": "Sets the visual theme or 4K wallpaper preset in Nexus settings.",
        "parameters": {
            "type": "object",
            "properties": {
                "theme_or_preset": {"type": "string", "description": "Theme name ('Light', 'Dark') or wallpaper name ('Cyberpunk', 'Cosmic Nebula', etc.)"}
            },
            "required": ["theme_or_preset"]
        }
    },
    {
        "name": "navigate_to_page",
        "description": "Navigates the user to any module in Nexus dashboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_name": {"type": "string", "description": "Destination module name (Dashboard, Learn, Planner, Practice, Review, Focus, Analytics, Search, Settings)"}
            },
            "required": ["page_name"]
        }
    }
]


# ══════════════════════════════════════════════════════════
# DISPATCHER / EXECUTION ROUTER
# ══════════════════════════════════════════════════════════

TOOL_FUNCTION_MAP = {
    "get_student_profile": tool_get_student_profile,
    "get_syllabus_overview": tool_get_syllabus_overview,
    "get_topic_details": tool_get_topic_details,
    "update_topic_status": tool_update_topic_status,
    "update_topic_confidence": tool_update_topic_confidence,
    "create_study_task": tool_create_study_task,
    "delete_study_task": tool_delete_study_task,
    "schedule_revision": tool_schedule_revision,
    "mark_revision_complete": tool_mark_revision_complete,
    "create_note": tool_create_note,
    "create_formula": tool_create_formula,
    "create_mistake": tool_create_mistake,
    "resolve_mistake": tool_resolve_mistake,
    "generate_and_launch_quiz": tool_generate_and_launch_quiz,
    "generate_and_launch_mistake_requiz": tool_generate_and_launch_mistake_requiz,
    "get_exam_readiness_and_analytics": tool_get_exam_readiness_and_analytics,
    "start_focus_session": tool_start_focus_session,
    "search_nexus_workspace": tool_search_nexus_workspace,
    "set_wallpaper_theme": tool_set_wallpaper_theme,
    "navigate_to_page": tool_navigate_to_page,
    "delete_all_notes": tool_delete_all_notes
}


def execute_nexus_tool(user_id: int, tool_name: str, parameters: dict = None) -> dict:
    """Safely executes a registered Nexus tool with validated arguments."""
    if tool_name not in TOOL_FUNCTION_MAP:
        return {"success": False, "error": f"Tool '{tool_name}' is not recognized."}

    func = TOOL_FUNCTION_MAP[tool_name]
    kwargs = dict(parameters or {})
    kwargs.pop("user_id", None)

    try:
        import inspect
        sig = inspect.signature(func)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters and k != "user_id"}
        
        if "user_id" in sig.parameters:
            return func(user_id, **valid_kwargs)
        else:
            return func(**valid_kwargs)
    except Exception as e:
        return {"success": False, "error": f"Tool execution failed: {str(e)}"}
