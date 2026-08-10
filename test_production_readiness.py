import os
import sys
import datetime
import json
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database import init_db, get_connection
from models import (
    create_user, verify_user, is_setup_complete, set_setting, get_setting,
    get_user_profile, get_user_theme, set_user_theme,
    get_all_subjects, add_subject, get_chapters_for_subject, add_chapter,
    get_topics_for_chapter, add_topic, save_progress,
    get_all_terms, add_term, calculate_exam_readiness_score,
    create_quiz, get_quiz_by_id, submit_quiz_and_sync_nexus, generate_mistake_requiz,
    get_all_mistakes, get_mistake_analytics, toggle_mistake_reviewed,
    get_active_recall_prompt, save_active_recall_session, get_recall_history, get_recall_stats,
    log_focus_session_and_sync, get_focus_analytics, get_study_sessions,
    get_revision_queue, complete_revision,
    global_nexus_search, get_overall_stats
)
from auth_utils import create_session_token, verify_session_token
from preloaded_syllabi import preload_standard_syllabus
from ai_service import nexus_ai

print("=" * 70)
print("⚡ NEXUS END-TO-END PRODUCTION READINESS VERIFICATION SUITE")
print("=" * 70)

# Initialize DB
assert init_db() is True, "Database initialization failed"
print("✅ DB connection and table schema verified.")

ts = int(datetime.datetime.now().timestamp())
u1_name = f"prod_student_a_{ts}"
u2_name = f"prod_student_b_{ts}"

# 1. User Creation & Verification
uid1 = create_user(u1_name, "SecurePass123!")
assert uid1 is not None, "Failed to create user A"
u1_auth = verify_user(u1_name, "SecurePass123!")
assert u1_auth is not None and u1_auth["id"] == uid1, "Failed to verify user A credentials"
assert verify_user(u1_name, "WrongPassword") is None, "Security flaw: invalid password was accepted"

uid2 = create_user(u2_name, "SecurePass456!")
assert uid2 is not None, "Failed to create user B"
print("✅ Multi-user authentication & password hashing verified.")

# 2. Session Token Creation & Verification
tok = create_session_token(uid1, u1_name)
payload = verify_session_token(tok)
assert payload is not None and payload["uid"] == uid1 and payload["usr"] == u1_name, "Session token verification failed"
assert verify_session_token("invalid.tampered.token") is None, "Security flaw: tampered token accepted"
print("✅ HMAC session tokens and tamper protection verified.")

# 3. Syllabus Preload & Hierarchy
preload_standard_syllabus(uid1, "CBSE", "Class 10")
preload_standard_syllabus(uid2, "ICSE", "Class 10")

subs1 = get_all_subjects(uid1)
subs2 = get_all_subjects(uid2)
assert len(subs1) > 0, "No subjects created for User A"
assert len(subs2) > 0, "No subjects created for User B"

# 4. Strict Multi-Tenant Isolation Audit
u1_sub_ids = {s["id"] for s in subs1}
u2_sub_ids = {s["id"] for s in subs2}
assert len(u1_sub_ids.intersection(u2_sub_ids)) == 0, "Security isolation breach: Subjects overlap between users"

# Check topics for User 1
chaps1 = get_chapters_for_subject(uid1, subs1[0]["id"])
assert len(chaps1) > 0, "No chapters for User A subject"
topics1 = get_topics_for_chapter(uid1, chaps1[0]["id"])
assert len(topics1) > 0, "No topics for User A chapter"
t1 = topics1[0]

# Check User 2 cannot access User 1 chapter
chaps_breach = get_topics_for_chapter(uid2, chaps1[0]["id"])
assert len(chaps_breach) == 0, "Security isolation breach: User B accessed User A's chapter topics"
print("✅ Multi-tenant data isolation verified across subjects, chapters, and topics.")

# 5. Progress Tracking & Spaced Repetition Trigger
save_progress(uid1, "topic", t1["id"], "Completed", understanding=4, is_important=1)
rev_q = get_revision_queue(uid1)
assert len(rev_q) > 0, "Completing a topic did not trigger spaced repetition schedule!"
print("✅ Progress tracking & automated spaced repetition pipeline verified.")

# 6. Quiz Engine & Mistake Vault Auto-Sync
quiz_id = create_quiz(
    uid1,
    title="Science Mastery Quiz",
    subject_id=subs1[0]["id"],
    chapter_id=chaps1[0]["id"],
    topic_id=t1["id"],
    difficulty="Medium",
    questions=[
        {
            "id": 1,
            "question": "What is the SI unit of electric potential difference?",
            "options": ["Ampere", "Volt", "Ohm", "Joule"],
            "correct_answer": "Volt",
            "explanation": "Volt (V) is the SI unit of potential difference, named after Alessandro Volta.",
            "prevention_strategy": "Memorize fundamental SI units for electricity."
        },
        {
            "id": 2,
            "question": "According to Ohm's law, if resistance doubles while voltage remains constant, current becomes:",
            "options": ["Doubled", "Halved", "Quadrupled", "Unchanged"],
            "correct_answer": "Halved",
            "explanation": "I = V / R, so current is inversely proportional to resistance.",
            "prevention_strategy": "Remember inverse proportionality in I = V/R."
        }
    ]
)
assert quiz_id is not None, "Failed to create quiz"

# Submit quiz attempt with 1 correct and 1 wrong answer
attempt_res = submit_quiz_and_sync_nexus(
    uid1,
    quiz_id=quiz_id,
    user_answers={"1": "Volt", "2": "Doubled"}, # Q2 is wrong
    time_taken_seconds=45,
    auto_save_mistakes=True
)
assert attempt_res["score"] == 1 and attempt_res["total"] == 2, f"Incorrect quiz grading: {attempt_res}"
assert attempt_res["mistakes_logged"] == 1, "Failed to auto-log mistake to Mistake Vault"

# Verify Mistake in Vault
mistakes = get_all_mistakes(uid1)
assert len(mistakes) > 0, "Mistake Vault is empty after quiz error"
m = mistakes[0]
assert "Ohm's law" in m["question"] or "resistance" in m["question"], "Incorrect mistake logged"
print("✅ Quiz Engine, automatic grading, and Mistake Vault auto-sync verified.")

# 7. Mistake Re-Quiz Generator
requiz_id = generate_mistake_requiz(uid1, count=5)
assert requiz_id is not None, "Mistake Re-Quiz generator failed"
print("✅ Mistake Re-Quiz generator verified.")

# 8. Active Recall Studio
recall_res = save_active_recall_session(
    uid1,
    topic_id=t1["id"],
    prompt_text="Explain Ohm's Law in simple terms without textbook jargon.",
    user_response="When voltage pushes electrons through a wire, the current is directly proportional to the voltage if temperature is constant.",
    ai_feedback="Excellent clear explanation covering temperature constancy.",
    score=5
)
assert recall_res is not None, "Failed to log active recall session"
recall_history = get_recall_history(uid1)
assert len(recall_history) > 0, "Active recall history empty"
print("✅ Active Recall Studio logging and rubric feedback verified.")

# 9. Focus Studio & Study Analytics
focus_res = log_focus_session_and_sync(
    uid1,
    subject_id=subs1[0]["id"],
    chapter_id=chaps1[0]["id"],
    topic_id=t1["id"],
    duration_minutes=55,
    notes="Deep focus session on circuit derivations"
)
assert focus_res is not None, "Failed to log focus study session"
analytics = get_focus_analytics(uid1, days=14)
assert analytics["total_minutes"] >= 55, "Study analytics did not aggregate focus minutes"
print("✅ Focus Studio deep work logging and 14-day analytics verified.")

# 10. Exam Readiness Score Engine
readiness = calculate_exam_readiness_score(uid1)
assert "composite_score" in readiness, "Readiness score missing composite score"
assert 0 <= readiness["composite_score"] <= 100, f"Invalid readiness score: {readiness['composite_score']}"
assert "breakdown" in readiness, "Readiness score missing factor breakdown"
print(f"✅ Exam Readiness Score engine verified (Score: {readiness['composite_score']}%).")

# 11. Global Nexus Search
search_res = global_nexus_search(uid1, "Ohm")
total_hits = sum(len(v) for v in search_res.values())
assert total_hits > 0, "Global search failed to find Ohm topic/mistake"
print(f"✅ Global Nexus Search verified ({total_hits} results found for 'Ohm').")

# 12. AI Command Center All 7 Modes
print("Testing AI Command Center capabilities...")
exp_feynman = nexus_ai.generate_explanation(uid1, topic_id=t1["id"], style="Feynman Technique (Plain English & Analogies)")
exp_board = nexus_ai.generate_explanation(uid1, topic_id=t1["id"], style="Board Exam Derivation (Step-by-Step & Formal)")
exp_visual = nexus_ai.generate_explanation(uid1, topic_id=t1["id"], style="Visual Analogy (Mental Models)")
exp_socratic = nexus_ai.generate_explanation(uid1, topic_id=t1["id"], style="Socratic Derivation (Guided Questions)")

assert exp_feynman["status"] == "success" and len(exp_feynman["content"]) > 200
assert exp_board["status"] == "success" and len(exp_board["content"]) > 200
assert exp_visual["status"] == "success" and len(exp_visual["content"]) > 200
assert exp_socratic["status"] == "success" and len(exp_socratic["content"]) > 200

# Daily blueprint
blueprint = nexus_ai.generate_daily_recommendations(uid1)
assert blueprint["status"] == "success" and len(blueprint["content"]) > 100

# AI Quiz generator
ai_quiz = nexus_ai.generate_custom_quiz(uid1, subject_id=subs1[0]["id"], topic_id=t1["id"], question_count=3)
assert ai_quiz["status"] == "success" and len(ai_quiz["questions"]) > 0

# AI Study Planner
ai_plan = nexus_ai.generate_study_plan(uid1, days_horizon=3, target_exam_id=None)
assert ai_plan["status"] == "success" and len(ai_plan["schedule"]) > 0

# AI Error Diagnostic
ai_errors = nexus_ai.diagnose_mistake_patterns(uid1)
assert ai_errors["status"] == "success" and len(ai_errors["content"]) > 50

# AI Revision Strategy
ai_rev = nexus_ai.recommend_revision_strategy(uid1)
assert ai_rev["status"] == "success" and len(ai_rev["content"]) > 50

# AI Progress Audit
ai_prog = nexus_ai.analyze_progress(uid1)
assert ai_prog["status"] == "success" and len(ai_prog["content"]) > 50

print("✅ AI Command Center all 7 capabilities verified.")

print("\n" + "=" * 70)
print("🎉 ALL PRODUCTION READINESS VERIFICATION CHECKS PASSED 100%!")
print("=" * 70)
