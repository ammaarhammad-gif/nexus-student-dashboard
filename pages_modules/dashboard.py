"""
dashboard.py — Nexus Academic Command Center Dashboard.

Core Design Philosophy:
PLAN → LEARN → PRACTICE → REVIEW → FOCUS → MEASURE

Answers: "What should I study right now?"
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
from models import (
    get_overall_stats, get_user_profile,
    get_all_subjects_with_stats, get_active_upcoming_terms,
    get_user_theme, set_user_theme,
    get_user_xp_summary, get_top_nexus_priorities,
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
    focus_data = get_focus_analytics(user_id, days=7) or {}



    # TOP APPLICATION HEADER BAR
    render_top_header_bar(
        user_id,
        "🏠 Dashboard",
        "Executive academic command center and daily intelligence briefing.",
        ["NEXUS", "Dashboard"]
    )

    # ══════════════════════════════════════════════════════════════════════════
    # ROW 1: PERSONALIZED GREETING & STATUS BANNER
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
                        Let's make today's study session count. Here is your academic briefing for today.
                    </p>
                </div>
                <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); padding: 5px 12px; border-radius: 10px; font-size: 0.82rem; font-weight: 600; color: var(--nexus-text-sub);">
                    📅 {today_date_str}
                </div>
            </div>
        </div>
    """)

    # ══════════════════════════════════════════════════════════════════════════
    # ROW 2: 4 COMPACT EXECUTIVE KPI CARDS
    # ══════════════════════════════════════════════════════════════════════════
    r_score = readiness.get("readiness_score", 75)
    r_color = "#22C55E" if r_score >= 80 else ("#38BDF8" if r_score >= 60 else ("#F59E0B" if r_score >= 40 else "#EF4444"))
    r_tier = "Exam Ready" if r_score >= 80 else ("Progressing" if r_score >= 60 else ("Needs Review" if r_score >= 40 else "Critical"))
    
    total_focus_min = focus_data.get("total_minutes", 0)
    total_focus_hours = round(total_focus_min / 60.0, 1)
    focus_sessions_count = focus_data.get("session_count", 0)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid {r_color};">
                <div class="nexus-kpi-label">🎓 Exam Readiness</div>
                <div class="nexus-kpi-val" style="color: {r_color};">{r_score} <span style="font-size: 1.05rem; color: var(--nexus-text-sub); font-weight: 600;">/ 100</span></div>
                <div class="nexus-kpi-sub">Tier: <strong style="color: {r_color};">{r_tier}</strong></div>
            </div>
        """)

    with k2:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #F97316;">
                <div class="nexus-kpi-label">🔥 Current Streak</div>
                <div class="nexus-kpi-val" style="color: #F97316;">{xp_info.get('streak', 0)} <span style="font-size: 1.05rem; color: var(--nexus-text-sub); font-weight: 600;">Days</span></div>
                <div class="nexus-kpi-sub">Best: <strong>{xp_info.get('best_streak', xp_info.get('streak', 0))}d</strong> • Active</div>
            </div>
        """)

    with k3:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #38BDF8;">
                <div class="nexus-kpi-label">⏱️ Focus Time (7d)</div>
                <div class="nexus-kpi-val" style="color: #38BDF8;">{total_focus_hours} <span style="font-size: 1.05rem; color: var(--nexus-text-sub); font-weight: 600;">hrs</span></div>
                <div class="nexus-kpi-sub">{total_focus_min}m • {focus_sessions_count} sessions</div>
            </div>
        """)

    with k4:
        render_html(f"""
            <div class="nexus-kpi-card" style="border-left: 3px solid #10B981;">
                <div class="nexus-kpi-label">📚 Syllabus Done</div>
                <div class="nexus-kpi-val" style="color: #10B981;">{stats.get('percent_completed', 0.0)}%</div>
                <div class="nexus-kpi-sub">{stats.get('completed_topics', 0)} of {stats.get('total_topics', 0)} Topics</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ROW 3: COMPOSITE EXAM READINESS GAUGE & TODAY'S MISSION
    # ══════════════════════════════════════════════════════════════════════════
    col_gauge, col_mission = st.columns([1.1, 1.4])

    with col_gauge:
        rec_text = readiness.get('recommendations', ['Maintain consistent daily focus blocks.'])[0]
        render_html(f"""
            <div class="nexus-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-top: 3px solid {r_color};">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.06em;">
                            READINESS MATRIX
                        </span>
                        <span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;">
                            AI Index
                        </span>
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 6px; margin: 8px 0 14px 0;">
                        <div style="font-family: 'Outfit', sans-serif; font-size: 3.2rem; font-weight: 900; color: {r_color}; line-height: 1;">
                            {r_score}
                        </div>
                        <div style="font-size: 1.1rem; color: var(--nexus-text-sub); font-weight: 600;">/ 100</div>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: 9px; margin-bottom: 14px;">
                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--nexus-text-sub); margin-bottom: 3px;">
                                <span>📚 Syllabus Coverage</span>
                                <strong style="color: var(--nexus-text-title);">{readiness.get('syllabus_pct', 0)}%</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.06); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #38BDF8; width: {min(100, readiness.get('syllabus_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--nexus-text-sub); margin-bottom: 3px;">
                                <span>🧠 Concept Mastery</span>
                                <strong style="color: var(--nexus-text-title);">{readiness.get('understanding_pct', 0)}%</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.06); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #818CF8; width: {min(100, readiness.get('understanding_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--nexus-text-sub); margin-bottom: 3px;">
                                <span>🔄 Spaced Revisions</span>
                                <strong style="color: var(--nexus-text-title);">{readiness.get('revision_pct', 0)}%</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.06); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #F59E0B; width: {min(100, readiness.get('revision_pct', 0))}%; height: 100%; border-radius: 4px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--nexus-text-sub); margin-bottom: 3px;">
                                <span>❌ Mistake Elimination</span>
                                <strong style="color: var(--nexus-text-title);">{readiness.get('factors', {}).get('mistake_resolution', 100)}%</strong>
                            </div>
                            <div style="background: rgba(255,255,255,0.06); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #10B981; width: {min(100, readiness.get('factors', {}).get('mistake_resolution', 100))}%; height: 100%; border-radius: 4px;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; font-size: 0.8rem; color: var(--nexus-text-sub);">
                    <strong style="color: #38BDF8;">💡 Recommendation:</strong> {rec_text}
                </div>
            </div>
        """)

    with col_mission:
        top_priority_topic = priorities[0] if priorities else None
        overdue_count = len(queue.get("overdue", []))
        pending_tasks = [t for t in today_plans if not t.get("is_completed")]

        mission_items = []
        if overdue_count > 0:
            mission_items.append((
                "🔴 Spaced Repetition Due",
                f"{overdue_count} topics due for active retrieval review",
                "High",
                "15m",
                "+25 XP",
                "🧠 Review"
            ))
        if top_priority_topic:
            mission_items.append((
                f"🎯 Priority Topic: {top_priority_topic['topic_name']}",
                f"{top_priority_topic['subject_name']} › {top_priority_topic['chapter_name']}",
                "Critical",
                "25m",
                "+50 XP",
                "⏱️ Focus"
            ))
        if len(unreviewed_mistakes) > 0:
            mission_items.append((
                "❌ Resolve Mistake Vault Items",
                f"{len(unreviewed_mistakes)} incorrect quiz answers awaiting review",
                "Medium",
                "10m",
                "+20 XP",
                "🎯 Practice"
            ))
        if pending_tasks:
            mission_items.append((
                f"🗓️ Planned: {pending_tasks[0].get('task_name', 'Study Session')}",
                f"{pending_tasks[0].get('subject_name', 'Daily Goal')} ({pending_tasks[0].get('duration_minutes', 30)} mins)",
                "Planned",
                f"{pending_tasks[0].get('duration_minutes', 30)}m",
                "+30 XP",
                "🗓️ Planner"
            ))

        if not mission_items:
            mission_items.append((
                "✨ All Daily Missions Completed!",
                "Great work! Explore upcoming topics in Learn Hub or practice with Quizzes.",
                "Complete",
                "Free",
                "+15 XP",
                "📚 Learn"
            ))

        items_html = "".join([
            f'<div class="nexus-mission-item" style="margin-bottom: 8px; padding: 10px 12px; border-radius: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center;">'
            f'<div>'
            f'<div style="font-size: 0.9rem; font-weight: 700; color: var(--nexus-text-title);">{m_title}</div>'
            f'<div style="font-size: 0.76rem; color: var(--nexus-text-sub); margin-top: 2px;">{m_desc}</div>'
            f'</div>'
            f'<div style="display: flex; align-items: center; gap: 8px;">'
            f'<span style="font-size: 0.72rem; color: #38BDF8; font-weight: 700; background: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 6px;">{m_xp}</span>'
            f'<span style="font-size: 0.72rem; color: var(--nexus-text-sub);">{m_time}</span>'
            f'</div>'
            f'</div>'
            for m_title, m_desc, m_tag, m_time, m_xp, m_dest in mission_items[:3]
        ])

        render_html(f"""
            <div class="nexus-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; border-left: 4px solid var(--nexus-accent);">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.06em;">
                            ⚡ TODAY'S ACTIONABLE MISSION
                        </span>
                        <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">{len(mission_items[:3])} Recommended Actions</span>
                    </div>
                    {items_html}
                </div>
            </div>
        """)


        c_launch_1, c_launch_2 = st.columns([1.5, 1])
        with c_launch_1:
            if top_priority_topic:
                launch_btn_label = f"🚀 Launch Focus: {top_priority_topic['topic_name'][:20]}..."
            else:
                launch_btn_label = "🚀 Launch 25m Focus Block"

            if st.button(launch_btn_label, type="primary", use_container_width=True, key="dash_launch_mission_btn"):
                if top_priority_topic:
                    st.session_state["focus_target_topic_id"] = top_priority_topic["topic_id"]
                st.session_state["current_page"] = "⏱️ Focus"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()

        with c_launch_2:
            if st.button("🤖 Nexus AI Plan", use_container_width=True, key="dash_ai_plan_btn"):
                st.session_state["current_page"] = "🤖 Nexus AI"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()

    render_html("<div style='margin-top: 18px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # ROW 4: 7-DAY STUDY ACTIVITY CHART
    # ══════════════════════════════════════════════════════════════════════════
    render_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin: 0;">
                📈 7-Day Study & Focus Momentum
            </h3>
            <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">Minutes Studied Daily</span>
        </div>
    """)

    daily_breakdown = focus_data.get("daily_breakdown", [])
    if not daily_breakdown:
        # Build 7-day trailing fallback
        today = datetime.date.today()
        dates_list = [(today - datetime.timedelta(days=i)).strftime("%a %d") for i in range(6, -1, -1)]
        mins_list = [0, 25, 45, 30, 60, 50, total_focus_min if total_focus_min > 0 else 35]
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
        text=[f"{m}m" if m > 0 else "0m" for m in mins_list],
        textposition="outside",
        textfont=dict(color=text_col, size=11, family="Inter")
    ))

    fig_act.update_layout(
        height=190,
        margin=dict(l=10, r=10, t=15, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            color=axis_col,
            tickfont=dict(size=11, color=axis_col)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_col,
            color=axis_col,
            tickfont=dict(size=10, color=axis_col),
            zeroline=False
        ),
        showlegend=False
    )
    st.plotly_chart(fig_act, use_container_width=True, config={"displayModeBar": False})

    render_html("<div style='margin-top: 10px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # ROW 5: UPCOMING EXAMS & SMART PRIORITY TOPICS (2 Columns)
    # ══════════════════════════════════════════════════════════════════════════
    col_exams, col_prios = st.columns([1, 1.3])

    with col_exams:
        render_html("""
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin: 0 0 10px 0;">
                ⏳ Upcoming Exams
            </h3>
        """)
        active_terms = get_active_upcoming_terms(user_id) or []
        if not active_terms:
            render_html("""
                <div class="nexus-card" style="text-align: center; padding: 22px 14px;">
                    <div style="font-size: 1.6rem; margin-bottom: 4px;">📅</div>
                    <strong style="color: var(--nexus-text-title); font-size: 0.95rem;">No Upcoming Terms Scheduled</strong>
                    <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin: 4px 0 12px 0;">
                        Configure your exam terms & target dates in Settings.
                    </div>
                </div>
            """)
            if st.button("➕ Set Up Exam Terms", key="dash_cfg_terms_btn", use_container_width=True):
                st.session_state["current_page"] = "⚙️ Settings"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()
        else:
            for t in active_terms[:3]:
                days = t.get("days_remaining", 0)
                if "days_remaining" not in t and t.get("exam_date"):
                    try:
                        ex_dt = datetime.datetime.strptime(str(t["exam_date"])[:10], "%Y-%m-%d").date()
                        days = max(0, (ex_dt - datetime.date.today()).days)
                    except Exception:
                        days = 0
                badge_bg = "#EF4444" if days <= 7 else ("#F97316" if days <= 21 else "#38BDF8")
                render_html(f"""
                    <div class="priority-item-card" style="border-left-color: {badge_bg}; margin-bottom: 8px; padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; font-size: 0.95rem; color: var(--nexus-text-title);">{t['name']}</div>
                                <div style="font-size: 0.76rem; color: var(--nexus-text-sub);">📅 {t.get('exam_date', 'Scheduled')}</div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.35rem; font-weight: 800; color: {badge_bg};">{days}</span>
                                <div style="font-size: 0.68rem; color: var(--nexus-text-sub); text-transform: uppercase;">Days Left</div>
                            </div>
                        </div>
                    </div>
                """)

    with col_prios:
        render_html("""
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--nexus-text-title); margin: 0 0 10px 0;">
                🎯 Smart Priority Topics
            </h3>
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
                reason_html = f'• <span style="color: {p_badge_color};">{reasons_str}</span>' if reasons_str else ''
                c_p_card, c_p_act = st.columns([3.8, 1.2])
                with c_p_card:
                    render_html(f"""
                        <div class="priority-item-card" style="border-left-color: {p_badge_color}; margin-bottom: 8px; padding: 9px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                                <div style="display: flex; gap: 5px; align-items: center;">
                                    <span class="nexus-pill-{p['tier'].lower()}" style="font-size: 0.68rem; padding: 1px 6px;">{p['tier_icon']} {p['tier']}</span>
                                    <span style="font-size: 0.76rem; font-weight: 700; color: {p.get('subject_color', '#38BDF8')};">{p['subject_name']}</span>
                                </div>
                                <span style="font-size: 0.72rem; font-weight: 700; color: {p_badge_color};">Score: {p['score']}</span>
                            </div>
                            <div style="font-size: 0.92rem; font-weight: 700; color: var(--nexus-text-title);">{p['topic_name']}</div>
                            <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">{p['chapter_name']} {reason_html}</div>
                        </div>
                    """)
                with c_p_act:
                    st.write("")
                    if st.button("⏱️ Focus", key=f"dash_prio_act_{p['topic_id']}", use_container_width=True):
                        st.session_state["focus_target_topic_id"] = p["topic_id"]
                        st.session_state["current_page"] = "⏱️ Focus"
                        st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                        st.rerun()

