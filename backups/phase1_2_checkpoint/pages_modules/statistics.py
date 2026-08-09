"""
statistics.py — Subject statistics page with interactive Plotly charts.

Shows: completion bar chart, per-subject donut, understanding heatmap,
and detailed stat cards for every subject.
"""

import streamlit as st
import plotly.graph_objects as go
from models import get_all_subjects_with_stats, get_user_theme
from styles import render_header, render_metric_card


def render_statistics_page(user_id: int):
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")
    render_header("📊 Statistics & Analytics", "Visual breakdown of your progress across all subjects.", theme=user_theme)

    subjects = get_all_subjects_with_stats(user_id)

    if not subjects:
        st.info("📝 Add subjects in the **Syllabus Manager** to see statistics here.")
        return

    # Gather data from single-query subject stats
    names = [s["name"] for s in subjects]
    pcts = [s["percent_completed"] for s in subjects]
    completed_counts = [s["completed"] for s in subjects]
    total_counts = [s["total_topics"] for s in subjects]
    remaining_counts = [s["remaining"] for s in subjects]
    avg_understandings = [s["avg_understanding"] for s in subjects]
    revision_counts = [s["revision_done"] for s in subjects]
    colors = [s["color"] for s in subjects]

    # Guard: if every subject has 0 topics, show helpful message instead of empty charts
    if sum(total_counts) == 0:
        st.info("📝 Your subjects don't have any topics yet. Go to **📚 Syllabus Manager** and add chapters & topics to see statistics here.")
        return

    # ── Completion Bar Chart ──
    st.subheader("📈 Completion by Subject")

    text_col = "#FFFFFF" if is_dark else "#0F172A"
    grid_col = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"
    axis_col = "#CBD5E1" if is_dark else "#64748B"

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=names,
        y=pcts,
        marker_color=colors,
        text=[f"{p}%" for p in pcts],
        textposition="outside",
        textfont=dict(color=text_col, size=13)
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=axis_col),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Completion %", showgrid=True,
                   gridcolor=grid_col, range=[0, 110]),
        margin=dict(t=20, b=40, l=40, r=20),
        height=350
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── Completed vs Remaining Stacked Bar ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("✅ Completed vs Remaining")

        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(
            name="Completed", x=names, y=completed_counts,
            marker_color="#22C55E"
        ))
        fig_stack.add_trace(go.Bar(
            name="Remaining", x=names, y=remaining_counts,
            marker_color="#94A3B8" if not is_dark else "#475569"
        ))
        fig_stack.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=axis_col),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3,
                       xanchor="center", x=0.5),
            margin=dict(t=10, b=50, l=40, r=20),
            height=320,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=grid_col)
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with col_right:
        st.subheader("🧠 Understanding Levels")

        fig_und = go.Figure()
        fig_und.add_trace(go.Bar(
            x=names,
            y=avg_understandings,
            marker_color=[
                "#EF4444" if v <= 2 else "#F59E0B" if v <= 3 else "#22C55E" if v <= 4 else "#4F46E5"
                for v in avg_understandings
            ],
            text=[f"{v}/5" for v in avg_understandings],
            textposition="outside",
            textfont=dict(color=text_col, size=12)
        ))
        fig_und.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=axis_col),
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Understanding (1–5)", showgrid=True,
                       gridcolor=grid_col, range=[0, 5.5]),
            margin=dict(t=10, b=40, l=40, r=20),
            height=320
        )
        st.plotly_chart(fig_und, use_container_width=True)

    st.markdown("---")

    # ── Per-Subject Stat Cards ──
    st.subheader("📋 Detailed Subject Stats")

    for row_start in range(0, len(subjects), 2):
        row_subs = subjects[row_start:row_start + 2]
        cols = st.columns(2)
        for idx, sub in enumerate(row_subs):
            with cols[idx]:
                st.markdown(f"""
                    <div class="nexus-card" style="border-top: 3px solid {sub['color']};">
                        <h4 style="margin: 0 0 12px 0;">{sub['name']}</h4>
                        <table style="width: 100%; font-size: 0.88rem;">
                            <tr><td>📖 Chapters</td><td style="text-align:right;"><b>{sub['total_chapters']}</b></td></tr>
                            <tr><td>📝 Total Topics</td><td style="text-align:right;"><b>{sub['total_topics']}</b></td></tr>
                            <tr><td>✅ Completed</td><td style="text-align:right; color: #22C55E;"><b>{sub['completed']}</b></td></tr>
                            <tr><td>🟡 In Progress</td><td style="text-align:right; color: #EAB308;"><b>{sub['in_progress']}</b></td></tr>
                            <tr><td>⚪ Not Started</td><td style="text-align:right;"><b>{sub['not_started']}</b></td></tr>
                            <tr><td>🔵 Revision Done</td><td style="text-align:right; color: #3B82F6;"><b>{sub['revision_done']}</b></td></tr>
                            <tr><td>🧠 Avg Understanding</td><td style="text-align:right;"><b>{sub['avg_understanding']}/5</b></td></tr>
                            <tr><td style="padding-top: 8px;">📊 <b>Progress</b></td>
                                <td style="text-align:right; padding-top: 8px; color: {sub['color']}; font-size: 1.1rem;">
                                    <b>{sub['percent_completed']}%</b>
                                </td></tr>
                        </table>
                    </div>
                """, unsafe_allow_html=True)

