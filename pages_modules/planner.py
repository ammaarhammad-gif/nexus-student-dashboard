"""
planner.py — Study Planner, Daily Schedule, Exam Term Allocation, and Study Sessions.

Features:
1. Daily Task & Study Planner (date-based todo with subject tagging)
2. Study Goals & Targets
3. Exam Term Allocation (assign chapters to specific terms and view term-specific progress)
4. Study Sessions (log, view, weekly summary)
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
    get_weekly_study_summary, get_user_theme
)
from styles import render_header, render_metric_card, render_breadcrumbs, render_empty_state


def render_planner_page(user_id: int):
    user_theme = get_user_theme(user_id)
    render_breadcrumbs(["🏠 Dashboard", "🗓️ Study Planner"])
    render_header("🗓️ Study Planner & Exam Allocation", "Schedule daily study tasks, track goals, and allocate chapters to exam terms.", theme=user_theme)

    tab_daily, tab_sessions, tab_terms, tab_goals = st.tabs([
        "📋 Daily Study Plan",
        "📖 Study Sessions",
        "🏷️ Exam Term Allocator", 
        "🎯 Study Goals"
    ])

    # ── TAB 1: Daily Study Plan ──
    with tab_daily:
        _render_daily_planner_tab(user_id)

    # ── TAB 2: Study Sessions ──
    with tab_sessions:
        _render_study_sessions_tab(user_id)

    # ── TAB 3: Exam Term Allocation ──
    with tab_terms:
        _render_term_allocation_tab(user_id)

    # ── TAB 4: Study Goals ──
    with tab_goals:
        _render_goals_tab(user_id)


def _render_daily_planner_tab(user_id: int):
    st.subheader("📅 Daily Study Tasks")

    # ── 1. Missed Task Rescheduler Alert ──
    from models import get_overdue_study_tasks, reschedule_overdue_tasks, auto_generate_study_plan, get_top_nexus_priorities
    overdue_tasks = get_overdue_study_tasks(user_id)
    if overdue_tasks:
        st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <strong style="color: #EF4444; font-size: 0.95rem;">⚠️ {len(overdue_tasks)} Overdue Study Task{'s' if len(overdue_tasks) != 1 else ''}</strong>
                    <div style="font-size: 0.82rem; color: var(--nexus-text-sub);">Unfinished tasks from past days are waiting to be rescheduled.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        col_res1, col_res2, _ = st.columns([1.5, 1.5, 2])
        with col_res1:
            if st.button("⚡ Rebalance Across Upcoming Days", type="primary", use_container_width=True, key="reschedule_forward_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today_forward", max_per_day=3)
                st.toast(f"✅ Rebalanced {count} overdue tasks across upcoming study days!", icon="🚀")
                st.rerun()
        with col_res2:
            if st.button("📅 Move All to Today", use_container_width=True, key="reschedule_today_btn"):
                count = reschedule_overdue_tasks(user_id, target_strategy="today")
                st.toast(f"✅ Moved {count} tasks to today's schedule!", icon="📅")
                st.rerun()

    # ── 2. Top Controls & Intelligent Auto-Scheduler Modal ──
    col_date, col_actions = st.columns([2, 3])
    with col_date:
        selected_date = st.date_input("Select Date", value=datetime.date.today(), key="planner_date_picker")
        date_str = selected_date.strftime("%Y-%m-%d")

    with col_actions:
        with st.popover("⚡ Auto-Generate Study Plan", use_container_width=True):
            st.markdown("### 🤖 Intelligent Study Plan Auto-Scheduler")
            st.caption("Distributes unfinished & high-priority syllabus topics evenly across study days, interleaved for high retention.")
            
            terms = get_all_terms(user_id)
            term_opts = {"🌟 Full Remaining Syllabus": None}
            for t in terms:
                if not t.get("is_already_done"):
                    term_opts[f"🎯 Exam: {t['name']} ({t.get('exam_date', '')})"] = t["id"]
                    
            chosen_term_label = st.selectbox("Target Curriculum Scope:", list(term_opts.keys()), key="auto_plan_scope")
            chosen_term_id = term_opts[chosen_term_label]
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                horizon_days = st.slider("Planning Horizon (Days)", min_value=3, max_value=45, value=14, step=1, key="auto_plan_days")
            with c_p2:
                daily_topics = st.slider("Topics Per Day", min_value=1, max_value=6, value=3, step=1, key="auto_plan_cap")
                
            if st.button("🚀 Generate My Study Plan", type="primary", use_container_width=True, key="run_auto_plan_btn"):
                with st.spinner("Analyzing syllabus, exam proximity, and understanding ratings..."):
                    res = auto_generate_study_plan(
                        user_id,
                        term_id=chosen_term_id,
                        days_count=horizon_days,
                        topics_per_day=daily_topics,
                        start_date=date_str
                    )
                if res.get("scheduled_count", 0) > 0:
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.info(res["message"])

    plans = get_daily_plans(user_id, date_str)
    total_plans = len(plans)
    completed_plans = sum(1 for p in plans if p["is_completed"])
    pct = int(completed_plans / total_plans * 100) if total_plans > 0 else 0

    st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 18px; margin: 12px 0 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <strong style="font-size: 1.05rem; color: var(--nexus-text-title);">Tasks for {selected_date.strftime('%A, %b %d')}</strong>
                <span style="font-size: 0.9rem; font-weight: 700; color: #38BDF8;">{completed_plans}/{total_plans} Completed ({pct}%)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(pct / 100)

    # ── 3. Nexus Smart Priority Quick-Add Bar ──
    top_prios = get_top_nexus_priorities(user_id, limit=3)
    if top_prios:
        with st.expander("🔴 Nexus Smart Priority Recommendations for Today", expanded=False):
            st.caption("High-urgency topics based on upcoming exams and low understanding scores:")
            for p in top_prios:
                c_pinfo, c_pbtn = st.columns([4, 1])
                with c_pinfo:
                    st.markdown(f"""
                        <span class="nexus-pill-{p['tier'].lower()}">{p['tier_icon']} {p['tier']}</span>
                        <strong style="margin-left: 6px; color: var(--nexus-text-title);">{p['topic_name']}</strong> 
                        <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">({p['subject_name']} › {p['chapter_name']})</span>
                    """, unsafe_allow_html=True)
                with c_pbtn:
                    if st.button("+ Plan Today", key=f"quick_add_prio_{p['topic_id']}", use_container_width=True):
                        desc = f"Study: {p['topic_name']} ({p['subject_name']})"
                        add_daily_plan(user_id, date_str, desc, 45, subject_id=p["subject_id"], chapter_id=p["chapter_id"], topic_id=p["topic_id"])
                        st.toast(f"Added {p['topic_name']} to today's schedule!", icon="✨")
                        st.rerun()

    st.markdown("---")

    # Add task form
    with st.expander("➕ Add Custom Task", expanded=(total_plans == 0)):
        subjects = get_all_subjects(user_id)
        subject_options = {"None": None}
        for s in subjects:
            subject_options[s["name"]] = s["id"]

        with st.form("add_daily_task_form", clear_on_submit=True):
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                desc = st.text_input("Task Description *", placeholder="e.g. Read Physics Chapter 2 & solve exercises")
            with col_t2:
                duration = st.number_input("Est. Minutes", min_value=5, max_value=480, value=30, step=5)

            selected_sub_name = st.selectbox("Link to Subject (Optional)", list(subject_options.keys()))
            sub_id = subject_options[selected_sub_name]

            if st.form_submit_button("Add Task", use_container_width=True, type="primary"):
                if desc.strip():
                    add_daily_plan(user_id, date_str, desc.strip(), duration, subject_id=sub_id)
                    st.success("Task added!")
                    st.rerun()
                else:
                    st.error("Please enter a task description.")

    # List tasks
    if not plans:
        st.info(f"No study tasks scheduled for {selected_date.strftime('%b %d, %Y')}. Add one above!")
    else:
        for task in plans:
            c_check, c_desc, c_dur, c_del = st.columns([1, 6, 2, 1])
            with c_check:
                is_done = st.checkbox(
                    "Done", 
                    value=bool(task["is_completed"]), 
                    key=f"task_chk_{task['id']}",
                    label_visibility="collapsed"
                )
                if is_done != bool(task["is_completed"]):
                    toggle_daily_plan(user_id, task["id"], is_done)
                    st.rerun()

            with c_desc:
                color = task.get("subject_color") or "#475569"
                sub_name = task.get("subject_name")
                tag = f"<span style='background: {color}; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; color: #fff;'>{sub_name}</span> " if sub_name else ""
                style = "text-decoration: line-through; opacity: 0.6;" if task["is_completed"] else ""
                st.markdown(f"{tag}<span style='{style} font-weight: 500;'>{task['description']}</span>", unsafe_allow_html=True)

            with c_dur:
                st.caption(f"⏱️ {task['duration_minutes']} min")

            with c_del:
                if st.button("🗑️", key=f"del_task_{task['id']}", help="Delete Task"):
                    delete_daily_plan(user_id, task["id"])
                    st.rerun()


def _render_term_allocation_tab(user_id: int):
    st.subheader("🏷️ Exam Term Syllabus Allocator")
    st.caption("Assign chapters to each upcoming exam or term to track term-specific syllabus completion.")

    terms = get_all_terms(user_id)
    subjects = get_all_subjects(user_id)

    if not terms:
        st.warning("No exam terms found. Go to **Settings** to add terms first.")
        return

    if not subjects:
        st.warning("No subjects found. Go to **Syllabus Manager** to add subjects first.")
        return

    term_names = [t["name"] for t in terms]
    sel_term_idx = st.selectbox("Select Exam Term", range(len(term_names)), format_func=lambda i: f"🏆 {term_names[i]}")
    selected_term = terms[sel_term_idx]

    # Show Term Stats
    term_stats = get_term_stats(user_id, selected_term["id"])
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Assigned Chapters", term_stats["total_chapters"], "#6366F1")
    with m2:
        render_metric_card("Total Topics", term_stats["total_topics"], "#8B5CF6")
    with m3:
        render_metric_card("Completed Topics", term_stats["completed"], "#22C55E")
    with m4:
        render_metric_card("Term Completion", f"{term_stats['percent_completed']}%", "#EC4899")

    st.markdown("---")

    # Current chapter selections
    assigned_chapter_ids = set(get_chapters_for_term(user_id, selected_term["id"]))

    st.markdown(f"### Select Chapters included in **{selected_term['name']}**")
    
    with st.form(f"term_chapters_form_{selected_term['id']}"):
        new_assigned_ids = set()

        for sub in subjects:
            chaps = get_chapters_for_subject(user_id, sub["id"])
            if not chaps:
                continue
            
            st.markdown(f"**📖 {sub['name']}**")
            cols = st.columns(2)
            for idx, ch in enumerate(chaps):
                with cols[idx % 2]:
                    checked = st.checkbox(
                        ch["name"],
                        value=(ch["id"] in assigned_chapter_ids),
                        key=f"term_ch_{selected_term['id']}_{ch['id']}"
                    )
                    if checked:
                        new_assigned_ids.add(ch["id"])

        save_alloc = st.form_submit_button("💾 Save Term Allocations", use_container_width=True)
        if save_alloc:
            set_term_chapters(user_id, selected_term["id"], list(new_assigned_ids))
            st.success(f"Updated chapter allocations for {selected_term['name']}!")
            st.rerun()


def _render_goals_tab(user_id: int):
    st.subheader("🎯 Academic Goals & Targets")

    goals = get_all_goals(user_id)

    with st.expander("➕ Add New Goal", expanded=(len(goals) == 0)):
        with st.form("add_goal_form", clear_on_submit=True):
            col_g1, col_g2 = st.columns([3, 1])
            with col_g1:
                title = st.text_input("Goal Title *", placeholder="e.g. Revise Math Chapter 1-3 before Friday")
            with col_g2:
                g_type = st.selectbox("Goal Type", ["Daily", "Weekly", "Monthly", "Exam Goal"])

            col_g3, col_g4 = st.columns(2)
            with col_g3:
                target = st.number_input("Target Count / Hours", min_value=1, value=1)
            with col_g4:
                deadline = st.date_input("Target Date (Optional)", value=datetime.date.today() + datetime.timedelta(days=7))

            if st.form_submit_button("Save Goal"):
                if title.strip():
                    add_goal(user_id, title.strip(), g_type, target, deadline.strftime("%Y-%m-%d"))
                    st.success("Goal added!")
                    st.rerun()
                else:
                    st.error("Please enter a goal title.")

    if not goals:
        st.info("No study goals added yet. Set a target above to stay motivated!")
    else:
        for g in goals:
            is_done = bool(g["is_completed"])
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 5, 3, 1])
                with c1:
                    chk = st.checkbox("Done", value=is_done, key=f"goal_chk_{g['id']}", label_visibility="collapsed")
                    if chk != is_done:
                        update_goal_progress(user_id, g["id"], g["target"] if chk else 0, is_completed=chk)
                        st.rerun()

                with c2:
                    style = "text-decoration: line-through; opacity: 0.6;" if is_done else ""
                    st.markdown(f"<strong style='{style} font-size: 1.05rem;'>{g['title']}</strong><br><span style='font-size: 0.8rem;'>{g['goal_type']} • Due: {g.get('deadline', 'N/A')}</span>", unsafe_allow_html=True)

                with c3:
                    new_prog = st.number_input(
                        "Progress", 
                        min_value=0, 
                        max_value=max(100, g["target"]), 
                        value=g["progress"], 
                        key=f"goal_prog_{g['id']}",
                        label_visibility="collapsed"
                    )
                    if new_prog != g["progress"]:
                        update_goal_progress(user_id, g["id"], new_prog, is_completed=(new_prog >= g["target"]))
                        st.rerun()

                with c4:
                    if st.button("🗑️", key=f"del_goal_{g['id']}"):
                        delete_goal(user_id, g["id"])
                        st.rerun()
                st.markdown("---")


def _render_study_sessions_tab(user_id: int):
    """Log, view, and analyze study sessions."""
    st.subheader("📖 Study Sessions")
    st.caption("Track how long you study each subject. Review your weekly habits.")

    # ── Weekly Study Summary Chart ──
    weekly = get_weekly_study_summary(user_id)
    day_labels = [d["day_label"] for d in weekly]
    day_minutes = [d["minutes"] for d in weekly]
    total_week = sum(day_minutes)

    col_chart, col_stat = st.columns([3, 1])
    with col_stat:
        render_metric_card("This Week", f"{total_week} min", "#A855F7",
                          f"{round(total_week / 60, 1)} hours")
        today_mins = day_minutes[-1] if day_minutes else 0
        render_metric_card("Today", f"{today_mins} min", "#22C55E")

    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")
    text_col = "#FFFFFF" if is_dark else "#0F172A"
    axis_col = "#CBD5E1" if is_dark else "#64748B"
    grid_col = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)"
    empty_bar_col = "#334155" if is_dark else "#E2E8F0"

    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=day_labels,
            y=day_minutes,
            marker_color=[
                "#4F46E5" if m > 0 else empty_bar_col for m in day_minutes
            ],
            text=[f"{m}m" if m > 0 else "" for m in day_minutes],
            textposition="outside",
            textfont=dict(color=text_col, size=12)
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=axis_col),
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Minutes", showgrid=True,
                       gridcolor=grid_col),
            margin=dict(t=10, b=30, l=40, r=20),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Log a Session ──
    with st.expander("➕ Log a Study Session", expanded=True):
        subjects = get_all_subjects(user_id)
        subject_options = {"— Select Subject —": None}
        for s in subjects:
            subject_options[s["name"]] = s["id"]

        with st.form("log_session_form", clear_on_submit=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                sel_sub = st.selectbox("Subject *", list(subject_options.keys()),
                                      key="session_subject")
                sub_id = subject_options[sel_sub]
            with col_b:
                duration = st.number_input("Duration (min) *", min_value=1,
                                          max_value=720, value=30, step=5)

            col_c, col_d = st.columns(2)
            with col_c:
                sess_date = st.date_input("Date", value=datetime.date.today(),
                                         key="session_date")
            with col_d:
                sess_notes = st.text_input("Notes (optional)",
                                          placeholder="What did you study?")

            if st.form_submit_button("💾 Log Session", use_container_width=True):
                if not sub_id:
                    st.error("Please select a subject.")
                else:
                    add_study_session(
                        user_id, subject_id=sub_id,
                        duration_minutes=duration,
                        session_date=sess_date.strftime("%Y-%m-%d"),
                        notes=sess_notes
                    )
                    st.success("Study session logged!")
                    st.rerun()

    st.markdown("---")

    # ── Recent Sessions ──
    st.subheader("📋 Recent Sessions")
    sessions = get_study_sessions(user_id, limit=20)

    if not sessions:
        st.info("No study sessions logged yet. Start by adding one above!")
    else:
        for sess in sessions:
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            with c1:
                sub_name = sess.get("subject_name") or "Unknown"
                color = sess.get("subject_color") or "#475569"
                st.markdown(
                    f"<span style='background: {color}; padding: 2px 8px; "
                    f"border-radius: 4px; font-size: 0.75rem; color: #fff;'>"
                    f"{sub_name}</span> "
                    f"<span style='font-weight: 500;'>"
                    f"{sess.get('notes') or ''}</span>",
                    unsafe_allow_html=True
                )

            with c2:
                st.caption(f"⏱️ {sess['duration_minutes']} min")
            with c3:
                st.caption(f"📅 {sess.get('session_date', '')}")
            with c4:
                if st.button("🗑️", key=f"del_sess_{sess['id']}", help="Delete"):
                    delete_study_session(user_id, sess["id"])
                    st.rerun()
