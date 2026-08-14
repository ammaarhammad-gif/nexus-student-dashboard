"""
planner.py — Nexus Unified Planner Module.

Consolidates:
1. 📋 Today's Plan (Time-budgeted checklist, subject tagging, XP rewards, overdue rebalancing)
2. ⚡ Smart Auto-Scheduler (Non-destructive proposal preview, cognitive interleaving, term-bound distribution)
3. 🏷️ Exam Term Allocator (Curriculum assignment to terms, term readiness)
4. 🎯 Study Goals & Sessions (Target hours, target topics, session logs)

Primary User Question Answered: "When should I study?"
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
from styles import render_top_header_bar, render_empty_state, render_html
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
        "Turn your goals into realistic study time.",
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
# 1. TODAY'S PLAN & TIME-BUDGETED CHECKLIST
# ══════════════════════════════════════════════════════════════════════════

def _render_daily_planner_tab(user_id: int):
    # Overdue Task Banner
    overdue_tasks = get_overdue_study_tasks(user_id)
    if overdue_tasks:
        render_html(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <strong style="color: #EF4444; font-size: 0.95rem;">⚠️ {len(overdue_tasks)} Overdue Study Task{'s' if len(overdue_tasks) != 1 else ''}</strong>
                        <div style="font-size: 0.8rem; color: var(--nexus-text-sub);">Unfinished tasks from past days waiting to be completed or rescheduled.</div>
                    </div>
                </div>
            </div>
        """)
        c_res1, c_res2, _ = st.columns([1.6, 1.4, 2])
        with c_res1:
            if st.button("⚡ Rebalance Across Upcoming Days", type="primary", use_container_width=True, key="plan_rebal_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today_forward", max_per_day=3)
                st.toast(f"✅ Rebalanced {count} tasks across upcoming days!", icon="🚀")
                st.rerun()
        with c_res2:
            if st.button("📅 Move All to Today", use_container_width=True, key="plan_mv_today_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today")
                st.toast(f"✅ Moved {count} tasks to today!", icon="📅")
                st.rerun()

    c_d1, c_d2 = st.columns([2, 3])
    with c_d1:
        selected_date = st.date_input("Select Date", value=datetime.date.today(), key="planner_date_picker", label_visibility="collapsed")
        date_str = selected_date.strftime("%Y-%m-%d")

    _render_planner_task_list_fragment(user_id, date_str, selected_date)


@st.fragment
def _render_planner_task_list_fragment(user_id: int, date_str: str, selected_date):
    plans = get_daily_plans(user_id, date_str)
    
    total_minutes = sum(p.get("duration_minutes", 30) for p in plans)
    completed_minutes = sum(
        p.get("duration_minutes", 30) for p in plans
        if get_optimistic_plan_status(p["id"], bool(p.get("is_completed", False)))
    )
    completed_count = sum(
        1 for p in plans
        if get_optimistic_plan_status(p["id"], bool(p.get("is_completed", False)))
    )
    total_count = len(plans)
    pct = round((completed_count / total_count * 100)) if total_count > 0 else 0

    tot_h, tot_m = divmod(total_minutes, 60)
    comp_h, comp_m = divmod(completed_minutes, 60)
    tot_time_str = f"{tot_h}h {tot_m}m" if tot_h > 0 else f"{tot_m}m"
    comp_time_str = f"{comp_h}h {comp_m}m" if comp_h > 0 else f"{comp_m}m"

    # Today Time-Budget Header Strip
    render_html(f"""
        <div class="nexus-card" style="margin: 10px 0 16px 0; padding: 16px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase;">
                        SCHEDULE FOR {selected_date.strftime('%A, %d %B')}
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: var(--nexus-text-title);">
                        {completed_count}/{total_count} Tasks Completed • <span style="color: #38BDF8;">{comp_time_str}</span> of {tot_time_str}
                    </div>
                </div>
                <div style="font-size: 1.5rem; font-weight: 900; color: #38BDF8;">
                    {pct}%
                </div>
            </div>
        </div>
    """)
    render_animated_progress_bar(pct, color="#38BDF8", height_px=7)

    # Add Task Expander
    with st.expander("➕ Add Task to Schedule", expanded=(total_count == 0)):
        subjects = get_all_subjects(user_id)
        s_opts = {"General / Non-Subject": None}
        if subjects:
            s_opts.update({s["name"]: s["id"] for s in subjects})

        with st.form("add_daily_plan_form", clear_on_submit=True):
            task_name = st.text_input("Task Description", placeholder="e.g. Solve Optics Numericals, Review French Rev Timeline")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                sel_subj = st.selectbox("Subject Tag (Optional)", list(s_opts.keys()), key="plan_add_subj_sel")
            with c_f2:
                est_dur = st.number_input("Duration (Minutes)", min_value=5, max_value=240, value=30, step=5)

            if st.form_submit_button("Add Task to Day", use_container_width=True):
                if task_name.strip():
                    add_daily_plan(
                        user_id=user_id,
                        plan_date=date_str,
                        description=task_name.strip(),
                        duration_minutes=int(est_dur),
                        subject_id=s_opts[sel_subj]
                    )
                    st.toast("Task added to schedule!", icon="🗓️")
                    st.rerun()

    if not plans:
        render_empty_state("📋", f"No tasks scheduled for {selected_date.strftime('%A, %b %d')}", "Add tasks above or use the Smart Schedule to generate a personalized study plan.")
    else:
        for p in plans:
            c_chk, c_title, c_dur, c_del = st.columns([0.6, 4.2, 1.2, 0.6])
            done = get_optimistic_plan_status(p["id"], bool(p.get("is_completed", False)))
            t_name = p.get("description") or p.get("task_name") or p.get("topic_name") or "Study Task"
            t_dur = p.get("duration_minutes") or 30

            with c_chk:
                checked = st.checkbox(
                    label="✓",
                    value=done,
                    key=f"plan_item_chk_{p['id']}",
                    label_visibility="collapsed"
                )

            with c_title:
                sub_tag = f"<span style='font-size: 0.72rem; color: {p.get('subject_color', '#38BDF8')}; font-weight: 700; background: rgba(56,189,248,0.1); padding: 1px 6px; border-radius: 6px; margin-right: 6px;'>{p.get('subject_name')}</span>" if p.get("subject_name") else ""
                title_style = "text-decoration: line-through; opacity: 0.5;" if done else "font-weight: 600;"
                render_html(f"""
                    <div style="font-size: 0.92rem; color: var(--nexus-text-title); {title_style}">
                        {sub_tag}{t_name}
                    </div>
                """)

            with c_dur:
                st.caption(f"⏱️ {t_dur}m")

            with c_del:
                if st.button("🗑️", key=f"plan_item_del_{p['id']}", help="Delete task"):
                    delete_daily_plan(user_id, p["id"])
                    st.rerun()

            if checked != done:
                def _save_task_db():
                    toggle_daily_plan(user_id, p["id"], 1 if checked else 0)
                set_optimistic_plan_status(user_id, p["id"], checked, _save_task_db)
                if checked:
                    render_floating_xp_toast(20, f"Completed: {t_name} (+20 XP)")
                else:
                    st.toast(f"Marked '{t_name}' as pending.", icon="⚪")

            st.markdown("<hr style='margin: 4px 0; border: none; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 2. SMART AUTO-SCHEDULER WITH NON-DESTRUCTIVE PROPOSAL PREVIEW
# ══════════════════════════════════════════════════════════════════════════

def _render_auto_scheduler_tab(user_id: int):
    st.markdown("### ⚡ Smart Auto-Scheduler")
    st.caption("Distributes your remaining syllabus topics evenly with cognitive interleaving. Generates a proposal preview first so you can review before applying.")

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
        daily_cap = st.slider("Max Topics Per Day", min_value=1, max_value=6, value=2, key="auto_sched_daily_cap")
    with c_p2:
        default_dur = st.select_slider("Study Duration per Topic", options=[25, 30, 45, 60], value=30, format_func=lambda x: f"{x} minutes", key="auto_sched_dur")

    if st.button("🔮 Generate Schedule Proposal", type="primary", use_container_width=True, key="btn_gen_sched_preview"):
        with st.spinner("Analyzing curriculum priorities & generating optimal study distribution..."):
            proposal = auto_generate_study_plan(
                user_id=user_id,
                start_date_str=start_date_str,
                term_id=chosen_term_id,
                daily_topic_cap=daily_cap,
                default_duration=default_dur,
                dry_run=True
            )
            st.session_state["auto_sched_proposal"] = proposal

    # Render Non-Destructive Proposal Preview if available
    proposal = st.session_state.get("auto_sched_proposal")
    if proposal:
        tasks = proposal.get("planned_tasks", [])
        render_html(f"""
            <div class="nexus-card" style="border-left: 4px solid #38BDF8; margin: 16px 0;">
                <h3 style="margin: 0 0 4px 0; color: var(--nexus-text-title); font-family: 'Outfit', sans-serif;">
                    📋 Schedule Proposal: {len(tasks)} Topics across {proposal.get('days_count', 0)} Study Days
                </h3>
                <div style="font-size: 0.84rem; color: var(--nexus-text-sub);">
                    Review recommended schedule below. Click Apply Schedule to commit these tasks to your daily study calendar.
                </div>
            </div>
        """)

        for t in tasks[:8]:
            render_html(f"""
                <div style="padding: 8px 12px; margin-bottom: 6px; background: rgba(255,255,255,0.03); border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: #38BDF8; font-weight: 700; font-size: 0.8rem;">📅 {t.get('date')}</span>
                        <strong style="color: var(--nexus-text-title); margin-left: 8px; font-size: 0.9rem;">{t.get('topic_name')}</strong>
                        <span style="font-size: 0.75rem; color: var(--nexus-text-sub); margin-left: 6px;">({t.get('subject_name')})</span>
                    </div>
                    <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">⏱️ {t.get('duration', 30)}m</span>
                </div>
            """)

        col_app1, col_app2 = st.columns(2)
        with col_app1:
            if st.button("✅ Apply Schedule to Calendar", type="primary", use_container_width=True, key="btn_commit_sched"):
                auto_generate_study_plan(
                    user_id=user_id,
                    start_date_str=start_date_str,
                    term_id=chosen_term_id,
                    daily_topic_cap=daily_cap,
                    default_duration=default_dur,
                    dry_run=False
                )
                st.session_state.pop("auto_sched_proposal", None)
                st.toast(f"✅ Scheduled {len(tasks)} tasks onto your calendar!", icon="🚀")
                st.rerun()

        with col_app2:
            if st.button("❌ Cancel Proposal", use_container_width=True, key="btn_cancel_sched"):
                st.session_state.pop("auto_sched_proposal", None)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 3. EXAM TERM ALLOCATOR
# ══════════════════════════════════════════════════════════════════════════

def _render_term_allocation_tab(user_id: int):
    st.markdown("### 🏷️ Exam Term Allocator")
    st.caption("Assign chapters to specific examination terms (e.g. Unit Test 1, Mid-Terms, Pre-Boards) to isolate term readiness and target schedules.")

    terms = get_all_terms(user_id)
    if not terms:
        render_empty_state("📅", "No Exam Terms Configured", "Go to Settings › Exam Terms to set up your upcoming target exams and dates.")
        return

    subjects = get_all_subjects(user_id)
    if not subjects:
        st.info("Please configure subjects in the Syllabus Manager first.")
        return

    term_names = [f"🎯 {t['name']} ({t.get('exam_date', 'Scheduled')})" for t in terms]
    sel_t_idx = st.selectbox("Select Exam Term to Manage:", range(len(term_names)), format_func=lambda i: term_names[i], key="term_alloc_sel_box")
    active_term = terms[sel_t_idx]

    t_stats = get_term_stats(user_id, active_term["id"]) or {}
    t_chaps = get_chapters_for_term(user_id, active_term["id"])
    t_chap_ids = [c["id"] for c in t_chaps]

    render_html(f"""
        <div class="nexus-card" style="border-left: 4px solid #F97316; margin: 12px 0 16px 0; padding: 16px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: var(--nexus-text-title); font-family: 'Outfit', sans-serif;">
                        {active_term['name']}
                    </h3>
                    <div style="font-size: 0.84rem; color: var(--nexus-text-sub);">
                        📅 Exam Date: {active_term.get('exam_date', 'Scheduled')} • {len(t_chaps)} Chapters Assigned
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.6rem; font-weight: 800; color: #F97316;">
                        {t_stats.get('readiness_pct', 0)}%
                    </div>
                    <div style="font-size: 0.72rem; color: var(--nexus-text-sub);">Term Readiness</div>
                </div>
            </div>
        </div>
    """)

    # Chapter Allocation Checkboxes by Subject
    for s in subjects:
        s_chaps = get_chapters_for_subject(user_id, s["id"])
        if not s_chaps:
            continue

        with st.expander(f"📚 {s['name']} ({len(s_chaps)} Chapters)", expanded=True):
            updated_ids = list(t_chap_ids)
            has_changes = False

            for c in s_chaps:
                is_assigned = c["id"] in t_chap_ids
                c_chk = st.checkbox(f"**{c['name']}**", value=is_assigned, key=f"t_alloc_{active_term['id']}_{c['id']}")
                if c_chk != is_assigned:
                    has_changes = True
                    if c_chk:
                        updated_ids.append(c["id"])
                    else:
                        updated_ids.remove(c["id"])

            if has_changes:
                if st.button(f"💾 Save Chapter Allocation for {s['name']}", key=f"btn_save_alloc_{s['id']}", type="primary"):
                    set_term_chapters(user_id, active_term["id"], updated_ids)
                    st.toast("Updated term chapters!", icon="✅")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 4. STUDY GOALS & LOGS
# ══════════════════════════════════════════════════════════════════════════

def _render_goals_tab(user_id: int):
    st.markdown("### 🎯 Study Goals & Daily Targets")
    goals = get_all_goals(user_id) or []

    with st.expander("➕ Set New Study Target", expanded=(len(goals) == 0)):
        with st.form("add_goal_form", clear_on_submit=True):
            g_title = st.text_input("Goal Description", placeholder="e.g. Complete 15 Optics numericals, Study 2 hours daily")
            c1, c2 = st.columns(2)
            with c1:
                g_target = st.number_input("Target Value", min_value=1, value=10)
            with c2:
                g_unit = st.selectbox("Unit", ["Topics", "Hours", "Quizzes", "Notes"])
            
            if st.form_submit_button("Save Goal", use_container_width=True):
                if g_title.strip():
                    add_goal(user_id, g_title.strip(), target_value=g_target, unit=g_unit)
                    st.toast("Goal saved!", icon="🎯")
                    st.rerun()

    if not goals:
        render_empty_state("🎯", "No Study Goals Set", "Set a target goal to track your weekly learning milestones.")
    else:
        for g in goals:
            g_val = g.get("current_value", 0)
            g_tgt = g.get("target_value", 10)
            g_pct = min(100, round((g_val / g_tgt * 100))) if g_tgt > 0 else 0

            render_html(f"""
                <div class="nexus-card" style="margin-bottom: 10px; padding: 12px 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: var(--nexus-text-title); font-size: 0.95rem;">{g.get('title')}</strong>
                        <span style="font-weight: 700; color: #38BDF8;">{g_val} / {g_tgt} {g.get('unit', '')} ({g_pct}%)</span>
                    </div>
                </div>
            """)
            render_animated_progress_bar(g_pct, color="#38BDF8", height_px=6)
            
            c_inc, c_del, _ = st.columns([1, 1, 4])
            with c_inc:
                if st.button("➕ Increment", key=f"inc_g_{g['id']}"):
                    update_goal_progress(user_id, g["id"], g_val + 1)
                    st.rerun()
            with c_del:
                if st.button("🗑️ Delete", key=f"del_g_{g['id']}"):
                    delete_goal(user_id, g["id"])
                    st.rerun()
