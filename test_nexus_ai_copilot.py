"""
test_nexus_ai_copilot.py — Comprehensive Automated Scenario Verification for Nexus AI Copilot.
ASCII-safe output for Windows PowerShell.
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


def run_tests():
    print("=" * 60)
    print("RUNNING NEXUS AI COPILOT 16-SCENARIO TEST SUITE")
    print("=" * 60)

    init_db()

    # 1. Setup mock user & curriculum
    username = f"ai_test_student_{os.getpid()}"
    user_id = create_user(username, "Password123!")
    if not user_id:
        u = verify_user(username, "Password123!")
        user_id = u["id"]

    print(f"Test User Created: ID {user_id} ({username})")

    # Add curriculum
    s_id = add_subject(user_id, "Physics", "#38BDF8")
    c_id = add_chapter(user_id, s_id, "Laws of Motion")
    t_id = add_topic(user_id, c_id, "Newton's Third Law of Motion")
    save_progress(user_id, "topic", t_id, status="Not Started", understanding=2)
    print(f"Seeded Syllabus Topic: Newton's Third Law (ID {t_id})")

    test_scenarios = [
        ("1. EXPLANATION", "Explain Newton's Third Law simply.", lambda r: "Third Law" in r["content"] and len(r["content"]) > 300),
        ("2. DEEP", "Explain it mathematically.", lambda r: "Derivation" in r["content"] or "Mathematical" in r["content"] or "Third Law" in r["content"]),
        ("3. CONFUSION", "I still don't understand.", lambda r: len(r["content"]) > 200),
        ("4. SOCRATIC", "Teach me using questions.", lambda r: "Socratic" in r.get("action_badge", "") or "question" in r["content"].lower()),
        ("5. QUIZ", "Quiz me on it.", lambda r: "Quiz" in r.get("action_badge", "") or "question" in r["content"].lower()),
        ("6. MISTAKE", "I got question 3 wrong.", lambda r: "Error" in r.get("action_badge", "") or "mistake" in r["content"].lower()),
        ("7. PLANNER", "Schedule 45 minutes of Physics tomorrow.", lambda r: "Scheduled" in r.get("action_badge", "") or "45" in r["content"]),
        ("8. SYLLABUS", "Mark Newton's Laws as completed.", lambda r: "Completed" in r.get("action_badge", "") or "Updated" in r["content"]),
        ("9. REVISION", "Add Newton's Laws to revision.", lambda r: "Spaced Revision" in r.get("action_badge", "") or "queue" in r["content"].lower()),
        ("10. NOTES", "Save this explanation as a note.", lambda r: "Note Saved" in r.get("action_badge", "") or "Saved" in r["content"]),
        ("11. FOCUS", "Start a 25 minute focus session for Physics.", lambda r: "Focus" in r.get("action_badge", "") or "25" in r["content"]),
        ("12. ANALYTICS", "How am I progressing?", lambda r: "Progress" in r.get("action_badge", "") or "Readiness" in r["content"]),
        ("13. SEARCH", "Find everything related to Newton.", lambda r: "Found" in r.get("action_badge", "") or "match" in r["content"].lower()),
        ("14. NAVIGATION", "Open my Mistake Vault.", lambda r: "Switched Page" in r.get("action_badge", "") or "Navigating" in r["content"]),
        ("15. WALLPAPER", "Set Cyberpunk wallpaper.", lambda r: "Appearance" in r.get("action_badge", "") or "wallpaper" in r["content"].lower()),
        ("16. DESTRUCTIVE CONFIRMATION", "Delete all my notes.", lambda r: "Confirmation Pending" in r.get("action_badge", "") or "Caution" in r["content"].lower())
    ]

    passed = 0
    failed = 0

    for name, prompt, validator in test_scenarios:
        try:
            res = nexus_ai.process_chat_message(user_id, prompt)
            ok = validator(res)
            if ok:
                badge = res.get('action_badge') or 'None'
                print(f"  [PASS] {name} (Badge: {badge})")
                passed += 1
            else:
                print(f"  [FAIL] {name} validation failed\nPreview: {res['content'][:120]}...")
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {name} Exception: {e}")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} / {len(test_scenarios)} Scenarios Passed ({round(passed/len(test_scenarios)*100)}%)")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
