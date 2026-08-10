"""
focus.py — Nexus Focus Studio (Deep Work & Pomodoro Timer with Study Analytics).
"""

import streamlit as st
import datetime
import plotly.express as px
from models import (
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    log_focus_session_and_sync,
    get_focus_analytics,
    get_study_sessions,
    get_planner_tasks
)
from styles import render_breadcrumbs


def render_focus_page(user_id: int):
    render_breadcrumbs(["🏠 Dashboard", "⏱️ Focus Studio"])

    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(249, 115, 22, 0.12); border: 1px solid rgba(249, 115, 22, 0.35); color: #F97316; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>⏱️</span> <span>DEEP WORK & STUDY ANALYTICS</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Nexus Focus Studio
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Single-task deep focus sessions with live timer, ambient audio, automatic topic progress syncing, and study consistency tracking.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_timer, tab_analytics = st.tabs([
        "⏱️ Deep Focus Session",
        "📊 Study Time Analytics"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1: DEEP FOCUS TIMER
    # ══════════════════════════════════════════════════════════
    with tab_timer:
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please configure subjects in the Syllabus Manager first.")
            return

        s_map = {s["name"]: s["id"] for s in subjects}
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_s_name = st.selectbox("Focus Subject", list(s_map.keys()), key="foc_subj")
        sel_s_id = s_map[sel_s_name]

        chapters = get_chapters_for_subject(user_id, sel_s_id)
        c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
        with c2:
            sel_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="foc_chap")
        sel_c_id = c_map.get(sel_c_name)

        topics = get_topics_for_chapter(user_id, sel_c_id) if sel_c_id else []
        t_map = {t["name"]: t["id"] for t in topics} if topics else {}
        with c3:
            sel_t_name = st.selectbox("Target Topic", ["General Study"] + list(t_map.keys()), key="foc_top")
        sel_t_id = t_map.get(sel_t_name) if sel_t_name != "General Study" else None

        # Focus Modes & Durations
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        dur_choice = st.radio(
            "Select Session Duration",
            ["⚡ 25 Min (Pomodoro)", "🔥 50 Min (Standard Deep Work)", "🧠 90 Min (Ultradian Sprint)", "⚙️ Custom Duration"],
            horizontal=True,
            key="foc_dur_radio"
        )

        selected_duration = 25
        if "25" in dur_choice:
            selected_duration = 25
        elif "50" in dur_choice:
            selected_duration = 50
        elif "90" in dur_choice:
            selected_duration = 90
        else:
            selected_duration = st.number_input("Enter Minutes", min_value=5, max_value=240, value=35, step=5)

        # Ambient Audio Player Option
        with st.expander("🎧 Ambient Soundscapes (Optional Concentration Enhancer)", expanded=False):
            st.markdown("""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 6px;">
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; text-align: center;">
                        <span style="font-size: 0.85rem; font-weight: 700; color: #38BDF8;">🌧️ Gentle Rainfall</span>
                        <audio controls style="width: 100%; height: 32px; margin-top: 6px;">
                            <source src="https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3" type="audio/mpeg">
                        </audio>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; text-align: center;">
                        <span style="font-size: 0.85rem; font-weight: 700; color: #A855F7;">🌊 Ocean Waves</span>
                        <audio controls style="width: 100%; height: 32px; margin-top: 6px;">
                            <source src="https://assets.mixkit.co/active_storage/sfx/1188/1188-preview.mp3" type="audio/mpeg">
                        </audio>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Interactive Timer Card
        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; margin-top: 16px; padding: 36px 20px;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;">
                    🎯 IMMERSIVE FOCUS TARGET
                </div>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 800; color: var(--nexus-text-title); margin: 0 0 12px 0;">
                    {sel_s_name} → {sel_c_name} {f'→ {sel_t_name}' if sel_t_id else ''}
                </h2>
                <div style="font-family: 'Outfit', sans-serif; font-size: clamp(3.2rem, 7vw, 5.0rem); font-weight: 800; background: linear-gradient(135deg, #38BDF8, #F97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 6px 0;">
                    {selected_duration}:00
                </div>
                <p style="color: var(--nexus-text-sub); max-width: 480px; margin: 0 auto; font-size: 0.88rem;">
                    Silence notifications, engage full screen, and focus entirely on mastering this concept.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Complete & Record Form
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        with st.form("complete_focus_session_form"):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                update_topic_status = None
                if sel_t_id:
                    update_topic_status = st.selectbox(
                        "Update Topic Status on Completion:",
                        ["Leave Unchanged", "In Progress", "Completed", "Revision Done"],
                        index=0
                    )
                    if update_topic_status == "Leave Unchanged":
                        update_topic_status = None
            with c_f2:
                # Fetch pending tasks for today to optionally mark complete
                tasks = get_planner_tasks(user_id, datetime.date.today().strftime("%Y-%m-%d"))
                pending_tasks = [t for t in tasks if not t.get("is_completed")]
                task_map = {f"#{t['id']}: {t['title']}": t['id'] for t in pending_tasks}
                sel_task_str = st.selectbox("Link to Planner Task (Optional)", ["None"] + list(task_map.keys()))
                linked_task_id = task_map.get(sel_task_str)

            notes_txt = st.text_input("Session Notes / Reflections", placeholder="e.g. Solved 5 numericals, derived formula successfully.")
            
            bonus_xp = 50 if selected_duration >= 50 else 0
            earned_est = (selected_duration * 2) + bonus_xp
            
            save_btn = st.form_submit_button(
                f"🏁 Complete & Log {selected_duration}m Focus Session (+{earned_est} XP)",
                type="primary",
                use_container_width=True
            )
            
            if save_btn:
                log_focus_session_and_sync(
                    user_id=user_id,
                    duration_minutes=selected_duration,
                    subject_id=sel_s_id,
                    chapter_id=sel_c_id,
                    topic_id=sel_t_id,
                    notes=notes_txt,
                    update_topic_status=update_topic_status,
                    planner_task_id=linked_task_id
                )
                st.balloons()
                st.success(f"Session logged! +{earned_est} XP awarded and streak updated 🔥")
                st.rerun()

        # Recent Focus Logs
        st.markdown("---")
        st.subheader("Recent Focus Logs")
        sessions = get_study_sessions(user_id, limit=5)
        if not sessions:
            st.info("No focus sessions recorded yet. Start your first session above!")
        else:
            for s in sessions:
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {s.get('subject_color', '#38BDF8')}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: {s.get('subject_color', '#38BDF8')};">{s.get('subject_name')}</span>
                                <span style="color: var(--nexus-text-sub); font-size: 0.85rem;"> • {s.get('session_date')}</span>
                                <div style="font-size: 0.95rem; color: var(--nexus-text-title); font-weight: 600; margin-top: 2px;">
                                    ⏱️ {s.get('duration_minutes')} Minutes Focused {f'— {s.get("notes")}' if s.get("notes") else ''}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 2: STUDY TIME ANALYTICS
    # ══════════════════════════════════════════════════════════
    with tab_analytics:
        st.subheader("📊 Focus & Deep Work Analytics")
        analytics = get_focus_analytics(user_id)

        c_a1, c_a2, c_a3, c_a4 = st.columns(4)
        with c_a1:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #F97316;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F97316; text-transform: uppercase;">Total Study Time</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #F97316; margin: 4px 0;">{analytics['total_hours']} hrs</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">{analytics['total_sessions']} completed sessions</div>
                </div>
            """, unsafe_allow_html=True)
        with c_a2:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #38BDF8;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">This Week</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #38BDF8; margin: 4px 0;">{round(analytics['week_minutes'] / 60, 1)} hrs</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">{analytics['week_sessions']} sessions this week</div>
                </div>
            """, unsafe_allow_html=True)
        with c_a3:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #22C55E;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #22C55E; text-transform: uppercase;">Average Duration</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #22C55E; margin: 4px 0;">{int(analytics['avg_duration'])} min</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Per focus session</div>
                </div>
            """, unsafe_allow_html=True)
        with c_a4:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #A855F7;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #A855F7; text-transform: uppercase;">Focus Streak</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #A855F7; margin: 4px 0;">{analytics['focus_streak']} Days 🔥</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Feeds Exam Readiness (10%)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

        # 14-Day Study Trend Chart
        c_ch1, c_ch2 = st.columns([1.5, 1])
        with c_ch1:
            daily_trend = analytics.get("daily_trend", [])
            if daily_trend:
                import pandas as pd
                df_trend = pd.DataFrame(daily_trend)
                fig_trend = px.bar(
                    df_trend,
                    x="day_label",
                    y="minutes",
                    title="Daily Focus Time (Last 14 Days - Minutes)",
                    labels={"minutes": "Minutes", "day_label": "Day"}
                )
                fig_trend.update_layout(
                    height=220,
                    margin=dict(l=10, r=10, t=35, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8", size=11),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
                )
                fig_trend.update_traces(marker_color="#F97316")
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

        with c_ch2:
            subj_dist = analytics.get("subject_distribution", [])
            if subj_dist:
                import pandas as pd
                df_sub = pd.DataFrame(subj_dist)
                fig_pie = px.pie(
                    df_sub,
                    names="name",
                    values="minutes",
                    title="Subject Time Breakdown",
                    hole=0.45,
                    color="name",
                    color_discrete_sequence=[s.get("color", "#38BDF8") for s in subj_dist]
                )
                fig_pie.update_layout(
                    height=220,
                    margin=dict(l=10, r=10, t=35, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8", size=11),
                    showlegend=False
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Log sessions across different subjects to see your distribution breakdown.")
