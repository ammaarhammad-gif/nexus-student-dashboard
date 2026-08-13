"""
planner.py — Nexus Unified Planner Module.

Consolidates:
1. 📋 Today's Plan (Date-based task checklist, subject tagging, XP rewards, overdue rebalancing)
2. ⚡ Smart Auto-Scheduler (Target horizon, daily topic cap, interleaved study scheduling)
3. 🏷️ Exam Term Allocator (Curriculum assignment to terms, term readiness)
4. 🎯 Study Goals & Sessions (Target hours, target topics, session logs)
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
from models import (
    get_daily_plans, add_daily_plan, toggle_daily_plan, delete_daily_plan,
    get_all_goals, add_goal, update_goal_progress, delete_goal,
    get_all_terms, get_all_subjects, get_chapters_for_subject,
    get_chapters_for_term, set_term_chapters, get_term_stats,
    add_study_session, get_study_sessions, delete_study_session,
    get_weekly_study_summary, get_user_theme,
    get_overdue_study_tasks, reschedule_overdue_tasks,
    auto_generate_study_plan, get_top_nexus_priorities
)
from styles import render_top_header_bar, render_metric_card, render_breadcrumbs, render_empty_state
from ui_optimistic import (
    get_optimistic_plan_status,
    set_optimistic_plan_status,
    render_animated_progress_bar,
    render_floating_xp_toast
)



def render_planner_page(user_id: int):
    render_top_header_bar(
        user_id,
        "🗓️ Planner",
        "Structure daily study missions, auto-schedule remaining curriculum, and track horizons.",
        ["NEXUS", "Planner"]
    )

    tab_daily, tab_scheduler, tab_terms, tab_goals = st.tabs([
        "📋 Today's Plan",
        "⚡ Smart Schedule",
        "🏷️ Exam Term Allocator",
        "🎯 Study Goals & Logs"
    ])


    with tab_daily:
        _render_daily_planner_tab(user_id)

    with tab_scheduler:
        _render_auto_scheduler_tab(user_id)

    with tab_terms:
        _render_term_allocation_tab(user_id)

    with tab_goals:
        _render_goals_tab(user_id)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 1: TODAY'S PLAN & DAILY SCHEDULE
# ══════════════════════════════════════════════════════════════════════════

def _render_daily_planner_tab(user_id: int):
    # Overdue Task Alert
    overdue_tasks = get_overdue_study_tasks(user_id)
    if overdue_tasks:
        st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 14px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <strong style="color: #EF4444; font-size: 0.95rem;">⚠️ {len(overdue_tasks)} Overdue Study Task{'s' if len(overdue_tasks) != 1 else ''}</strong>
                    <div style="font-size: 0.82rem; color: var(--nexus-text-sub);">Unfinished tasks from past days are waiting to be completed or rescheduled.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        col_res1, col_res2, _ = st.columns([1.5, 1.5, 2])
        with col_res1:
            if st.button("⚡ Rebalance Across Upcoming Days", type="primary", use_container_width=True, key="plan_resched_forward_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today_forward", max_per_day=3)
                st.toast(f"✅ Rebalanced {count} overdue tasks across upcoming study days!", icon="🚀")
                st.rerun()
        with col_res2:
            if st.button("📅 Move All to Today", use_container_width=True, key="plan_resched_today_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today")
                st.toast(f"✅ Moved {count} tasks to today's schedule!", icon="📅")
                st.rerun()

    c_d1, c_d2 = st.columns([2, 3])
    with c_d1:
        selected_date = st.date_input("Select Date", value=datetime.date.today(), key="planner_date_picker")
        date_str = selected_date.strftime("%Y-%m-%d")

    _render_planner_task_list_fragment(user_id, date_str, selected_date)


@st.fragment
def _render_planner_task_list_fragment(user_id: int, date_str: str, selected_date):
    plans = get_daily_plans(user_id, date_str)
    
    # Calculate optimistic completion counts
    completed_count = sum(
        1 for p in plans
        if get_optimistic_plan_status(p["id"], bool(p.get("is_completed", False)))
    )
    total_plans = len(plans)
    pct = round((completed_count / total_plans) * 100) if total_plans > 0 else 0

    render_animated_progress_bar(pct, color="#38BDF8", height_px=9, label=f"Daily Progress: {completed_count}/{total_plans} Tasks")

    # Add Task Form
    with st.expander("➕ Add Task for " + selected_date.strftime('%b %d, %Y'), expanded=(total_plans == 0)):
        subjects = get_all_subjects(user_id)
        s_opts = {"General / Non-Subject": None}
        if subjects:
            s_opts.update({s["name"]: s["id"] for s in subjects})

        with st.form("add_daily_plan_form", clear_on_submit=True):
            task_name = st.text_input("Task Description", placeholder="e.g. Read Light Refraction notes, Solve Exercise 10.2")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                sel_subj = st.selectbox("Subject Tag (Optional)", list(s_opts.keys()), key="plan_add_subj_sel")
            with c_f2:
                est_dur = st.number_input("Estimated Minutes", min_value=5, max_value=240, value=30, step=5)

            if st.form_submit_button("Add Task to Schedule", use_container_width=True):
                if task_name.strip():
                    add_daily_plan(
                        user_id=user_id,
                        plan_date=date_str,
                        description=task_name.strip(),
                        duration_minutes=int(est_dur),
                        subject_id=s_opts[sel_subj]
                    )
                    st.success("Task added!")
                    st.rerun()

    if not plans:
        render_empty_state("📋", f"No tasks scheduled for {selected_date.strftime('%A, %b %d')}", "Add tasks manually above or use the Smart Auto-Scheduler to generate an optimal study plan.")
    else:
        for p in plans:
            c1, c2, c3 = st.columns([5, 1.2, 0.8])
            with c1:
                t_name = p.get("description") or p.get("task_name") or p.get("topic_name") or "Study Task"
                t_dur = p.get("duration_minutes") or p.get("estimated_minutes") or 30
                done = get_optimistic_plan_status(p["id"], bool(p.get("is_completed", False)))
                sub_label = f" <span style='font-size: 0.75rem; color: {p.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 10px; font-weight: 700;'>{p.get('subject_name')}</span>" if p.get("subject_name") else ""
                
                checked = st.checkbox(
                    f"**{t_name}**",
                    value=done,
                    key=f"plan_item_chk_{p['id']}"
                )
                if checked != done:
                    def _save_task_db():
                        toggle_daily_plan(user_id, p["id"], 1 if checked else 0)
                    set_optimistic_plan_status(user_id, p["id"], checked, _save_task_db)
                    if checked:
                        render_floating_xp_toast(15, f"Completed: {t_name}")
                    else:
                        st.toast(f"Marked '{t_name}' as pending.", icon="⚪")

                if sub_label:
                    st.markdown(f"<div style='margin-left: 28px; margin-top: -4px;'>{sub_label}</div>", unsafe_allow_html=True)

            with c2:
                st.caption(f"⏱️ {t_dur} min")

            with c3:
                if st.button("🗑️", key=f"plan_item_del_{p['id']}", help="Delete task"):
                    delete_daily_plan(user_id, p["id"])
                    st.rerun()
            st.markdown("<hr style='margin: 6px 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 2: SMART AUTO-SCHEDULER
# ══════════════════════════════════════════════════════════════════════════

def _render_auto_scheduler_tab(user_id: int):
    st.markdown("### 🤖 Intelligent Syllabus Auto-Scheduler")
    st.caption("Distributes your remaining syllabus topics evenly across study days with cognitive interleaving to prevent burnout and maximize retention.")

    terms = get_all_terms(user_id)
    term_opts = {"🌟 Full Remaining Syllabus": None}
    for t in terms:
        if not t.get("is_already_done"):
            term_opts[f"🎯 Exam: {t['name']} ({t.get('exam_date', '')})"] = t["id"]

    c_s1, c_s2 = st.columns(2)
    with c_s1:
        chosen_term_label = st.selectbox("Target Curriculum Scope:", list(term_opts.keys()), key="auto_sched_tab_scope")
        chosen_term_id = term_opts[chosen_term_label]
    with c_s2:
        start_date = st.date_input("Start Scheduling From:", value=datetime.date.today(), key="auto_sched_start_date")
        start_date_str = start_date.strftime("%Y-%m-%d")

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        horizon_days = st.slider("Planning Horizon (Days)", min_value=3, max_value=60, value=14, step=1, key="auto_sched_horizon_days")
    with c_p2:
        daily_topics = st.slider("Topics Per Day", min_value=1, max_value=6, value=3, step=1, key="auto_sched_daily_cap")

    if st.button("🚀 Auto-Generate & Schedule Study Plan", type="primary", use_container_width=True, key="run_auto_sched_tab_btn"):
        with st.spinner("Analyzing syllabus, priority rankings, and exam proximity..."):
            res = auto_generate_study_plan(
                user_id,
                term_id=chosen_term_id,
                days_count=horizon_days,
                topics_per_day=daily_topics,
                start_date=start_date_str
            )
        if res.get("scheduled_count", 0) > 0:
            st.success(res["message"])
            st.rerun()
        else:
            st.info(res["message"])


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 3: EXAM TERM ALLOCATOR
# ══════════════════════════════════════════════════════════════════════════

def _render_term_allocation_tab(user_id: int):
    st.subheader("🏷️ Allocate Chapters to Exam Terms")
    st.markdown("Assign specific chapters to upcoming terms (e.g. Unit Tests, Mid-Terms, Pre-Boards) to isolate term-specific revision goals.")

    terms = get_all_terms(user_id)
    if not terms:
        st.info("No exam terms found. Add terms in Settings → Exams.")
        return

    term_map = {t["name"]: t["id"] for t in terms}
    sel_term_name = st.selectbox("Select Exam Term", list(term_map.keys()), key="plan_term_alloc_sel")
    sel_term_id = term_map[sel_term_name]

    # Stats for term
    stats = get_term_stats(user_id, sel_term_id)
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Allocated Chapters", stats.get("total_chapters", 0), "Chapters in term")
    with c2:
        render_metric_card("Total Topics", stats.get("total_topics", 0), "Topics to master")
    with c3:
        pct_val = stats.get("percent_completed", stats.get("completion_pct", 0.0))
        comp_val = stats.get("completed", stats.get("completed_topics", 0))
        tot_val = stats.get("total_topics", 0)
        render_metric_card("Term Completion", f"{pct_val}%", f"{comp_val}/{tot_val} done")

    # Allocation Editor
    st.markdown("### 📚 Select Chapters Included in this Term")
    subjects = get_all_subjects(user_id)
    allocated_chap_ids = get_chapters_for_term(user_id, sel_term_id)

    selected_chap_ids = list(allocated_chap_ids)

    with st.form(f"term_alloc_form_{sel_term_id}"):
        for s in subjects:
            chaps = get_chapters_for_subject(user_id, s["id"])
            if chaps:
                st.markdown(f"**📖 {s['name']}**")
                cols = st.columns(min(len(chaps), 3) or 1)
                for idx, c in enumerate(chaps):
                    col = cols[idx % len(cols)]
                    is_in = c["id"] in allocated_chap_ids
                    chk = col.checkbox(c["name"], value=is_in, key=f"t_alloc_chk_{sel_term_id}_{c['id']}")
                    if chk and c["id"] not in selected_chap_ids:
                        selected_chap_ids.append(c["id"])
                    elif not chk and c["id"] in selected_chap_ids:
                        selected_chap_ids.remove(c["id"])

        if st.form_submit_button("💾 Save Term Chapter Allocation", type="primary", use_container_width=True):
            set_term_chapters(user_id, sel_term_id, selected_chap_ids)
            st.success("Term chapter allocation saved successfully!")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 4: STUDY GOALS & SESSIONS
# ══════════════════════════════════════════════════════════════════════════

def _render_goals_tab(user_id: int):
    tab_g_active, tab_g_new, tab_sessions_log = st.tabs(["🎯 Active Goals", "➕ New Goal", "⏱️ Study Sessions Log"])

    with tab_g_new:
        st.subheader("Create Academic Target")
        with st.form("add_goal_form_plan", clear_on_submit=True):
            g_title = st.text_input("Goal Title", placeholder="e.g. Complete 50 MCQs this week, Study 15 hours")
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                g_type = st.selectbox("Goal Type", ["Weekly Hours", "Chapter Mastery", "Daily Consistency", "Quiz Target"])
            with c_g2:
                g_target = st.number_input("Target Value", min_value=1, value=10)
            g_unit = st.text_input("Unit (e.g. hours, topics, quizzes)", value="hours")

            if st.form_submit_button("Create Target Goal", use_container_width=True, type="primary"):
                if g_title.strip():
                    add_goal(user_id, g_title.strip(), g_type, g_target, g_unit)
                    st.success("Goal created!")
                    st.rerun()

    with tab_g_active:
        goals = get_all_goals(user_id)
        if not goals:
            render_empty_state("🎯", "No Active Goals", "Set daily or weekly academic targets to stay focused and measure velocity.")
        else:
            for g in goals:
                pct = min(100, round((g["current_value"] / g["target_value"]) * 100)) if g["target_value"] > 0 else 0
                c_info, c_act = st.columns([4, 1.2])
                with c_info:
                    st.markdown(f"""
                        <div style="font-weight: 700; font-size: 1.05rem; color: var(--nexus-text-title); margin-bottom: 2px;">
                            {g['title']}
                        </div>
                        <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-bottom: 6px;">
                            {g['current_value']} / {g['target_value']} {g.get('unit', '')} ({pct}%)
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(pct / 100)

                with c_act:
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button("➕1", key=f"g_inc_{g['id']}"):
                            update_goal_progress(user_id, g['id'], g['current_value'] + 1)
                            st.rerun()
                    with c_b2:
                        if st.button("🗑️", key=f"g_del_{g['id']}"):
                            delete_goal(user_id, g['id'])
                            st.rerun()
                st.markdown("<hr style='margin: 8px 0; opacity: 0.15;'/>", unsafe_allow_html=True)

    with tab_sessions_log:
        st.subheader("⏱️ Focus & Study Session History")
        sessions = get_study_sessions(user_id, limit=15)
        if not sessions:
            render_empty_state("⏱️", "No Study Sessions Logged", "Launch a session in the Focus Studio to record your study time automatically.")
        else:
            for s in sessions:
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {s.get('subject_color', '#38BDF8')}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: var(--nexus-text-title);">{s.get('subject_name', 'Study Session')}</span>
                                <div style="font-size: 0.8rem; color: var(--nexus-text-sub);">{s.get('topic_name') or 'Focused Study'} • {s['session_date']}</div>
                            </div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: #38BDF8;">
                                {s['duration_minutes']} min
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
