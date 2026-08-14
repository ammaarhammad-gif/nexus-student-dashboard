"""
dashboard.py — Nexus Academic Command Center Dashboard.

Core Design Philosophy:
PLAN → LEARN → PRACTICE → REVIEW → FOCUS → MEASURE → IMPROVE

Primary User Question Answered: "What should I do next?"
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
from models import (
    get_overall_stats, get_user_profile,
    get_all_subjects_with_stats, get_active_upcoming_terms,
    get_user_theme, get_user_xp_summary, get_top_nexus_priorities,
    calculate_exam_readiness_score, get_daily_plans,
    get_revision_queue, get_unreviewed_mistakes_for_quiz,
    get_recent_activity_stream, get_weak_areas, get_focus_analytics
)
from preloaded_syllabi import preload_standard_syllabus
from styles import render_top_header_bar, render_html


def render_dashboard_page(user_id: int):
    profile = get_user_profile(user_id) or {}
    user_name = profile.get("name", "Student")
    class_name = profile.get("class_name", "Class 10")
    board = profile.get("board", "CBSE")
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # Ensure standard syllabus is preloaded if database is empty
    subjects_raw = get_all_subjects_with_stats(user_id)
    if not subjects_raw:
        preload_standard_syllabus(user_id, board=board, class_name=class_name)

    stats = get_overall_stats(user_id) or {}
    xp_info = get_user_xp_summary(user_id) or {}
    readiness = calculate_exam_readiness_score(user_id) or {}
    priorities = get_top_nexus_priorities(user_id, limit=3) or []
    queue = get_revision_queue(user_id) or {}
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_plans = get_daily_plans(user_id, today_str) or []
    unreviewed_mistakes = get_unreviewed_mistakes_for_quiz(user_id, limit=10) or []
    weak_areas = get_weak_areas(user_id, limit=3) or []
    recent_activity = get_recent_activity_stream(user_id, limit=4) or []

    # TOP APPLICATION HEADER BAR
    render_top_header_bar(
        user_id,
        "🏠 Dashboard",
        "Executive academic command center and daily intelligence briefing.",
        ["NEXUS", "Dashboard"]
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 1. GREETING (Clean, subtle date, no giant quotes)
    # ══════════════════════════════════════════════════════════════════════════
    now_hour = datetime.datetime.now().hour
    if now_hour < 12:
        time_greeting = "Good morning"
    elif now_hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    today_date_str = datetime.date.today().strftime("%A, %d %B %Y")

    render_html(f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 8px;">
                <div>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.85rem; font-weight: 800; color: var(--nexus-text-title); margin: 0 0 2px 0; letter-spacing: -0.02em;">
                        {time_greeting}, <span style="background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{user_name}</span>.
                    </h2>
                    <p style="color: var(--nexus-text-sub); font-size: 0.92rem; margin: 0; font-weight: 500;">
                        Let's make today's study session count.
                    </p>
                </div>
                <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); padding: 5px 12px; border-radius: 10px; font-size: 0.82rem; font-weight: 600; color: var(--nexus-text-sub);">
                    📅 {today_date_str}
                </div>
            </div>
        </div>
    """)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TODAY'S MISSION (Strongest Action Area)
    # ══════════════════════════════════════════════════════════════════════════
    top_prio = priorities[0] if priorities else None
    overdue_count = len(queue.get("overdue", []))
    pending_tasks = [t for t in today_plans if not t.get("is_completed")]

    # Primary recommendation
    if top_prio:
        primary_title = f"{top_prio['subject_name']} • {top_prio['topic_name']}"
        primary_duration = "45 minutes"
        primary_reason = " • ".join(top_prio.get("reasons", ["Low confidence + exam approaching"]))
        primary_topic_id = top_prio.get("topic_id")
        primary_subject_id = top_prio.get("subject_id")
    elif pending_tasks:
        p_task = pending_tasks[0]
        primary_title = f"{p_task.get('subject_name', 'General')} • {p_task.get('description', 'Planned Study Task')}"
        primary_duration = f"{p_task.get('duration_minutes', 30)} minutes"
        primary_reason = "Scheduled on today's study planner"
        primary_topic_id = p_task.get("topic_id")
        primary_subject_id = p_task.get("subject_id")
    elif overdue_count > 0:
        primary_title = f"Spaced Repetition Review ({overdue_count} topics due)"
        primary_duration = "20 minutes"
        primary_reason = "Critical active retrieval retention window"
        primary_topic_id = None
        primary_subject_id = None
    else:
        primary_title = "Curriculum Exploration & Practice"
        primary_duration = "30 minutes"
        primary_reason = "Maintain daily learning momentum"
        primary_topic_id = None
        primary_subject_id = None

    # Secondary actions (max 2)
    secondary_actions = []
    if overdue_count > 0 and top_prio:
        secondary_actions.append({
            "title": f"🔄 Spaced Repetition ({overdue_count} topics)",
            "desc": "Active retrieval to prevent forgetting",
            "time": "15m",
            "xp": "+25 XP",
            "page": "🧠 Review"
        })
    if unreviewed_mistakes:
        secondary_actions.append({
            "title": f"❌ Mistake Vault ({len(unreviewed_mistakes)} items)",
            "desc": "Review incorrect quiz questions",
            "time": "10m",
            "xp": "+20 XP",
            "page": "🎯 Practice"
        })
    if len(secondary_actions) < 2 and pending_tasks and top_prio:
        secondary_actions.append({
            "title": f"🗓️ {pending_tasks[0].get('description', 'Planned Task')}",
            "desc": f"{pending_tasks[0].get('subject_name', 'Study')} ({pending_tasks[0].get('duration_minutes', 30)}m)",
            "time": f"{pending_tasks[0].get('duration_minutes', 30)}m",
            "xp": "+30 XP",
            "page": "🗓️ Planner"
        })

    sec_items_html = "".join([
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; margin-top: 6px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;">
            <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: var(--nexus-text-title);">{sa['title']}</div>
                <div style="font-size: 0.74rem; color: var(--nexus-text-sub);">{sa['desc']}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.72rem; color: #38BDF8; font-weight: 700; background: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 6px;">{sa['xp']}</span>
                <span style="font-size: 0.72rem; color: var(--nexus-text-sub);">{sa['time']}</span>
            </div>
        </div>
        """
        for sa in secondary_actions[:2]
    ])

    render_html(f"""
        <div class="nexus-card" style="border-left: 4px solid var(--nexus-accent); margin-bottom: 20px; padding: 20px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.08em;">
                    🎯 TODAY'S MISSION
                </span>
                <span style="font-size: 0.76rem; color: var(--nexus-text-sub); background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 8px;">
                    ⏱️ {primary_duration}
                </span>
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 800; color: var(--nexus-text-title); margin-bottom: 4px;">
                {primary_title}
            </div>
            <div style="font-size: 0.84rem; color: #38BDF8; font-weight: 600; margin-bottom: 12px;">
                💡 Reason: <span style="color: var(--nexus-text-sub); font-weight: 500;">{primary_reason}</span>
            </div>
            {sec_items_html}
        </div>
    """)

    col_btn_m1, col_btn_m2, _ = st.columns([1.3, 1.3, 2])
    with col_btn_m1:
        if st.button("🚀 Start Mission", type="primary", use_container_width=True, key="dash_start_mission_btn"):
            if primary_topic_id:
                st.session_state["focus_target_topic_id"] = primary_topic_id
            if primary_subject_id:
                st.session_state["focus_target_subject_id"] = primary_subject_id
            st.session_state["current_page"] = "⏱️ Focus"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with col_btn_m2:
        if st.button("📋 View Details", use_container_width=True, key="dash_view_details_btn"):
            st.session_state["current_page"] = "📚 Learn"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    render_html("<div style='margin-top: 18px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # 3. EXAM READINESS & EXAM COUNTDOWN (Side-by-Side)
    # ══════════════════════════════════════════════════════════════════════════
    r_score = readiness.get("readiness_score", 75)
    r_color = "#22C55E" if r_score >= 80 else ("#38BDF8" if r_score >= 60 else ("#F59E0B" if r_score >= 40 else "#EF4444"))
    r_tier = "Exam Ready" if r_score >= 80 else ("Progressing" if r_score >= 60 else ("Needs Review" if r_score >= 40 else "Critical"))

    active_terms = get_active_upcoming_terms(user_id) or []
    next_term = active_terms[0] if active_terms else None

    col_readiness, col_countdown = st.columns([1.2, 1.2])

    with col_readiness:
        render_html(f"""
            <div class="nexus-card" style="height: 100%; border-top: 3px solid {r_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.06em;">
                        EXAM READINESS
                    </span>
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;">
                        {r_tier}
                    </span>
                </div>
                <div style="display: flex; align-items: baseline; gap: 6px; margin: 4px 0 12px 0;">
                    <div style="font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 900; color: {r_color}; line-height: 1;">
                        {r_score}%
                    </div>
                    <div style="font-size: 0.95rem; color: var(--nexus-text-sub); font-weight: 600;">Overall Mastery</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;">
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--nexus-text-sub); margin-bottom: 2px;">
                            <span>Syllabus</span>
                            <strong style="color: var(--nexus-text-title);">{readiness.get('syllabus_pct', 0)}%</strong>
                        </div>
                        <div style="background: rgba(255,255,255,0.06); height: 5px; border-radius: 4px; overflow: hidden;">
                            <div style="background: #38BDF8; width: {min(100, readiness.get('syllabus_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--nexus-text-sub); margin-bottom: 2px;">
                            <span>Practice</span>
                            <strong style="color: var(--nexus-text-title);">{readiness.get('understanding_pct', 0)}%</strong>
                        </div>
                        <div style="background: rgba(255,255,255,0.06); height: 5px; border-radius: 4px; overflow: hidden;">
                            <div style="background: #818CF8; width: {min(100, readiness.get('understanding_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.76rem; color: var(--nexus-text-sub); margin-bottom: 2px;">
                            <span>Revision & Recall</span>
                            <strong style="color: var(--nexus-text-title);">{readiness.get('revision_pct', 0)}%</strong>
                        </div>
                        <div style="background: rgba(255,255,255,0.06); height: 5px; border-radius: 4px; overflow: hidden;">
                            <div style="background: #F59E0B; width: {min(100, readiness.get('revision_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        """)
        if st.button("📊 View Breakdown", use_container_width=True, key="dash_view_readiness_bd"):
            st.session_state["current_page"] = "📊 Analytics"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    with col_countdown:
        if next_term:
            t_name = next_term.get("name", "Term Exam")
            t_date = next_term.get("exam_date", "")
            days_left = next_term.get("days_remaining", 0)
            if not days_left and t_date:
                try:
                    ex_dt = datetime.datetime.strptime(str(t_date)[:10], "%Y-%m-%d").date()
                    days_left = max(0, (ex_dt - datetime.date.today()).days)
                except Exception:
                    days_left = 0

            # Urgency tiering: <7 urgent (red), 7-21 attention (orange), >21 normal (cyan)
            if days_left <= 7:
                cd_color = "#EF4444"
                cd_status = "URGENT"
            elif days_left <= 21:
                cd_color = "#F97316"
                cd_status = "ATTENTION"
            else:
                cd_color = "#38BDF8"
                cd_status = "ON TRACK"

            render_html(f"""
                <div class="nexus-card" style="height: 100%; border-top: 3px solid {cd_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: {cd_color}; text-transform: uppercase; letter-spacing: 0.06em;">
                            EXAM COUNTDOWN
                        </span>
                        <span style="background: rgba(255,255,255,0.06); color: {cd_color}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;">
                            {cd_status}
                        </span>
                    </div>
                    <div style="font-weight: 800; font-size: 1.15rem; color: var(--nexus-text-title); margin-bottom: 2px;">
                        {t_name}
                    </div>
                    <div style="font-size: 0.82rem; color: var(--nexus-text-sub); margin-bottom: 14px;">
                        📅 Target Date: <strong style="color: var(--nexus-text-title);">{t_date or 'Scheduled'}</strong>
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 12px;">
                        <div style="font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 900; color: {cd_color}; line-height: 1;">
                            {days_left}
                        </div>
                        <div style="font-size: 0.95rem; color: var(--nexus-text-sub); font-weight: 600;">Days Remaining</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.06); height: 5px; border-radius: 4px; overflow: hidden; margin-top: 10px;">
                        <div style="background: {cd_color}; width: {max(5, min(100, 100 - days_left))}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
            """)
        else:
            render_html("""
                <div class="nexus-card" style="height: 100%; text-align: center; display: flex; flex-direction: column; justify-content: center; padding: 24px;">
                    <div style="font-size: 1.8rem; margin-bottom: 6px;">📅</div>
                    <strong style="color: var(--nexus-text-title); font-size: 1.05rem;">No Upcoming Terms Scheduled</strong>
                    <div style="font-size: 0.82rem; color: var(--nexus-text-sub); margin: 6px 0 14px 0;">
                        Configure your exam terms & target dates in Settings.
                    </div>
                </div>
            """)

        if st.button("🗓️ Configure Exam Terms", use_container_width=True, key="dash_cfg_terms_btn"):
            st.session_state["current_page"] = "⚙️ Settings"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    render_html("<div style='margin-top: 18px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # 4. DASHBOARD STAT STRIP (4 Compact Cards)
    # ══════════════════════════════════════════════════════════════════════════
    focus_data_7d = get_focus_analytics(user_id, days=7) or {}
    total_focus_min = focus_data_7d.get("total_minutes", 0)
    total_focus_hours = round(total_focus_min / 60.0, 1)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #38BDF8;">
                <div class="nexus-kpi-label">⏱️ Study Time (7d)</div>
                <div class="nexus-kpi-val" style="color: #38BDF8;">{total_focus_hours} <span style="font-size: 0.95rem; color: var(--nexus-text-sub); font-weight: 600;">hrs</span></div>
                <div class="nexus-kpi-sub">{total_focus_min}m recorded</div>
            </div>
        """)
    with s2:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #F97316;">
                <div class="nexus-kpi-label">🔥 Current Streak</div>
                <div class="nexus-kpi-val" style="color: #F97316;">{xp_info.get('streak', 0)} <span style="font-size: 0.95rem; color: var(--nexus-text-sub); font-weight: 600;">Days</span></div>
                <div class="nexus-kpi-sub">Best: <strong>{xp_info.get('best_streak', xp_info.get('streak', 0))}d</strong></div>
            </div>
        """)
    with s3:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #10B981;">
                <div class="nexus-kpi-label">📚 Topics Done</div>
                <div class="nexus-kpi-val" style="color: #10B981;">{stats.get('completed_topics', 0)} <span style="font-size: 0.95rem; color: var(--nexus-text-sub); font-weight: 600;">/ {stats.get('total_topics', 0)}</span></div>
                <div class="nexus-kpi-sub">{stats.get('percent_completed', 0.0)}% syllabus complete</div>
            </div>
        """)
    with s4:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #818CF8;">
                <div class="nexus-kpi-label">⭐ Total XP</div>
                <div class="nexus-kpi-val" style="color: #818CF8;">{xp_info.get('total_xp', 0)}</div>
                <div class="nexus-kpi-sub">Lvl {xp_info.get('level', 1)} • {xp_info.get('title', 'Novice')}</div>
            </div>
        """)

    render_html("<div style='margin-top: 18px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # 5. STUDY ACTIVITY (7D / 14D / 30D Filter)
    # ══════════════════════════════════════════════════════════════════════════
    col_act_title, col_act_filter = st.columns([3, 1])
    with col_act_title:
        render_html("""
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title);">
                📈 Study Activity & Consistency
            </div>
            <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin-bottom: 8px;">
                How consistently am I studying?
            </div>
        """)
    with col_act_filter:
        timeframe = st.selectbox("Timeframe", [7, 14, 30], format_func=lambda x: f"{x} Days", key="dash_chart_tf", label_visibility="collapsed")

    chart_focus_data = get_focus_analytics(user_id, days=timeframe) or {}
    daily_breakdown = chart_focus_data.get("daily_breakdown", [])

    if not daily_breakdown:
        today = datetime.date.today()
        dates_list = [(today - datetime.timedelta(days=i)).strftime("%a %d") for i in range(timeframe - 1, -1, -1)]
        mins_list = [0] * len(dates_list)
    else:
        dates_list = [datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %d") if len(d["date"]) == 10 else d["date"] for d in daily_breakdown]
        mins_list = [d.get("minutes", 0) for d in daily_breakdown]

    text_col = "#FFFFFF" if is_dark else "#0F172A"
    grid_col = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)"
    axis_col = "#94A3B8" if is_dark else "#64748B"

    fig_act = go.Figure()
    fig_act.add_trace(go.Bar(
        x=dates_list,
        y=mins_list,
        marker=dict(
            color=mins_list,
            colorscale=[[0, "#0284C7"], [1, "#38BDF8"]],
            line=dict(width=0)
        ),
        text=[f"{m}m" if m > 0 else "" for m in mins_list],
        textposition="outside",
        textfont=dict(color=text_col, size=10, family="Inter")
    ))

    fig_act.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=15, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color=axis_col, tickfont=dict(size=10, color=axis_col)),
        yaxis=dict(showgrid=True, gridcolor=grid_col, color=axis_col, tickfont=dict(size=9, color=axis_col), zeroline=False),
        showlegend=False
    )
    st.plotly_chart(fig_act, use_container_width=True, config={"displayModeBar": False})

    render_html("<div style='margin-top: 18px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # 6 & 7 & 8: SMART PRIORITIES, WEAK AREAS & RECENT ACTIVITY (3 Columns)
    # ══════════════════════════════════════════════════════════════════════════
    col_prios, col_weak, col_recent = st.columns([1.4, 1.1, 1.1])

    with col_prios:
        render_html("""
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                🎯 Smart Priorities (Top 3)
            </div>
        """)
        if not priorities:
            render_html("""
                <div class="nexus-card" style="padding: 16px; text-align: center;">
                    <div style="color: #10B981; font-weight: 700; font-size: 0.95rem;">🎉 No Critical Bottlenecks</div>
                    <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin-top: 4px;">Syllabus pacing is in good standing across all subjects.</div>
                </div>
            """)
        else:
            for p in priorities[:3]:
                reasons_str = " • ".join(p.get("reasons", []))
                p_badge_color = p.get("badge_color", "#38BDF8")
                c_p_card, c_p_act = st.columns([3.5, 1.5])
                with c_p_card:
                    render_html(f"""
                        <div class="priority-item-card" style="border-left-color: {p_badge_color}; margin-bottom: 8px; padding: 8px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                                <span class="nexus-pill-{p['tier'].lower()}" style="font-size: 0.66rem; padding: 1px 6px;">{p['tier_icon']} {p['tier']}</span>
                                <span style="font-size: 0.74rem; font-weight: 700; color: {p.get('subject_color', '#38BDF8')};">{p['subject_name']}</span>
                            </div>
                            <div style="font-size: 0.9rem; font-weight: 700; color: var(--nexus-text-title);">{p['topic_name']}</div>
                            <div style="font-size: 0.74rem; color: var(--nexus-text-sub);">{reasons_str}</div>
                        </div>
                    """)
                with c_p_act:
                    st.write("")
                    if st.button("Study Now", key=f"dash_prio_sn_{p['topic_id']}", use_container_width=True):
                        st.session_state["focus_target_topic_id"] = p["topic_id"]
                        st.session_state["current_page"] = "⏱️ Focus"
                        st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                        st.rerun()

    with col_weak:
        render_html("""
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                ⚠️ Weak Areas
            </div>
        """)
        if not weak_areas:
            render_html("""
                <div class="nexus-card" style="padding: 16px; text-align: center;">
                    <div style="color: #10B981; font-weight: 700; font-size: 0.95rem;">✨ High Confidence</div>
                    <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin-top: 4px;">No topics rated below 3 stars.</div>
                </div>
            """)
        else:
            for w in weak_areas[:3]:
                stars_str = "★" * int(w.get("understanding", 2)) + "☆" * (5 - int(w.get("understanding", 2)))
                render_html(f"""
                    <div style="padding: 8px 12px; margin-bottom: 8px; background: var(--nexus-card-bg); border: 1px solid var(--nexus-card-border); border-left: 3px solid #EF4444; border-radius: 10px;">
                        <div style="font-size: 0.74rem; font-weight: 700; color: #EF4444;">{w.get('subject_name', 'Subject')}</div>
                        <div style="font-size: 0.88rem; font-weight: 700; color: var(--nexus-text-title);">{w.get('topic_name', 'Topic')}</div>
                        <div style="font-size: 0.75rem; color: #F59E0B; margin-top: 2px;">{stars_str} ({w.get('understanding', 2)}/5)</div>
                    </div>
                """)

    with col_recent:
        render_html("""
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                🕒 Recent Activity
            </div>
        """)
        if not recent_activity:
            render_html("""
                <div class="nexus-card" style="padding: 16px; text-align: center;">
                    <div style="font-size: 0.85rem; color: var(--nexus-text-sub);">No activity logged yet today. Complete a topic or start a focus session to begin!</div>
                </div>
            """)
        else:
            for act in recent_activity[:4]:
                render_html(f"""
                    <div style="padding: 6px 10px; margin-bottom: 6px; background: rgba(255,255,255,0.02); border-left: 2px solid var(--nexus-accent); border-radius: 6px; font-size: 0.8rem;">
                        <div style="font-weight: 600; color: var(--nexus-text-title);">{act.get('title', 'Activity')}</div>
                        <div style="font-size: 0.72rem; color: var(--nexus-text-muted);">{act.get('timestamp_relative', 'Recent')}</div>
                    </div>
                """)
