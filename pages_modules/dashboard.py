"""
dashboard.py — Main dashboard page.

Shows: Welcome banner, overall stats, donut chart, per-subject breakdown,
and an exam countdown section.
"""

import streamlit as st
import plotly.graph_objects as go
import datetime
from models import (
    get_overall_stats, get_user_profile, get_all_subjects,
    get_subject_stats, get_all_terms,
    get_due_revisions, complete_revision
)
from preloaded_syllabi import preload_standard_syllabus
from styles import render_header, render_metric_card


def render_dashboard_page(user_id: int):
    profile = get_user_profile(user_id)
    user_name = profile.get("name", "Student")
    class_info = f"{profile.get('class_name', '')} • {profile.get('board', '')} • {profile.get('academic_year', '')}"

    # Auto-load official board syllabus if user has no subjects or 0 topics
    subjects = get_all_subjects(user_id)
    stats = get_overall_stats(user_id)
    if not subjects or stats["total_topics"] == 0:
        board = profile.get("board", "CBSE")
        class_name = profile.get("class_name", "Class 10")
        loaded = preload_standard_syllabus(user_id, board, class_name)
        if loaded:
            st.rerun()
        stats = get_overall_stats(user_id)

    # ── Welcome Banner ──
    st.markdown(f"""
        <div class="welcome-banner">
            <h2>Welcome back, {user_name}! 👋</h2>
            <p>{class_info}</p>
        </div>
    """, unsafe_allow_html=True)

    # ── Top Metric Cards ──
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("Subjects", stats["total_subjects"], "#6366F1")
    with m2:
        render_metric_card("Chapters", stats["total_chapters"], "#8B5CF6")
    with m3:
        render_metric_card("Topics", stats["total_topics"], "#A855F7")
    with m4:
        render_metric_card("Completed", stats["completed"], "#22C55E",
                          f"of {stats['total_topics']}")
    with m5:
        render_metric_card("Progress", f"{stats['percent_completed']}%", "#6366F1",
                          f"{stats['remaining']} remaining")

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
                marker=dict(colors=["#22C55E", "#3B82F6", "#EAB308", "#475569"]),
                hoverinfo="label+percent+value",
                textinfo="percent",
                textfont=dict(size=13, color="#F8FAFC")
            )])

            fig.update_layout(
                annotations=[dict(
                    text=f"<b>{stats['percent_completed']}%</b><br>"
                         f"<span style='font-size:12px;color:#94A3B8;'>"
                         f"{stats['completed']}/{stats['total_topics']}</span>",
                    x=0.5, y=0.5, font_size=28, font_color="#F8FAFC",
                    showarrow=False
                )],
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5,
                    font=dict(color="#CBD5E1")
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
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
    _render_exam_countdown(user_id)

    st.markdown("---")

    # ── Revision Reminders ──
    _render_revision_reminders(user_id)

    st.markdown("---")

    # ── Subject-wise Breakdown ──
    st.subheader("📚 Subject Summary")
    subjects = get_all_subjects(user_id)

    if subjects:
        # Create rows of 3 columns
        for row_start in range(0, len(subjects), 3):
            row_subjects = subjects[row_start:row_start + 3]
            cols = st.columns(3)
            for idx, sub in enumerate(row_subjects):
                sub_stats = get_subject_stats(user_id, sub["id"])
                pct = sub_stats["percent_completed"]
                color = sub["color"]

                with cols[idx]:
                    st.markdown(f"""
                        <div class="nexus-card" style="border-left: 4px solid {color};">
                            <h4 style="margin: 0; color: #F8FAFC;">{sub['name']}</h4>
                            <p style="color: #94A3B8; font-size: 0.85rem; margin: 4px 0 8px 0;">
                                {sub_stats['total_chapters']} Chapters • {sub_stats['total_topics']} Topics
                            </p>
                            <h3 style="color: {color}; margin: 0;">{pct}% Done</h3>
                            <p style="color: #CBD5E1; font-size: 0.82rem; margin: 4px 0 0 0;">
                                {sub_stats['completed']} of {sub_stats['total_topics']} completed
                                {f' • Avg: {sub_stats["avg_understanding"]}/5' if sub_stats['total_topics'] > 0 else ''}
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


def _render_exam_countdown(user_id: int):
    """Show a countdown to the next upcoming exam."""
    terms = get_all_terms(user_id)
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
            "#EC4899"
        )
    with c2:
        render_metric_card(
            "Exam Date",
            next_exam["date"].strftime("%d %B %Y"),
            "#F8FAFC"
        )
    with c3:
        days = next_exam["days_left"]
        urgency_color = "#22C55E" if days > 30 else "#EAB308" if days > 7 else "#EF4444"
        render_metric_card(
            "Days Remaining",
            f"{days}",
            urgency_color,
            "days left" if days != 1 else "day left"
        )

    # Show all upcoming exams if more than one
    if len(upcoming) > 1:
        with st.expander("📅 All Upcoming Exams"):
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
                f"<span style='color: #94A3B8; font-size: 0.8rem;'>{subject_name}</span> • "
                f"<strong style='color: #F8FAFC;'>{item_name}</strong>{overdue_badge}",
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
