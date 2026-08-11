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
    get_daily_plans
)
from styles import render_top_header_bar, render_breadcrumbs


def render_focus_page(user_id: int):
    render_top_header_bar(
        user_id,
        "⏱️ Focus",
        "Single-task deep work studio with live timer, ambient audio, and auto XP rewards.",
        ["NEXUS", "Focus"]
    )

    tab_timer, tab_analytics = st.tabs([
        "⏱️ Focus Timer",
        "📊 Study Analytics"
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
        
        # Check prefill from topic shortcut or priority click
        pre_s_id = st.session_state.get("focus_target_subject_id")
        pre_t_id = st.session_state.get("focus_target_topic_id")
        pre_c_id = st.session_state.get("focus_target_chapter_id")
        
        pre_s_idx = 0
        if pre_s_id:
            for i, (sn, sid) in enumerate(s_map.items()):
                if sid == pre_s_id:
                    pre_s_idx = i
                    break

        c1, c2, c3 = st.columns(3)
        with c1:
            sel_s_name = st.selectbox("Focus Subject", list(s_map.keys()), index=pre_s_idx, key="foc_subj")
        sel_s_id = s_map[sel_s_name]

        chapters = get_chapters_for_subject(user_id, sel_s_id)
        c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
        
        pre_c_idx = 0
        if pre_c_id and c_map:
            for i, (cn, cid) in enumerate(c_map.items()):
                if cid == pre_c_id:
                    pre_c_idx = i
                    break

        with c2:
            sel_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], index=pre_c_idx, key="foc_chap")
        sel_c_id = c_map.get(sel_c_name)

        topics = get_topics_for_chapter(user_id, sel_c_id) if sel_c_id else []
        t_map = {t["name"]: t["id"] for t in topics} if topics else {}
        
        pre_t_idx = 0
        if pre_t_id and t_map:
            for i, (tn, tid) in enumerate(t_map.items()):
                if tid == pre_t_id:
                    pre_t_idx = i + 1  # Account for "General Study" at index 0
                    break

        with c3:
            sel_t_name = st.selectbox("Target Topic", ["General Study"] + list(t_map.keys()), index=pre_t_idx, key="foc_top")
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

        # Interactive High-Performance Client-Side Timer
        timer_seconds = int(selected_duration) * 60
        st.components.v1.html(f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 24px 16px; color: #F8FAFC;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px;">
                    🎯 IMMERSIVE FOCUS TARGET
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin-bottom: 16px;">
                    {sel_s_name} → {sel_c_name} {f'→ {sel_t_name}' if sel_t_id else ''}
                </div>
                
                <!-- Circular Progress & Display -->
                <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
                    <svg width="200" height="200" viewBox="0 0 200 200" style="transform: rotate(-90deg);">
                        <circle cx="100" cy="100" r="86" fill="transparent" stroke="rgba(255,255,255,0.08)" stroke-width="12" />
                        <circle id="nexus-timer-ring" cx="100" cy="100" r="86" fill="transparent" stroke="url(#timerGradient)" stroke-width="12" stroke-dasharray="540.35" stroke-dashoffset="0" stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;" />
                        <defs>
                            <linearGradient id="timerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#38BDF8" />
                                <stop offset="100%" stop-color="#F97316" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <div id="nexus-timer-text" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 2.5rem; font-weight: 800; color: #FFFFFF; font-family: 'Outfit', sans-serif; letter-spacing: -0.02em;">
                        {selected_duration}:00
                    </div>
                </div>

                <!-- Instant Response Controls -->
                <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                    <button id="nexus-btn-start" onclick="nexusStartTimer()" style="background: linear-gradient(135deg, #0284C7, #2563EB); border: none; color: white; padding: 10px 22px; font-size: 0.95rem; font-weight: 700; border-radius: 10px; cursor: pointer; transition: all 0.15s ease; box-shadow: 0 4px 14px rgba(37,99,235,0.4);">
                        ▶ Start Focus
                    </button>
                    <button id="nexus-btn-pause" onclick="nexusPauseTimer()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); color: #F8FAFC; padding: 10px 18px; font-size: 0.95rem; font-weight: 600; border-radius: 10px; cursor: pointer; transition: all 0.15s ease;">
                        ⏸ Pause
                    </button>
                    <button onclick="nexusAddMinutes(5)" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); color: #38BDF8; padding: 10px 14px; font-size: 0.9rem; font-weight: 700; border-radius: 10px; cursor: pointer; transition: all 0.15s ease;">
                        +5 Min
                    </button>
                    <button onclick="nexusResetTimer()" style="background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3); color: #EF4444; padding: 10px 16px; font-size: 0.9rem; font-weight: 600; border-radius: 10px; cursor: pointer; transition: all 0.15s ease;">
                        ↺ Reset
                    </button>
                </div>
            </div>

            <script>
                var totalSecs = {timer_seconds};
                var remainingSecs = totalSecs;
                var timerInterval = null;
                var circumference = 2 * Math.PI * 86; // 540.35

                function formatTime(secs) {{
                    var m = Math.floor(secs / 60);
                    var s = secs % 60;
                    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
                }}

                function updateDisplay() {{
                    document.getElementById('nexus-timer-text').innerText = formatTime(remainingSecs);
                    var ring = document.getElementById('nexus-timer-ring');
                    if (ring) {{
                        var fraction = 1 - (remainingSecs / totalSecs);
                        var offset = fraction * circumference;
                        ring.style.strokeDashoffset = offset;
                    }}
                }}

                function nexusStartTimer() {{
                    if (timerInterval) return;
                    document.getElementById('nexus-btn-start').style.opacity = '0.7';
                    document.getElementById('nexus-btn-start').innerText = '🔥 Focusing...';
                    timerInterval = setInterval(function() {{
                        if (remainingSecs > 0) {{
                            remainingSecs--;
                            updateDisplay();
                        }} else {{
                            clearInterval(timerInterval);
                            timerInterval = null;
                            document.getElementById('nexus-btn-start').innerText = '🎉 Completed!';
                            alert('🎯 Focus session complete! Log your progress below to claim your XP.');
                        }}
                    }}, 1000);
                }}

                function nexusPauseTimer() {{
                    if (timerInterval) {{
                        clearInterval(timerInterval);
                        timerInterval = null;
                        document.getElementById('nexus-btn-start').style.opacity = '1.0';
                        document.getElementById('nexus-btn-start').innerText = '▶ Resume';
                    }}
                }}

                function nexusAddMinutes(mins) {{
                    totalSecs += mins * 60;
                    remainingSecs += mins * 60;
                    updateDisplay();
                }}

                function nexusResetTimer() {{
                    nexusPauseTimer();
                    totalSecs = {timer_seconds};
                    remainingSecs = totalSecs;
                    document.getElementById('nexus-btn-start').innerText = '▶ Start Focus';
                    updateDisplay();
                }}
            </script>
        """, height=380)

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
                tasks = get_daily_plans(user_id, datetime.date.today().strftime("%Y-%m-%d"))
                pending_tasks = [t for t in tasks if not t.get("is_completed")]
                task_map = {f"#{t['id']}: {t.get('task') or t.get('title') or t.get('description', 'Task')}": t['id'] for t in pending_tasks}
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
