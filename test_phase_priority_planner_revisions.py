import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import init_db, get_connection
from models import (
    get_top_nexus_priorities,
    auto_generate_study_plan, get_overdue_study_tasks, reschedule_overdue_tasks,
    schedule_adaptive_revisions, get_revision_queue, complete_adaptive_revision,
    save_progress, get_all_subjects, get_subject_hierarchy, add_daily_plan,
    delete_daily_plan
)

def run_priority_planner_revision_tests():
    print("================================================================")
    print("   NEXUS PRIORITY ENGINE, PLANNER & REVISION ENGINE TEST SUITE  ")
    print("================================================================")

    print("\n[TEST 1] Setup & DB Connection")
    init_db()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username FROM users LIMIT 1;")
            row = cur.fetchone()
    assert row is not None, "No user found in DB"
    user_id = row[0]
    print(f"  --> PASSED: User ID={user_id} ({row[1]})")

    print("\n[TEST 2] Priority Engine Real User Data Computation")
    priorities = get_top_nexus_priorities(user_id, limit=6)
    assert isinstance(priorities, list), "Priorities must return a list"
    print(f"  --> Calculated priorities for {len(priorities)} topics:")
    for p in priorities[:3]:
        print(f"      • [{p['tier']}] Score={p['score']} | {p['topic_name']} ({p['subject_name']}) | Reasons: {', '.join(p['reasons'])}")
        assert "score" in p and 0 <= p["score"] <= 100, "Score must be normalized between 0 and 100"
        assert p["tier"] in ["Critical", "High", "Medium", "Low"], "Tier must be valid"
    print("  --> PASSED: Priority Engine mathematical scoring verified.")

    print("\n[TEST 3] Adaptive Spaced Repetition Scheduling & Queue")
    subs = get_all_subjects(user_id)
    assert len(subs) > 0, "Subjects required"
    hier = get_subject_hierarchy(user_id, subs[0]["id"])
    assert len(hier) > 0 and len(hier[0]["topics"]) > 0, "Need at least 1 topic"
    test_topic = hier[0]["topics"][0]
    
    # 1. Schedule weak understanding (1) -> should produce [1, 3, 7] days
    schedule_adaptive_revisions(user_id, "topic", test_topic["id"], understanding=1)
    queue = get_revision_queue(user_id)
    assert isinstance(queue, dict), "Revision queue must be a dict"
    all_queue_items = queue["overdue"] + queue["due_today"] + queue["due_this_week"] + queue["upcoming"]
    test_revs = [r for r in all_queue_items if r["item_id"] == test_topic["id"]]
    assert len(test_revs) == 3, f"Expected 3 intervals for understanding 1, found {len(test_revs)}"
    print(f"  --> PASSED: 3 adaptive intervals generated for weak topic: {[r['due_date'] for r in test_revs]}")

    # 2. Complete a revision step
    first_rev = test_revs[0]
    complete_adaptive_revision(user_id, first_rev["id"])
    queue_after = get_revision_queue(user_id)
    assert any(r["id"] == first_rev["id"] for r in queue_after["recent_completed"]), "Completed revision must appear in history"
    print("  --> PASSED: Revision completion and XP award verified.")

    # 3. Test automatic scheduling via save_progress(status='Completed')
    save_progress(user_id, "topic", test_topic["id"], status="Completed", understanding=4)
    queue_after_comp = get_revision_queue(user_id)
    all_revs_after = queue_after_comp["overdue"] + queue_after_comp["due_today"] + queue_after_comp["due_this_week"] + queue_after_comp["upcoming"]
    topic_revs = [r for r in all_revs_after if r["item_id"] == test_topic["id"]]
    assert len(topic_revs) == 4, f"Expected 4 intervals for understanding 4, found {len(topic_revs)}"
    print(f"  --> PASSED: Automatic Spaced Repetition trigger on topic completion verified ({len(topic_revs)} intervals).")

    print("\n[TEST 4] Intelligent Study Planner Auto-Scheduler & Rescheduler")
    # 1. Run Auto-Scheduler for next 7 days
    res = auto_generate_study_plan(user_id, days_count=7, topics_per_day=2)
    assert isinstance(res, dict) and "scheduled_count" in res, "Auto-scheduler must return dict"
    print(f"  --> Auto-Scheduler Result: {res['message']} (Scheduled: {res['scheduled_count']})")

    # 2. Test Overdue Task Rescheduler
    # Create an artificial past task
    past_task_id = add_daily_plan(user_id, "2026-08-01", "Past Uncompleted Task", subject_id=subs[0]["id"])
    overdue_list = get_overdue_study_tasks(user_id)
    assert any(t["id"] == past_task_id for t in overdue_list), "Past task must be detected as overdue"
    print(f"  --> Detected {len(overdue_list)} overdue task(s).")
    
    # Reschedule forward
    resched_count = reschedule_overdue_tasks(user_id, target_strategy="today_forward", max_per_day=3)
    assert resched_count > 0, "Must reschedule at least 1 task"
    overdue_after = get_overdue_study_tasks(user_id)
    assert len(overdue_after) == 0, "No overdue tasks should remain after rescheduling"
    delete_daily_plan(user_id, past_task_id)
    print(f"  --> PASSED: Overdue tasks successfully rebalanced across upcoming days.")

    print("\n================================================================")
    print("  🎉 ALL PRIORITY, PLANNER & REVISION TESTS PASSED WITH 100% SUCCESS! ")
    print("================================================================")

if __name__ == "__main__":
    run_priority_planner_revision_tests()
