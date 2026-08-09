"""
focus.py — Nexus Focus Studio (Deep Work & Pomodoro Timer).
"""

import streamlit as st
import datetime
from models import (
    add_study_session,
    award_user_xp,
    update_user_streak,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    get_study_sessions
)

def render_focus_page(user_id: int):
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(249, 115, 22, 0.12); border: 1px solid rgba(249, 115, 22, 0.35); color: #F97316; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>⏱️</span> <span>DEEP WORK IMMERSION</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Nexus Focus Studio
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Single-task deep focus sessions with automatic study analytics logging and streak building.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Subject & Topic Selectors
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

    # Focus Modes
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    c_dur1, c_dur2, c_dur3, c_dur4 = st.columns(4)
    with c_dur1:
        m25 = st.button("⚡ 25 Min (Pomodoro)", use_container_width=True)
    with c_dur2:
        m50 = st.button("🔥 50 Min (Standard)", use_container_width=True)
    with c_dur3:
        m90 = st.button("🧠 90 Min (Deep Work)", use_container_width=True)
    with c_dur4:
        custom_mins = st.number_input("Custom Minutes", min_value=5, max_value=180, value=30, step=5, label_visibility="collapsed")

    selected_duration = 30
    if m25:
        selected_duration = 25
    elif m50:
        selected_duration = 50
    elif m90:
        selected_duration = 90
    else:
        selected_duration = custom_mins

    # Interactive Timer Display Card
    st.markdown(f"""
        <div class="readiness-container" style="text-align: center; margin-top: 20px; padding: 40px 20px;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                🎯 CURRENT FOCUS TARGET
            </div>
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--nexus-text-title); margin: 0 0 16px 0;">
                {sel_s_name} → {sel_c_name} {f'→ {sel_t_name}' if sel_t_id else ''}
            </h2>
            <div style="font-family: 'Outfit', sans-serif; font-size: clamp(3.5rem, 8vw, 5.5rem); font-weight: 800; background: linear-gradient(135deg, #38BDF8, #F97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0;">
                {selected_duration}:00
            </div>
            <p style="color: var(--nexus-text-sub); max-width: 480px; margin: 0 auto 20px auto; font-size: 0.9rem;">
                Eliminate all browser distractions, silence your phone, and immerse yourself in single-concept deep focus.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Session Completion Form
    with st.form("complete_focus_session_form"):
        notes_txt = st.text_input("Session Reflection / Notes", placeholder="e.g. Mastered all lens formula sign conventions, solved 4 numericals.")
        save_btn = st.form_submit_button(f"🏁 Complete & Record {selected_duration}m Focus Session (+{selected_duration * 2} XP)", type="primary", use_container_width=True)
        if save_btn:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            add_study_session(
                user_id=user_id,
                subject_id=sel_s_id,
                duration_minutes=selected_duration,
                session_date=today_str,
                notes=notes_txt,
                chapter_id=sel_c_id,
                topic_id=sel_t_id
            )
            earned_xp = selected_duration * 2
            award_user_xp(user_id, "focus_session", earned_xp, f"Completed {selected_duration}m Focus in {sel_s_name}")
            update_user_streak(user_id)
            st.balloons()
            st.success(f"Great focus session! Logged {selected_duration} minutes & awarded +{earned_xp} XP.")
            st.rerun()

    # Recent Focus Sessions
    st.markdown("---")
    st.subheader("Recent Focus Logs")
    sessions = get_study_sessions(user_id, limit=5)
    if not sessions:
        st.info("No focus sessions recorded yet. Start your first session above!")
    else:
        for s in sessions:
            st.markdown(f"""
                <div class="priority-item-card" style="border-left-color: {s.get('subject_color', '#38BDF8')};">
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
