"""
test_nexus_ai_copilot.py — Verification for the 12 Mandatory Conversational Academic Copilot Scenarios.
Fully UTF-8 / ASCII safe for Windows consoles.
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
    safe_print("=" * 70)
    safe_print("RUNNING 12 MANDATORY NEXUS AI CONVERSATIONAL COPILOT TESTS")
    safe_print("=" * 70)

    init_db()

    # 1. Setup mock user & curriculum
    username = f"copilot_test_student_{os.getpid()}"
    user_id = create_user(username, "Password123!")
    if not user_id:
        u = verify_user(username, "Password123!")
        user_id = u["id"]

    safe_print(f"Test User Active: ID {user_id} ({username})")

    # Add curriculum
    s_id = add_subject(user_id, "Physics", "#38BDF8")
    c_id = add_chapter(user_id, s_id, "Laws of Motion")
    t_id = add_topic(user_id, c_id, "Newton's Third Law of Motion")
    save_progress(user_id, "topic", t_id, status="Not Started", understanding=2)
    safe_print(f"Seeded Syllabus Topic: Newton's Third Law (ID {t_id})")

    # The 12 Mandatory Tests in Sequential Conversational Progression
    test_suite = [
        (
            "TEST 1: MIT Career Goal Mentorship",
            "I wanna get into MIT",
            lambda r: "MIT" in r["content"] and "student MIT would want" in r["content"] and "Execution Error" not in r["content"]
        ),
        (
            "TEST 2: Concept Explanation (12-Step Tutor Flow)",
            "Explain Newton's Third Law to me",
            lambda r: "jump" in r["content"].lower() and "action" in r["content"].lower() and len(r["content"]) > 300
        ),
        (
            "TEST 3: Multi-turn Clarification (Second Part)",
            "I don't understand the second part",
            lambda r: "second part" in r["content"].lower() or "microscopic" in r["content"].lower() or "cancel" in r["content"].lower()
        ),
        (
            "TEST 4: Multi-turn Simplification (Make it easier)",
            "Make it easier",
            lambda r: "analogy" in r["content"].lower() or "plain everyday" in r["content"].lower() or "handshake" in r["content"].lower()
        ),
        (
            "TEST 5: Action - Quiz on Active Concept",
            "Quiz me on this",
            lambda r: "Quiz" in str(r.get("action_badge", "")) and "5-question" in r["content"]
        ),
        (
            "TEST 6: Action - Add Active Topic to Revision Queue",
            "Add this to my revision queue",
            lambda r: "Spaced Repetition" in r["content"] and "Revision" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 7: Action - Start 25-min Focus Session",
            "Start a 25 minute Physics focus session",
            lambda r: "Focus Studio" in r["content"] and "25" in r["content"]
        ),
        (
            "TEST 8: Data-Driven Study Recommendation",
            "What should I study today?",
            lambda r: "workspace" in r["content"].lower() and "Prioritizing" in r["content"]
        ),
        (
            "TEST 9: Action - Save Explanation to Notes Repository",
            "Save this explanation to my notes",
            lambda r: "Notes Repository" in r["content"] or "Note Saved" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 10: Mistake Diagnostic Analysis",
            "I made a mistake in question 4. Help me understand why.",
            lambda r: "Root-Cause" in r["content"] or "Sign Convention" in r["content"] or "Diagnosed" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 11: Progress Velocity & Readiness Audit",
            "How am I progressing?",
            lambda r: "Readiness" in r["content"] and "Progress" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 12: Procrastination & Mindset Reset (5-Min Rule)",
            "I've been procrastinating and don't feel like studying.",
            lambda r: "5-Minute Rule" in r["content"] and "Focus Sprint" in r["content"]
        )
    ]

    passed = 0
    failed = 0

    for name, prompt, validator in test_suite:
        try:
            res = nexus_ai.process_chat_message(user_id, prompt)
            ok = validator(res)
            if ok:
                safe_print(f"  [PASS] {name}")
                passed += 1
            else:
                safe_print(f"  [FAIL] {name}")
                safe_print(f"         Badge: {res.get('action_badge')}")
                safe_print(f"         Snippet: {res.get('content')[:120]}...")
                failed += 1
        except Exception as e:
            safe_print(f"  [ERROR] {name} Exception: {e}")
            failed += 1

    safe_print("=" * 70)
    safe_print(f"FINAL RESULT: {passed} / {len(test_suite)} Tests Passed ({round(passed/len(test_suite)*100)}%)")
    safe_print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
