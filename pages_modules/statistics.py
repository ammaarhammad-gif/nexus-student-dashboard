"""
statistics.py — Subject statistics page with interactive Plotly charts.

Shows: completion bar chart, per-subject donut, understanding heatmap,
and detailed stat cards for every subject.
"""

import streamlit as st
import plotly.graph_objects as go
from models import get_all_subjects, get_subject_stats
from styles import render_header, render_metric_card


def render_statistics_page(user_id: int):
    render_header("📊 Statistics & Analytics", "Visual breakdown of your progress across all subjects.")

    subjects = get_all_subjects(user_id)

    if not subjects:
        st.info("📝 Add subjects in the **Syllabus Manager** to see statistics here.")
        return

    # Gather data
    names = []
    pcts = []
    completed_counts = []
    total_counts = []
    remaining_counts = []
    avg_understandings = []
    revision_counts = []
    colors = []

    for sub in subjects:
        stats = get_subject_stats(user_id, sub["id"])
        names.append(sub["name"])
        pcts.append(stats["percent_completed"])
        completed_counts.append(stats["completed"])
        total_counts.append(stats["total_topics"])
        remaining_counts.append(stats["remaining"])
        avg_understandings.append(stats["avg_understanding"])
        revision_counts.append(stats["revision_done"])
        colors.append(sub["color"])

    # ── Completion Bar Chart ──
    st.subheader("📈 Completion by Subject")

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=names,
        y=pcts,
        marker_color=colors,
        text=[f"{p}%" for p in pcts],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=13)
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Completion %", showgrid=True,
                   gridcolor="rgba(255,255,255,0.05)", range=[0, 110]),
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
            marker_color="#475569"
        ))
        fig_stack.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3,
                       xanchor="center", x=0.5),
            margin=dict(t=10, b=50, l=40, r=20),
            height=320,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with col_right:
        st.subheader("🧠 Understanding Levels")

        fig_und = go.Figure()
        fig_und.add_trace(go.Bar(
            x=names,
            y=avg_understandings,
            marker_color=[
                "#EF4444" if v <= 2 else "#EAB308" if v <= 3 else "#22C55E" if v <= 4 else "#6366F1"
                for v in avg_understandings
            ],
            text=[f"{v}/5" for v in avg_understandings],
            textposition="outside",
            textfont=dict(color="#F8FAFC", size=12)
        ))
        fig_und.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Understanding (1–5)", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)", range=[0, 5.5]),
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
            stats = get_subject_stats(user_id, sub["id"])
            with cols[idx]:
                st.markdown(f"""
                    <div class="nexus-card" style="border-top: 3px solid {sub['color']};">
                        <h4 style="color: #F8FAFC; margin: 0 0 12px 0;">{sub['name']}</h4>
                        <table style="width: 100%; color: #CBD5E1; font-size: 0.88rem;">
                            <tr><td>📖 Chapters</td><td style="text-align:right;"><b>{stats['total_chapters']}</b></td></tr>
                            <tr><td>📝 Total Topics</td><td style="text-align:right;"><b>{stats['total_topics']}</b></td></tr>
                            <tr><td>✅ Completed</td><td style="text-align:right; color: #22C55E;"><b>{stats['completed']}</b></td></tr>
                            <tr><td>🟡 In Progress</td><td style="text-align:right; color: #EAB308;"><b>{stats['in_progress']}</b></td></tr>
                            <tr><td>⚪ Not Started</td><td style="text-align:right;"><b>{stats['not_started']}</b></td></tr>
                            <tr><td>🔵 Revision Done</td><td style="text-align:right; color: #3B82F6;"><b>{stats['revision_done']}</b></td></tr>
                            <tr><td>🧠 Avg Understanding</td><td style="text-align:right;"><b>{stats['avg_understanding']}/5</b></td></tr>
                            <tr><td style="padding-top: 8px;">📊 <b>Progress</b></td>
                                <td style="text-align:right; padding-top: 8px; color: {sub['color']}; font-size: 1.1rem;">
                                    <b>{stats['percent_completed']}%</b>
                                </td></tr>
                        </table>
                    </div>
                """, unsafe_allow_html=True)
