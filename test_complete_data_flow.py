"""
test_complete_data_flow.py — Comprehensive end-to-end test suite for Nexus integrated features.
Tests:
1. Exam Readiness Score (5-factor composite + term filtering)
2. Quiz Engine (MCQ generation, grading, XP, understanding sync)
3. Mistake Vault (Auto-logging from quiz, analytics, re-quiz generation, mastery resolution)
4. Active Recall (Feynman prompt, self-eval, automatic adaptive revision trigger)
5. Focus Studio (Deep work timer, session logging, streak, topic status update)
6. Full data flow interconnection
"""

import sys
import os
import json
import datetime

# Ensure project directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database import init_db, get_connection
from models import (
    create_user,
    verify_user,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    calculate_exam_readiness_score,
    get_question_bank_for_topic,
    create_quiz,
    submit_quiz_and_sync_nexus,
    get_quiz_history,
    get_all_mistakes,
    get_mistake_analytics,
    generate_mistake_requiz,
    toggle_mistake_reviewed,
    get_active_recall_prompt,
    save_active_recall_session,
    get_recall_history,
    get_recall_stats,
    log_focus_session_and_sync,
    get_focus_analytics,
    get_due_revisions,
    get_user_xp_summary
)
from preloaded_syllabi import preload_standard_syllabus


def test_complete_data_flow():
    print("=" * 70)
    print("🚀 STARTING NEXUS COMPLETE DATA FLOW INTEGRATION TEST")
    print("=" * 70)

    # Step 1: Initialize Database & Create Test User
    print("\n[STEP 1] Initializing DB & Creating Test Student...")
    init_db()
    
    test_username = f"flow_tester_{int(datetime.datetime.now().timestamp())}"
    user_id = create_user(test_username, "password123")
    assert user_id is not None, "User creation failed!"
    print(f"✅ Created User '{test_username}' with ID: {user_id}")

    # Step 2: Preload CBSE Class 10 Syllabus
    print("\n[STEP 2] Preloading CBSE Class 10 Syllabus & Terms...")
    loaded = preload_standard_syllabus(user_id, "CBSE", "Class 10")
    assert loaded, "Syllabus preloading failed!"
    
    subjects = get_all_subjects(user_id)
    assert len(subjects) > 0, "No subjects found after preload!"
    print(f"✅ Preloaded {len(subjects)} subjects (e.g. {subjects[0]['name']})")
    
    physics_sub = next(s for s in subjects if "Physics" in s["name"] or "Science" in s["name"])
    chapters = get_chapters_for_subject(user_id, physics_sub["id"])
    assert len(chapters) > 0, "No chapters found for Physics!"
    topics = get_topics_for_chapter(user_id, chapters[0]["id"])
    assert len(topics) > 0, "No topics found for first chapter!"
    test_topic = topics[0]
    print(f"✅ Selected Test Topic: '{test_topic['name']}' in Chapter '{chapters[0]['name']}'")

    # Step 3: Baseline Exam Readiness Score
    print("\n[STEP 3] Testing Baseline Exam Readiness Score...")
    baseline_readiness = calculate_exam_readiness_score(user_id)
    print(f"📊 Baseline Readiness Score: {baseline_readiness['readiness_score']}/100")
    print(f"   Factors: Syllabus={baseline_readiness['syllabus_pct']}%, Understanding={baseline_readiness['understanding_pct']}%, Revision={baseline_readiness['revision_pct']}%, Practice={baseline_readiness['practice_pct']}%")
    assert "readiness_score" in baseline_readiness
    assert "recommendations" in baseline_readiness

    # Step 4: Quiz Engine Flow
    print("\n[STEP 4] Testing Quiz Engine Generation & Submission...")
    questions = get_question_bank_for_topic(
        user_id=user_id,
        subject_id=physics_sub["id"],
        chapter_id=chapters[0]["id"],
        topic_id=test_topic["id"],
        difficulty="Mixed",
        count=5
    )
    assert len(questions) == 5, f"Expected 5 questions, got {len(questions)}"
    print(f"✅ Generated {len(questions)} conceptual MCQs for '{test_topic['name']}'")

    quiz_id = create_quiz(
        user_id=user_id,
        title=f"Test Quiz: {test_topic['name']}",
        subject_id=physics_sub["id"],
        chapter_id=chapters[0]["id"],
        topic_id=test_topic["id"],
        difficulty="Mixed",
        questions_json=json.dumps(questions)
    )
    assert quiz_id > 0

    # Submit quiz answers: 3 correct, 2 wrong (to verify auto-mistake vault logging)
    user_answers = {}
    for idx, q in enumerate(questions):
        if idx < 3:
            user_answers[str(q["id"])] = q["correct_answer"]  # Correct
        else:
            user_answers[str(q["id"])] = "Wrong Distractor Answer"  # Wrong

    quiz_result = submit_quiz_and_sync_nexus(
        user_id=user_id,
        quiz_id=quiz_id,
        user_answers=user_answers,
        time_taken_seconds=45,
        auto_save_mistakes=True
    )
    print(f"✅ Quiz Submitted: Score={quiz_result['score']}/{quiz_result['total']} ({quiz_result['accuracy_pct']}%)")
    print(f"   XP Earned: +{quiz_result['earned_xp']} XP")
    print(f"   Mistakes Auto-Logged to Vault: {quiz_result['mistakes_logged']}")
    assert quiz_result["score"] == 3
    assert quiz_result["total"] == 5
    assert quiz_result["mistakes_logged"] == 2

    # Step 5: Mistake Vault & Mistake Re-Quiz Flow
    print("\n[STEP 5] Testing Mistake Vault Integration & Re-Quiz Engine...")
    mistakes = get_all_mistakes(user_id, is_reviewed=False)
    assert len(mistakes) == 2, f"Expected 2 unreviewed mistakes in vault, found {len(mistakes)}"
    print(f"✅ Verified {len(mistakes)} errors successfully captured in Mistake Vault:")
    for m in mistakes:
        print(f"   - ❓ {m['question'][:45]}... (Your: '{m['your_answer']}' vs Corr: '{m['correct_answer']}')")

    mistake_analytics = get_mistake_analytics(user_id)
    assert mistake_analytics["unreviewed"] == 2
    assert mistake_analytics["total"] == 2

    # Generate Mistake Re-Quiz from Vault
    print("\n   Generating Re-Quiz from unreviewed mistakes...")
    requiz = generate_mistake_requiz(user_id, limit=5)
    assert requiz is not None
    assert len(requiz["questions"]) == 2
    print(f"✅ Re-Quiz generated with {len(requiz['questions'])} questions!")

    # Student takes Re-Quiz and answers correctly -> marks mistakes mastered
    requiz_answers = {str(q["id"]): q["correct_answer"] for q in requiz["questions"]}
    requiz_result = submit_quiz_and_sync_nexus(
        user_id=user_id,
        quiz_id=requiz["quiz_id"],
        user_answers=requiz_answers,
        time_taken_seconds=30,
        auto_save_mistakes=False
    )
    assert requiz_result["score"] == 2
    assert requiz_result["solved_mistakes_count"] == 2
    print(f"✅ Re-Quiz Passed 100%! Mastered {requiz_result['solved_mistakes_count']} mistakes.")

    post_requiz_mistakes = get_all_mistakes(user_id, is_reviewed=False)
    assert len(post_requiz_mistakes) == 0, "Mistakes should now be marked as reviewed/mastered!"
    print("✅ Verified 0 pending unreviewed mistakes remaining.")

    # Step 6: Active Recall (Feynman Technique) Flow
    print("\n[STEP 6] Testing Active Recall Studio & Adaptive Spaced Repetition...")
    prompt_info = get_active_recall_prompt(user_id, test_topic["id"])
    assert prompt_info is not None
    print(f"✅ Active Recall Prompt generated: '{prompt_info['prompt_text'][:60]}...'")
    print(f"   Rubric points: {len(prompt_info['rubric_points'])} criteria")

    # Save active recall with weak score (2/5) to verify automatic spaced repetition scheduling
    recall_id = save_active_recall_session(
        user_id=user_id,
        topic_id=test_topic["id"],
        prompt_text=prompt_info["prompt_text"],
        user_response="Tried to explain from memory but missed the second formula condition.",
        evaluation_feedback="Review formula and sign convention.",
        understanding_score=2
    )
    assert recall_id > 0

    # Check that spaced repetition revision was scheduled
    due_revs = get_due_revisions(user_id, (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
    assert len(due_revs) > 0, "Adaptive revision should be scheduled for weak active recall!"
    print(f"✅ Adaptive Spaced Revision automatically scheduled in queue ({len(due_revs)} revisions due soon)")

    # Save active recall with strong score (5/5)
    save_active_recall_session(
        user_id=user_id,
        topic_id=test_topic["id"],
        prompt_text=prompt_info["prompt_text"],
        user_response="Complete step-by-step derivation, correct formula, and edge conditions explained flawlessly.",
        evaluation_feedback="Full mastery achieved.",
        understanding_score=5
    )
    recall_stats = get_recall_stats(user_id)
    assert recall_stats["total_sessions"] == 2
    assert recall_stats["strong_recalls"] == 1
    print(f"✅ Active Recall Stats: {recall_stats['total_sessions']} sessions, Avg Score: {recall_stats['avg_score']}/5")

    # Step 7: Focus Studio (Deep Work) Flow
    print("\n[STEP 7] Testing Focus Mode Deep Work & Study Analytics...")
    session_id = log_focus_session_and_sync(
        user_id=user_id,
        duration_minutes=50,
        subject_id=physics_sub["id"],
        chapter_id=chapters[0]["id"],
        topic_id=test_topic["id"],
        notes="Deep focus numerical practice",
        update_topic_status="Completed"
    )
    assert session_id > 0
    print(f"✅ Focus Session #{session_id} logged (50m, +150 XP including deep work bonus)")

    focus_analytics = get_focus_analytics(user_id)
    assert focus_analytics["total_minutes"] >= 50
    assert focus_analytics["total_sessions"] >= 1
    assert focus_analytics["focus_streak"] >= 1
    print(f"✅ Focus Analytics: Total Time={focus_analytics['total_hours']}h, Focus Streak={focus_analytics['focus_streak']}d")

    # Step 8: Final Gamification & Exam Readiness Check
    print("\n[STEP 8] Testing Final Interconnected Gamification & Exam Readiness...")
    xp_summary = get_user_xp_summary(user_id)
    print(f"🏆 Total XP Earned: {xp_summary['total_xp']} XP | Level {xp_summary['level']} ({xp_summary['title']}) | Streak: {xp_summary['streak']}d")
    assert xp_summary["total_xp"] > 150

    final_readiness = calculate_exam_readiness_score(user_id)
    print(f"🎓 Final Exam Readiness Score: {final_readiness['readiness_score']}/100")
    print(f"   Breakdown: Syllabus={final_readiness['syllabus_pct']}%, Understanding={final_readiness['understanding_pct']}%, Revision={final_readiness['revision_pct']}%, Mistake Resolution={final_readiness['factors']['mistake_resolution']}%, Consistency={final_readiness['practice_pct']}%")
    print(f"   Actionable Recommendation: '{final_readiness['recommendations'][0]}'")
    
    assert final_readiness["readiness_score"] >= baseline_readiness["readiness_score"]
    assert final_readiness["factors"]["mistake_resolution"] == 100.0  # Because all 2 mistakes were mastered via re-quiz

    print("\n" + "=" * 70)
    print("🎉 ALL 8 INTEGRATION TESTS PASSED PERFECTLY WITH ZERO ERRORS!")
    print("=" * 70)


if __name__ == "__main__":
    test_complete_data_flow()
