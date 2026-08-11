"""
test_nexus_ai_copilot.py — Comprehensive Verification Suite for Nexus AI Pedagogical Master Tutor.
Tests all 12 mandatory pedagogical scenarios.
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
    safe_print("=" * 75)
    safe_print("RUNNING 12 MANDATORY NEXUS AI PEDAGOGICAL MASTER TUTOR TESTS")
    safe_print("=" * 75)

    init_db()

    # 1. Setup mock user & curriculum
    username = f"master_tutor_student_{os.getpid()}"
    user_id = create_user(username, "Password123!")
    if not user_id:
        u = verify_user(username, "Password123!")
        user_id = u["id"]

    safe_print(f"Test User Active: ID {user_id} ({username})")

    # Add curriculum
    s_id = add_subject(user_id, "Physics", "#38BDF8")
    c_id = add_chapter(user_id, s_id, "Optics & Light")
    t_id = add_topic(user_id, c_id, "Refraction of Light")
    save_progress(user_id, "topic", t_id, status="Not Started", understanding=2)
    safe_print(f"Seeded Syllabus Topic: Refraction of Light (ID {t_id})")

    # The 12 Mandatory Pedagogical Test Cases
    test_suite = [
        (
            "TEST 1: Detailed Long Pedagogical Masterclass on Refraction",
            "Explain refraction of light in detail.",
            lambda r: len(r["content"]) > 800 and "Snell" in r["content"] and "mud" in r["content"].lower() and "diamond" in r["content"].lower() and "Execution Error" not in r["content"]
        ),
        (
            "TEST 2: Socratic Reset & Diagnostic Question on Confusion",
            "I don't understand refraction.",
            lambda r: "lawnmower" in r["content"].lower() and "90" in r["content"] and ("Diagnostic" in r["content"] or "Socratic Reset" in str(r.get("action_badge", "")))
        ),
        (
            "TEST 3: Physical WHY Mechanism of Convex Lens Convergence",
            "Why does a convex lens converge light?",
            lambda r: "thick" in r["content"].lower() and "delay" in r["content"].lower() and "focus" in r["content"].lower()
        ),
        (
            "TEST 4: Interactive Board Numerical Request",
            "Give me a numerical on refraction.",
            lambda r: "Problem" in r["content"] and "water" in r["content"].lower() and "glass" in r["content"].lower()
        ),
        (
            "TEST 5: Calculation Mismatch Diagnostic Analysis",
            "I got 3.2 m/s but the answer says 4 m/s.",
            lambda r: "Diagnostic" in r["content"] or "Unit Conversion" in r["content"] or "Calculation" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 6: Real Action - Add to Revision Queue",
            "Add refraction to my revision queue.",
            lambda r: "Revision" in str(r.get("action_badge", "")) or "Spaced Repetition" in r["content"]
        ),
        (
            "TEST 7: Real Action - Start 25-min Physics Focus Session",
            "Start a 25 minute physics focus session.",
            lambda r: "Focus Studio" in r["content"] and "25" in r["content"]
        ),
        (
            "TEST 8: Real Action - Save Context Explanation to Notes",
            "Save this as a note.",
            lambda r: "Notes Repository" in r["content"] or "Note Saved" in str(r.get("action_badge", "")) or "Note" in str(r.get("action_badge", ""))
        ),
        (
            "TEST 9: Real Data - Weakest Topics & Progress Analysis",
            "What are my weakest topics?",
            lambda r: "Progress" in str(r.get("action_badge", "")) or "Readiness" in r["content"] or "Coverage" in r["content"]
        ),
        (
            "TEST 10: Natural Academic & Career Mentorship",
            "I want to get into MIT.",
            lambda r: "MIT" in r["content"] and "student MIT would want" in r["content"]
        ),
        (
            "TEST 11: Beginner / From Zero Teaching",
            "Explain Newton's laws like I'm completely new to physics.",
            lambda r: "cart" in r["content"].lower() and "lazy" in r["content"].lower() and "Handshake" in r["content"]
        ),
        (
            "TEST 12: Go Deeper Conceptual Layer Progression",
            "Go deeper.",
            lambda r: ("Fermat" in r["content"] or "Wavefront" in r["content"] or "Least Time" in r["content"]) and "Advanced" in str(r.get("action_badge", ""))
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
                safe_print(f"         Length: {len(res.get('content', ''))} chars")
                safe_print(f"         Snippet: {res.get('content')[:120]}...")
                failed += 1
        except Exception as e:
            safe_print(f"  [ERROR] {name} Exception: {e}")
            failed += 1

    safe_print("=" * 75)
    safe_print(f"FINAL RESULT: {passed} / {len(test_suite)} Tests Passed ({round(passed/len(test_suite)*100)}%)")
    safe_print("=" * 75)
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
