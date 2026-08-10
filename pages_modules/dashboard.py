"""
dashboard.py — Main dashboard page.

Shows: Welcome banner, overall stats, donut chart, per-subject breakdown,
and an exam countdown section.
"""

import streamlit as st
import plotly.graph_objects as go
import datetime
from models import (
    get_overall_stats, get_user_profile,
    get_all_subjects_with_stats, get_active_upcoming_terms,
    get_due_revisions, complete_revision, get_user_theme
)
from preloaded_syllabi import preload_standard_syllabus
from styles import render_header, render_metric_card, render_cinematic_welcome_banner


def render_dashboard_page(user_id: int):
    profile = get_user_profile(user_id)
    user_name = profile.get("name", "Student")
    class_name = profile.get("class_name", "Class 10")
    board = profile.get("board", "CBSE")
    class_info = f"{class_name} • {board} • {profile.get('academic_year', '')}"

    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # Fetch overall stats and all subjects with stats in 2 super-fast indexed queries
    stats = get_overall_stats(user_id)
    subjects_with_stats = get_all_subjects_with_stats(user_id)

    # Auto-load official board syllabus if user has no subjects
    if not subjects_with_stats:
        board = profile.get("board", "CBSE")
        class_name = profile.get("class_name", "Class 10")
        loaded = preload_standard_syllabus(user_id, board, class_name)
        if loaded:
            st.rerun()
        stats = get_overall_stats(user_id)
        subjects_with_stats = get_all_subjects_with_stats(user_id)


    # ── Ultra-Smooth Cinematic Animated Welcome Hero ──
    render_cinematic_welcome_banner(user_name, class_name, board, theme=user_theme)

    # ── Student OS Gamification & Streak Banner ──
    from models import get_user_xp_summary, get_top_nexus_priorities, calculate_exam_readiness_score
    xp_info = get_user_xp_summary(user_id)
    
    st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 14px; padding: 14px 20px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; backdrop-filter: blur(14px);">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="background: linear-gradient(135deg, #38BDF8, #0284C7); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: 800; color: #FFFFFF; box-shadow: 0 4px 14px rgba(56,189,248,0.3);">
                    {xp_info['level']}
                </div>
                <div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em;">
                        NEXUS RANK • {xp_info['title']}
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: var(--nexus-text-title);">
                        {xp_info['total_xp']} <span style="font-size: 0.8rem; color: #94A3B8;">/ {xp_info['next_xp']} XP</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="text-align: right;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #F97316; text-transform: uppercase;">
                        🔥 STUDY STREAK
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: var(--nexus-text-title);">
                        {xp_info['streak']} Day{'s' if xp_info['streak'] != 1 else ''} <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">(Best: {xp_info['longest_streak']}d)</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Quick Hub Action Bar ──
    c_act0, c_act1, c_act2, c_act3, c_act4, c_act5, c_act6 = st.columns(7)
    with c_act0:
        if st.button("🧠 Nexus AI", use_container_width=True, type="primary", key="dash_go_ai_btn"):
            st.session_state["current_page"] = "🧠 AI Command Center"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act1:
        if st.button("🎯 Quiz Engine", use_container_width=True, key="dash_go_quiz_btn"):
            st.session_state["current_page"] = "🎯 Quiz Engine"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act2:
        if st.button("💡 Active Recall", use_container_width=True, key="dash_go_recall_btn"):
            st.session_state["current_page"] = "💡 Active Recall"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act3:
        if st.button("❌ Mistake Vault", use_container_width=True, key="dash_go_mistakes_btn"):
            st.session_state["current_page"] = "❌ Mistake Vault"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act4:
        if st.button("⏱️ Focus Studio", use_container_width=True, key="dash_go_focus_btn"):
            st.session_state["current_page"] = "⏱️ Focus Studio"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act5:
        if st.button("🧠 Revisions", use_container_width=True, key="dash_go_revisions_btn"):
            st.session_state["current_page"] = "🧠 Revision Queue"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_act6:
        if st.button("🗓️ Planner", use_container_width=True, key="dash_go_planner_btn"):
            st.session_state["current_page"] = "🗓️ Study Planner"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    # ── Top Metric Cards ──
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("Subjects", stats["total_subjects"], "#6366F1", theme=user_theme)
    with m2:
        render_metric_card("Chapters", stats["total_chapters"], "#8B5CF6", theme=user_theme)
    with m3:
        render_metric_card("Topics", stats["total_topics"], "#A855F7", theme=user_theme)
    with m4:
        render_metric_card("Completed", stats["completed"], "#22C55E",
                          f"of {stats['total_topics']}", theme=user_theme)
    with m5:
        render_metric_card("Progress", f"{stats['percent_completed']}%", "#6366F1",
                          f"{stats['remaining']} remaining", theme=user_theme)

    st.markdown("---")

    # ── NEXUS SMART PRIORITIES & EXAM READINESS ENGINE ──
    c_prio, c_ready = st.columns([1.3, 1.2])

    with c_prio:
        st.subheader("🔴 Nexus Smart Priorities")
        st.caption("Dynamically scored based on exam proximity, understanding level, and overdue status.")
        
        priorities = get_top_nexus_priorities(user_id, limit=4)
        if not priorities:
            st.success("🎉 Outstanding! No critical or high priority bottlenecks found.")
        else:
            for p in priorities:
                reasons_str = " • ".join(p["reasons"])
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {p['badge_color']};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <div style="display: flex; gap: 6px; align-items: center;">
                                <span class="nexus-pill-{p['tier'].lower()}">{p['tier_icon']} {p['tier']}</span>
                                <span style="font-size: 0.8rem; font-weight: 700; color: {p.get('subject_color', '#38BDF8')};">{p['subject_name']}</span>
                            </div>
                            <span style="font-size: 0.78rem; font-weight: 700; color: {p['badge_color']};">Score: {p['score']}</span>
                        </div>
                        <div style="font-size: 1.02rem; font-weight: 700; color: var(--nexus-text-title);">
                            {p['topic_name']}
                        </div>
                        <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-top: 4px;">
                            {p['chapter_name']} {f'• <span style="color: {p["badge_color"]};">{reasons_str}</span>' if reasons_str else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with c_ready:
        st.subheader("🎓 Exam Readiness Score")
        
        # Term selector
        active_terms = get_active_upcoming_terms(user_id)
        term_options = {"Overall (All Terms)": None}
        for t in active_terms:
            term_options[f"{t['name']} (Exam: {t.get('exam_date', 'N/A')})"] = t["id"]
            
        sel_term_label = st.selectbox("Exam Term Filter", list(term_options.keys()), key="dash_term_select", label_visibility="collapsed")
        sel_term_id = term_options[sel_term_label]
        
        readiness = calculate_exam_readiness_score(user_id, term_id=sel_term_id)
        r_score = readiness["readiness_score"]
        r_color = "#22C55E" if r_score >= 80 else ("#38BDF8" if r_score >= 60 else ("#F59E0B" if r_score >= 40 else "#EF4444"))
        
        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; padding: 18px 16px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: {r_color}; text-transform: uppercase; letter-spacing: 0.05em;">
                    COMPOSITE PREPAREDNESS INDEX
                </div>
                <div class="readiness-score-big" style="margin: 4px 0; color: {r_color};">
                    {r_score} <span style="font-size: 1.4rem; color: var(--nexus-text-sub);">/ 100</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin: 12px 0 10px 0; font-size: 0.82rem; text-align: left;">
                    <div style="background: rgba(255,255,255,0.04); padding: 6px 8px; border-radius: 6px;">
                        📚 <strong>Syllabus:</strong> {readiness['syllabus_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 6px 8px; border-radius: 6px;">
                        🧠 <strong>Understand:</strong> {readiness['understanding_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 6px 8px; border-radius: 6px;">
                        🔄 <strong>Revisions:</strong> {readiness['revision_pct']}%
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 6px 8px; border-radius: 6px;">
                        ❌ <strong>Mistakes:</strong> {readiness.get('factors', {}).get('mistake_resolution', 100)}%
                    </div>
                </div>
                <div style="text-align: left; font-size: 0.8rem; color: var(--nexus-text-sub); border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                    <strong style="color: #38BDF8;">⚡ Actionable Next Step:</strong><br/>
                    {readiness['recommendations'][0] if readiness['recommendations'] else 'Keep up your daily study momentum!'}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Main: Donut Chart + Details ──
    col_chart, col_details = st.columns([3, 2])

    with col_chart:
        st.subheader("📊 Overall Syllabus Progress")
        if stats["total_topics"] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=["Completed", "Revision Done", "In Progress", "Not Started"],
                values=[
                    stats["completed"] - stats["revision_done"],
                    stats["revision_done"],
                    stats["in_progress"],
                    stats["not_started"]
                ],
                hole=0.65,
                marker=dict(colors=["#22C55E", "#0284C7", "#F59E0B", "#94A3B8" if not is_dark else "#475569"]),
                hoverinfo="label+percent+value",
                textinfo="percent",
                textfont=dict(size=13, color="#FFFFFF" if is_dark else "#0F172A")
            )])

            text_color = "#FFFFFF" if is_dark else "#0F172A"
            sub_text_color = "#94A3B8" if is_dark else "#64748B"
            legend_color = "#CBD5E1" if is_dark else "#334155"

            fig.update_layout(
                annotations=[dict(
                    text=f"<b>{stats['percent_completed']}%</b><br>"
                         f"<span style='font-size:12px;color:{sub_text_color};'>"
                         f"{stats['completed']}/{stats['total_topics']}</span>",
                    x=0.5, y=0.5, font_size=28, font_color=text_color,
                    showarrow=False
                )],
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5,
                    font=dict(color=legend_color)
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_color),
                margin=dict(t=10, b=40, l=10, r=10),
                height=340
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 No topics yet. Go to **📚 Syllabus Manager** to add your subjects and topics!")

    with col_details:
        st.subheader("🎯 Progress Breakdown")

        if stats["total_topics"] > 0:
            st.markdown(f"🟢 **Completed:** {stats['completed']} / {stats['total_topics']}")
            st.progress(stats["completed"] / stats["total_topics"])

            st.markdown(f"🔵 **Revision Done:** {stats['revision_done']}")
            st.progress(stats["revision_done"] / stats["total_topics"])

            st.markdown(f"🟡 **In Progress:** {stats['in_progress']}")
            st.progress(stats["in_progress"] / stats["total_topics"])

            st.markdown(f"⚪ **Not Started:** {stats['not_started']}")
            st.progress(stats["not_started"] / stats["total_topics"])

            st.markdown(f"🧠 **Avg Understanding:** {stats['avg_understanding']} / 5")
        else:
            st.caption("Add topics to see progress here.")

    st.markdown("---")

    # ── Exam Countdown ──
    _render_exam_countdown(user_id, user_theme)

    st.markdown("---")

    # ── Revision Reminders ──
    _render_revision_reminders(user_id)

    st.markdown("---")

    # ── Subject-wise Breakdown (Batch Rendered) ──
    st.subheader("📚 Subject Summary")

    if subjects_with_stats:
        # Create rows of 3 columns
        for row_start in range(0, len(subjects_with_stats), 3):
            row_subjects = subjects_with_stats[row_start:row_start + 3]
            cols = st.columns(3)
            for idx, sub in enumerate(row_subjects):
                pct = sub["percent_completed"]
                color = sub["color"]

                with cols[idx]:
                    st.markdown(f"""
                        <div class="nexus-card" style="border-left: 4px solid {color};">
                            <h4 style="margin: 0;">{sub['name']}</h4>
                            <p style="font-size: 0.85rem; margin: 4px 0 8px 0;">
                                {sub['total_chapters']} Chapters • {sub['total_topics']} Topics
                            </p>
                            <h3 style="color: {color}; margin: 0;">{pct}% Done</h3>
                            <p style="font-size: 0.82rem; margin: 4px 0 0 0;">
                                {sub['completed']} of {sub['total_topics']} completed
                                {f' • Avg: {sub["avg_understanding"]}/5' if sub['total_topics'] > 0 else ''}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        board = profile.get("board", "CBSE")
        class_name = profile.get("class_name", "Class 10")
        with st.spinner(f"⚡ Auto-loading official {board} ({class_name}) syllabus..."):
            loaded = preload_standard_syllabus(user_id, board, class_name)
            if loaded:
                st.toast(f"✅ Official {board} ({class_name}) syllabus loaded!", icon="🚀")
                st.rerun()


def _render_exam_countdown(user_id: int, theme: str = "Light"):
    """Show a countdown to the next upcoming active exam (filters out completed/already-done terms)."""
    terms = get_active_upcoming_terms(user_id)
    if not terms:
        return

    today = datetime.date.today()
    upcoming = []

    for term in terms:
        try:
            exam_date = datetime.datetime.strptime(term["exam_date"], "%Y-%m-%d").date()
            days_left = (exam_date - today).days
            if days_left >= 0:
                upcoming.append({
                    "name": term["name"],
                    "date": exam_date,
                    "days_left": days_left
                })
        except (ValueError, TypeError):
            continue

    if not upcoming:
        return

    # Sort by closest first
    upcoming.sort(key=lambda x: x["days_left"])
    next_exam = upcoming[0]

    st.subheader("⏰ Next Exam Countdown")

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        render_metric_card(
            "Next Exam",
            next_exam["name"],
            "#EC4899",
            theme=theme
        )
    with c2:
        render_metric_card(
            "Exam Date",
            next_exam["date"].strftime("%d %B %Y"),
            "#38BDF8" if theme.lower() == "dark" else "#4F46E5",
            theme=theme
        )
    with c3:
        days = next_exam["days_left"]
        urgency_color = "#22C55E" if days > 30 else "#EAB308" if days > 7 else "#EF4444"
        render_metric_card(
            "Days Remaining",
            f"{days}",
            urgency_color,
            "days left" if days != 1 else "day left",
            theme=theme
        )

    # Show all upcoming exams if more than one
    if len(upcoming) > 1:
        with st.expander("📅 All Active Upcoming Exams"):
            for exam in upcoming:
                e_col1, e_col2 = st.columns([3, 1])
                with e_col1:
                    st.write(f"**{exam['name']}** — {exam['date'].strftime('%d %B %Y')}")
                with e_col2:
                    days = exam["days_left"]
                    if days == 0:
                        st.warning("TODAY!")
                    elif days <= 7:
                        st.error(f"⚠️ {days} days")
                    else:
                        st.info(f"{days} days")


def _render_revision_reminders(user_id: int):
    """Show today's due spaced revision reminders."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    due = get_due_revisions(user_id, today_str)

    if not due:
        return

    st.subheader(f"🔔 Revision Reminders ({len(due)} due)")
    st.caption("Topics you completed that are due for spaced revision today.")

    for rev in due:
        item_name = rev.get("item_name") or f"{rev['item_type']} #{rev['item_id']}"
        subject_name = rev.get("subject_name") or ""
        interval = rev.get("interval_days", 0)
        due_date = rev.get("due_date", "")
        is_overdue = due_date < today_str

        c1, c2, c3 = st.columns([5, 2, 1])
        with c1:
            overdue_badge = " <span style='color: #EF4444; font-size: 0.75rem;'>⚠️ OVERDUE</span>" if is_overdue else ""
            st.markdown(
                f"<span style='font-size: 0.85rem;'>{subject_name}</span> • "
                f"<strong>{item_name}</strong>{overdue_badge}",
                unsafe_allow_html=True
            )
        with c2:
            label_map = {1: "1-day", 3: "3-day", 7: "1-week", 14: "2-week", 30: "1-month"}
            label = label_map.get(interval, f"{interval}d")
            st.caption(f"📅 {label} review • Due: {due_date}")
        with c3:
            if st.button("✅", key=f"rev_done_{rev['id']}", help="Mark as revised"):
                complete_revision(user_id, rev["id"])
                st.toast(f"✅ Revision completed for '{item_name}'", icon="🌟")
                st.rerun()

