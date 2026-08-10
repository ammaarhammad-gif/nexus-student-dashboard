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
    get_recent_activity_stream, get_weak_areas
)
from preloaded_syllabi import preload_standard_syllabus
from styles import render_metric_card


def render_dashboard_page(user_id: int):
    profile = get_user_profile(user_id)
    user_name = profile.get("name", "Student")
    class_name = profile.get("class_name", "Class 10")
    board = profile.get("board", "CBSE")
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # Fetch stats and auto-preload if fresh
    stats = get_overall_stats(user_id)
    subjects_with_stats = get_all_subjects_with_stats(user_id)
    if not subjects_with_stats:
        preload_standard_syllabus(user_id, board, class_name)
        stats = get_overall_stats(user_id)
        subjects_with_stats = get_all_subjects_with_stats(user_id)

    xp_info = get_user_xp_summary(user_id)
    readiness = calculate_exam_readiness_score(user_id)
    priorities = get_top_nexus_priorities(user_id, limit=3)
    queue = get_revision_queue(user_id)
    unreviewed_mistakes = get_unreviewed_mistakes_for_quiz(user_id, limit=10)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_plans = get_daily_plans(user_id, today_str)

    # ══════════════════════════════════════════════════════════════════════════
    # 1. TOP HEADER (Level, Rank, XP Progress, Compact Theme Switch, Logout)
    # ══════════════════════════════════════════════════════════════════════════
    col_hdr_left, col_hdr_right = st.columns([3, 1.2])

    with col_hdr_left:
        xp_pct = min(100, round((xp_info['total_xp'] / max(1, xp_info['next_xp'])) * 100))
        st.markdown(f"""
            <div class="nexus-stat-capsule" style="margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="background: linear-gradient(135deg, #38BDF8, #0284C7); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: 800; color: #FFFFFF; box-shadow: 0 4px 14px rgba(56,189,248,0.3);">
                        {xp_info['level']}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 0.78rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em;">
                                RANK: {xp_info['title']}
                            </span>
                            <span style="font-size: 0.75rem; color: #F97316; font-weight: 700;">
                                🔥 {xp_info['streak']}d Streak
                            </span>
                        </div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: var(--nexus-text-title);">
                            {xp_info['total_xp']} <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">/ {xp_info['next_xp']} XP ({xp_pct}%)</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_hdr_right:
        c_th_btn, c_lo_btn = st.columns([1.2, 1])
        with c_th_btn:
            theme_target = "Light" if is_dark else "Dark"
            theme_icon = "☀️" if is_dark else "🌙"
            if st.button(f"{theme_icon} {theme_target}", key="dash_compact_theme_toggle", use_container_width=True):
                set_user_theme(user_id, theme_target)
                st.session_state["theme_mode"] = theme_target
                st.rerun()
        with c_lo_btn:
            if st.button("🚪 Logout", key="dash_logout_btn", use_container_width=True):
                for k in ["authenticated", "user_id", "username", "session_token"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # 2. TIME-AWARE GREETING & TODAY'S MISSION
    # ══════════════════════════════════════════════════════════════════════════
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        time_greeting = "Good morning"
    elif current_hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">
                ACADEMIC COMMAND CENTER • {board} {class_name}
            </div>
            <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--nexus-text-title); margin: 0;">
                {time_greeting}, {user_name} 👋 Ready for your next mission?
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 3. TODAY'S MISSION (Primary Decision Engine)
    # ══════════════════════════════════════════════════════════════════════════
    top_priority_topic = priorities[0] if priorities else None
    overdue_count = len(queue.get("overdue", []))
    due_today_count = len(queue.get("due_today", []))
    pending_tasks_count = len([t for t in today_plans if not t["is_completed"]])

    st.markdown("""
        <div class="nexus-mission-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.08em;">
                        ⚡ STRATEGIC FOCUS
                    </div>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--nexus-text-title); margin: 2px 0 0 0;">
                        Today's Mission
                    </h2>
                </div>
                <div style="font-size: 0.85rem; color: var(--nexus-text-sub);">
                    Curated actions for maximum retention & score acceleration
                </div>
            </div>
    """, unsafe_allow_html=True)

    # Mission items list
    mission_items = []
    if overdue_count > 0:
        mission_items.append((
            "🔴 Overdue Spaced Revisions",
            f"{overdue_count} topics have crossed their optimal retention threshold",
            "#EF4444",
            "🧠 Review",
            "review_queue"
        ))
    if top_priority_topic:
        mission_items.append((
            f"🎯 Master Priority: {top_priority_topic['topic_name']}",
            f"{top_priority_topic['subject_name']} › {top_priority_topic['chapter_name']} ({' • '.join(top_priority_topic['reasons'])})",
            "#38BDF8",
            "⏱️ Focus",
            "focus_top"
        ))
    if len(unreviewed_mistakes) > 0:
        mission_items.append((
            "❌ Eliminate Recurring Errors",
            f"{len(unreviewed_mistakes)} unreviewed mistakes awaiting targeted re-testing in Mistake Re-Quiz",
            "#F97316",
            "🎯 Practice",
            "practice_mistakes"
        ))
    if pending_tasks_count > 0:
        mission_items.append((
            "📋 Daily Study Tasks",
            f"{pending_tasks_count} study tasks remaining on today's planner schedule",
            "#22C55E",
            "🗓️ Planner",
            "planner_daily"
        ))

    if not mission_items:
        mission_items.append((
            "✨ Perfect Pace!",
            "All revisions caught up and daily milestones achieved. Explore new syllabus topics in Learn Hub.",
            "#22C55E",
            "📚 Learn",
            "learn_hub"
        ))

    for m_title, m_desc, m_col, m_page, m_key in mission_items[:4]:
        st.markdown(f"""
            <div class="nexus-mission-item">
                <div>
                    <strong style="color: {m_col}; font-size: 0.95rem;">{m_title}</strong>
                    <div style="font-size: 0.82rem; color: var(--nexus-text-sub); margin-top: 2px;">{m_desc}</div>
                </div>
                <div>
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                        {m_page}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Primary Action CTA Button
    c_cta1, c_cta2 = st.columns([2, 1])
    with c_cta1:
        if top_priority_topic:
            btn_txt = f"🚀 Launch Session: {top_priority_topic['topic_name']} ({top_priority_topic['subject_name']})"
        else:
            btn_txt = "🚀 Start Recommended Focus Session"

        if st.button(btn_txt, type="primary", use_container_width=True, key="dash_primary_mission_launch_btn"):
            if top_priority_topic:
                st.session_state["focus_target_topic_id"] = top_priority_topic["topic_id"]
            st.session_state["current_page"] = "⏱️ Focus"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    with c_cta2:
        if st.button("🤖 Consult Nexus AI Daily Blueprint", use_container_width=True, key="dash_mission_ai_btn"):
            st.session_state["current_page"] = "🤖 Nexus AI"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 4. EXAM READINESS & EXAM COUNTDOWN (2 Columns)
    # ══════════════════════════════════════════════════════════════════════════
    col_ready, col_count = st.columns([1.2, 1])

    with col_ready:
        st.subheader("🎓 Exam Readiness Score")
        r_score = readiness["readiness_score"]
        r_color = "#22C55E" if r_score >= 80 else ("#38BDF8" if r_score >= 60 else ("#F59E0B" if r_score >= 40 else "#EF4444"))

        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; padding: 20px 18px; border-top: 4px solid {r_color};">
                <div style="font-size: 0.78rem; font-weight: 700; color: {r_color}; text-transform: uppercase; letter-spacing: 0.06em;">
                    COMPOSITE PREPAREDNESS INDEX
                </div>
                <div class="readiness-score-big" style="margin: 6px 0; color: {r_color};">
                    {r_score} <span style="font-size: 1.4rem; color: var(--nexus-text-sub);">/ 100</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0 10px 0; font-size: 0.82rem; text-align: left;">
                    <div style="background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 8px;">
                        📚 <strong>Syllabus:</strong> {readiness['syllabus_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 8px;">
                        🧠 <strong>Mastery:</strong> {readiness['understanding_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 8px;">
                        🔄 <strong>Revisions:</strong> {readiness['revision_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 8px;">
                        ❌ <strong>Mistakes:</strong> {readiness.get('factors', {}).get('mistake_resolution', 100)}%
                    </div>
                </div>
                <div style="text-align: left; font-size: 0.82rem; color: var(--nexus-text-sub); border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                    <strong style="color: #38BDF8;">⚡ Strategic Focus:</strong> {readiness['recommendations'][0] if readiness['recommendations'] else 'Maintain active daily review velocity.'}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_count:
        st.subheader("⏳ Upcoming Exams")
        active_terms = get_active_upcoming_terms(user_id)
        if not active_terms:
            st.markdown("""
                <div class="readiness-container" style="text-align: center; padding: 28px 16px;">
                    <div style="font-size: 1.8rem; margin-bottom: 6px;">📅</div>
                    <strong style="color: var(--nexus-text-title); font-size: 1.0rem;">No Upcoming Exams Configured</strong>
                    <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin: 6px 0 14px 0;">
                        Add your Term & Board exam dates in Settings to unlock dynamic countdown clocks.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("➕ Configure Exam Dates", use_container_width=True, key="dash_add_exam_btn"):
                st.session_state["current_page"] = "⚙️ Settings"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()
        else:
            for t in active_terms[:3]:
                days = t["days_remaining"]
                badge_bg = "#EF4444" if days <= 7 else ("#F97316" if days <= 21 else "#38BDF8")
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {badge_bg}; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; font-size: 1.05rem; color: var(--nexus-text-title);">
                                    {t['name']}
                                </div>
                                <div style="font-size: 0.8rem; color: var(--nexus-text-sub);">
                                    📅 {t['exam_date']}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.4rem; font-weight: 800; color: {badge_bg};">
                                    {days}
                                </span>
                                <div style="font-size: 0.72rem; color: var(--nexus-text-sub); text-transform: uppercase;">Days Left</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. SMART PRIORITY (Top 3 Topics with Direct Actions) & TODAY'S PROGRESS
    # ══════════════════════════════════════════════════════════════════════════
    col_prio_list, col_today_strip = st.columns([1.4, 1])

    with col_prio_list:
        st.subheader("🎯 Smart Priorities (Top 3)")
        if not priorities:
            st.success("🎉 Outstanding! No critical syllabus bottlenecks detected.")
        else:
            for p in priorities[:3]:
                reasons_str = " • ".join(p["reasons"])
                c_p_card, c_p_act = st.columns([4, 1.2])
                with c_p_card:
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {p['badge_color']}; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <div style="display: flex; gap: 6px; align-items: center;">
                                    <span class="nexus-pill-{p['tier'].lower()}">{p['tier_icon']} {p['tier']}</span>
                                    <span style="font-size: 0.8rem; font-weight: 700; color: {p.get('subject_color', '#38BDF8')};">{p['subject_name']}</span>
                                </div>
                                <span style="font-size: 0.75rem; font-weight: 700; color: {p['badge_color']};">Score: {p['score']}</span>
                            </div>
                            <div style="font-size: 1.02rem; font-weight: 700; color: var(--nexus-text-title);">
                                {p['topic_name']}
                            </div>
                            <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-top: 2px;">
                                {p['chapter_name']} {f'• <span style="color: {p["badge_color"]};">{reasons_str}</span>' if reasons_str else ''}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_p_act:
                    st.write("")
                    if st.button("⏱️ Focus", key=f"dash_prio_foc_{p['topic_id']}", use_container_width=True):
                        st.session_state["focus_target_topic_id"] = p["topic_id"]
                        st.session_state["current_page"] = "⏱️ Focus"
                        st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                        st.rerun()

    with col_today_strip:
        st.subheader("📊 Today's Momentum")
        st.markdown(f"""
            <div class="readiness-container" style="padding: 16px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; border-left: 3px solid #38BDF8;">
                        <div style="font-size: 0.72rem; color: var(--nexus-text-sub); text-transform: uppercase;">Tasks Done</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #38BDF8;">{len([t for t in today_plans if t['is_completed']])}/{len(today_plans)}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; border-left: 3px solid #F97316;">
                        <div style="font-size: 0.72rem; color: var(--nexus-text-sub); text-transform: uppercase;">Streak</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #F97316;">{xp_info['streak']} Days</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; border-left: 3px solid #22C55E;">
                        <div style="font-size: 0.72rem; color: var(--nexus-text-sub); text-transform: uppercase;">Syllabus</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #22C55E;">{stats['percent_completed']}%</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 10px; border-left: 3px solid #A855F7;">
                        <div style="font-size: 0.72rem; color: var(--nexus-text-sub); text-transform: uppercase;">Nexus Level</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #A855F7;">Lvl {xp_info['level']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 6. WEAK AREAS & RECENT ACTIVITY (2 Columns)
    # ══════════════════════════════════════════════════════════════════════════
    col_weak, col_rec = st.columns([1.2, 1.2])

    with col_weak:
        st.subheader("⚠️ Weak Areas Needing Remediation")
        weak_list = get_weak_areas(user_id, limit=4)
        if not weak_list:
            st.info("✨ No weak areas recorded yet. Complete quizzes or rate topic understanding in Learn Hub.")
        else:
            for w in weak_list:
                und_stars = "⭐" * max(1, min(5, w.get("understanding", 1)))
                m_count = w.get("mistake_count", 0)
                m_str = f" • <span style='color: #EF4444;'>{m_count} Mistake{'s' if m_count!=1 else ''}</span>" if m_count > 0 else ""
                
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: #EF4444; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: var(--nexus-text-title); font-size: 0.95rem;">{w['topic_name']}</span>
                                <div style="font-size: 0.78rem; color: var(--nexus-text-sub);">
                                    {w['subject_name']} › {w['chapter_name']}{m_str}
                                </div>
                            </div>
                            <div style="font-size: 0.85rem; color: #F59E0B; font-weight: 700;">
                                {und_stars}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with col_rec:
        st.subheader("📜 Recent Activity Stream")
        activity_stream = get_recent_activity_stream(user_id, limit=4)
        if not activity_stream:
            st.info("No recent study sessions or quizzes yet. Launch a session to populate your log!")
        else:
            for a in activity_stream:
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {a['tag_color']}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; color: var(--nexus-text-title); font-size: 0.92rem;">
                                    {a['icon']} {a['title']}
                                </div>
                                <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin-top: 2px;">
                                    {a['subtitle']}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 0.75rem; font-weight: 700; color: {a['tag_color']};">
                                    {a['tag']}
                                </span>
                                <div style="font-size: 0.7rem; color: var(--nexus-text-sub);">{a['timestamp']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
