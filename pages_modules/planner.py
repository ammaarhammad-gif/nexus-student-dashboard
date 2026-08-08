"""
planner.py — Study Planner, Daily Schedule, and Exam Term Allocation.

Features:
1. Daily Task & Study Planner (date-based todo with subject tagging)
2. Study Goals & Targets
3. Exam Term Allocation (assign chapters to specific terms and view term-specific progress)
"""

import streamlit as st
import datetime
from models import (
    get_daily_plans, add_daily_plan, toggle_daily_plan, delete_daily_plan,
    get_all_goals, add_goal, update_goal_progress, delete_goal,
    get_all_terms, get_all_subjects, get_chapters_for_subject,
    get_chapters_for_term, set_term_chapters, get_term_stats
)
from styles import render_header, render_metric_card


def render_planner_page(user_id: int):
    render_header("🗓️ Study Planner & Exam Allocation", "Schedule daily study tasks, track goals, and allocate chapters to exam terms.")

    tab_daily, tab_terms, tab_goals = st.tabs([
        "📋 Daily Study Plan", 
        "🏷️ Exam Term Allocator", 
        "🎯 Study Goals"
    ])

    # ── TAB 1: Daily Study Plan ──
    with tab_daily:
        _render_daily_planner_tab(user_id)

    # ── TAB 2: Exam Term Allocation ──
    with tab_terms:
        _render_term_allocation_tab(user_id)

    # ── TAB 3: Study Goals ──
    with tab_goals:
        _render_goals_tab(user_id)


def _render_daily_planner_tab(user_id: int):
    st.subheader("📅 Daily Study Tasks")

    col_date, col_summary = st.columns([2, 3])
    with col_date:
        selected_date = st.date_input("Select Date", value=datetime.date.today(), key="planner_date_picker")
        date_str = selected_date.strftime("%Y-%m-%d")

    plans = get_daily_plans(user_id, date_str)
    total_plans = len(plans)
    completed_plans = sum(1 for p in plans if p["is_completed"])
    pct = int(completed_plans / total_plans * 100) if total_plans > 0 else 0

    with col_summary:
        st.markdown(f"### Progress for {selected_date.strftime('%A, %b %d')}")
        st.progress(pct / 100)
        st.caption(f"{completed_plans} of {total_plans} tasks completed ({pct}%)")

    st.markdown("---")

    # Add task form
    with st.expander("➕ Add Planned Task", expanded=(total_plans == 0)):
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

            if st.form_submit_button("Add Task"):
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
                style = "text-decoration: line-through; color: #64748B;" if task["is_completed"] else "color: #F8FAFC;"
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
                    style = "text-decoration: line-through; color: #64748B;" if is_done else "color: #F8FAFC;"
                    st.markdown(f"<strong style='{style} font-size: 1.05rem;'>{g['title']}</strong><br><span style='color: #94A3B8; font-size: 0.8rem;'>{g['goal_type']} • Due: {g.get('deadline', 'N/A')}</span>", unsafe_allow_html=True)

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
