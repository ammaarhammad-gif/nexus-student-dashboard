"""
test_nexus_ai_copilot.py — Comprehensive Automated Scenario Verification for Nexus AI Copilot.
Fully UTF-8 / ASCII safe for all Windows encodings.
"""

import os
import sys
import streamlit as st

# Setup mock session state for headless test execution
if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
    class MockSessionState(dict):
        def __getattr__(self, key):
            return self.get(key)
        def __setattr__(self, key, value):
            self[key] = value
    st.session_state = MockSessionState()

from database import init_db
from models import create_user, verify_user, add_subject, add_chapter, add_topic, save_progress
from ai_service import nexus_ai, NexusConversationSession
from ai_tools import execute_nexus_tool, resolve_topic_by_name


def safe_print(msg: str):
    """Prints message safely regardless of console encoding."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def run_tests():
    safe_print("=" * 60)
    safe_print("RUNNING NEXUS AI COPILOT 20-SCENARIO TEST SUITE")
    safe_print("=" * 60)

    init_db()

    # 1. Setup mock user & curriculum
    username = f"ai_test_student_{os.getpid()}"
    user_id = create_user(username, "Password123!")
    if not user_id:
        u = verify_user(username, "Password123!")
        user_id = u["id"]

    safe_print(f"Test User Created: ID {user_id} ({username})")

    # Add curriculum
    s_id = add_subject(user_id, "Physics", "#38BDF8")
    c_id = add_chapter(user_id, s_id, "Laws of Motion")
    t_id = add_topic(user_id, c_id, "Newton's Third Law of Motion")
    save_progress(user_id, "topic", t_id, status="Not Started", understanding=2)
    safe_print(f"Seeded Syllabus Topic: Newton's Third Law (ID {t_id})")

    test_scenarios = [
        ("1. GREETING", "hi", lambda r: "Hello" in r["content"] or "Copilot" in r["content"]),
        ("2. MIT CAREER GOAL", "I wanna get into MIT", lambda r: "MIT" in r["content"] and "Roadmap" in r["action_badge"] and "Execution Error" not in r["content"]),
        ("3. IIT GOAL", "I want to crack JEE Advanced and get into IIT", lambda r: "IIT" in r["content"] or "Roadmap" in r["action_badge"]),
        ("4. STUDY ADVICE & STRESS", "I'm struggling with physics", lambda r: "Physics" in r["content"] and "Coaching" in r["action_badge"]),
        ("5. FEYNMAN EXPLANATION", "Explain Newton's Third Law simply.", lambda r: "Newton" in r["content"] and len(r["content"]) > 300),
        ("6. MATHEMATICAL DERIVATION", "Explain it mathematically.", lambda r: "Derivation" in r["content"] or "Mathematical" in r["content"] or "Newton" in r["content"]),
        ("7. LENS FORMULA", "Teach me Lens Formula from first principles", lambda r: "Lens" in r["content"] and len(r["content"]) > 300),
        ("8. SOCRATIC MODE", "Teach me using questions.", lambda r: "Socratic" in str(r.get("action_badge", "")) or "question" in r["content"].lower()),
        ("9. QUIZ REQUEST", "Quiz me on it.", lambda r: "Quiz" in str(r.get("action_badge", "")) or "question" in r["content"].lower()),
        ("10. MISTAKE DIAGNOSTIC", "I got question 3 wrong.", lambda r: "Error" in str(r.get("action_badge", "")) or "mistake" in r["content"].lower()),
        ("11. PLANNER COMMAND", "Schedule 45 minutes of Physics tomorrow.", lambda r: "Scheduled" in str(r.get("action_badge", "")) or "45" in r["content"]),
        ("12. SYLLABUS COMMAND", "Mark Newton's Laws as completed.", lambda r: "Completed" in str(r.get("action_badge", "")) or "Syllabus" in r["content"] or "Updated" in r["content"]),
        ("13. REVISION COMMAND", "Add Newton's Laws to revision.", lambda r: "Revision" in str(r.get("action_badge", "")) or "queue" in r["content"].lower() or "Spaced" in r["content"]),
        ("14. NOTES COMMAND", "Save this explanation as a note.", lambda r: "Note" in str(r.get("action_badge", "")) or "Saved" in r["content"]),
        ("15. FOCUS STUDIO", "Start a 25 minute focus session for Physics.", lambda r: "Focus" in str(r.get("action_badge", "")) or "25" in r["content"]),
        ("16. ANALYTICS AUDIT", "How am I progressing?", lambda r: "Progress" in str(r.get("action_badge", "")) or "Readiness" in r["content"]),
        ("17. WORKSPACE SEARCH", "Find everything related to Newton.", lambda r: "Found" in str(r.get("action_badge", "")) or "match" in r["content"].lower()),
        ("18. NAVIGATION", "Open my Mistake Vault.", lambda r: "Switched Page" in str(r.get("action_badge", "")) or "Navigating" in r["content"]),
        ("19. THEME/WALLPAPER", "Set Cyberpunk wallpaper.", lambda r: "Appearance" in str(r.get("action_badge", "")) or "wallpaper" in r["content"].lower()),
        ("20. DESTRUCTIVE GUARDRAIL", "Delete all my notes.", lambda r: "Confirmation Pending" in str(r.get("action_badge", "")) or "Caution" in r["content"].lower() or "Destructive" in r["content"])
    ]

    passed = 0
    failed = 0

    for name, prompt, validator in test_scenarios:
        try:
            res = nexus_ai.process_chat_message(user_id, prompt)
            ok = validator(res)
            if ok:
                safe_print(f"  [PASS] {name}")
                passed += 1
            else:
                safe_print(f"  [FAIL] {name} validation failed: {res.get('action_badge')} | {res.get('content')[:100]}...")
                failed += 1
        except Exception as e:
            safe_print(f"  [ERROR] {name} Exception: {e}")
            failed += 1

    safe_print("=" * 60)
    safe_print(f"RESULTS: {passed} / {len(test_scenarios)} Scenarios Passed ({round(passed/len(test_scenarios)*100)}%)")
    safe_print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
