"""
revisions.py — Adaptive Spaced Repetition Engine & Interactive Revision Queue.
"""

import streamlit as st
import datetime
from models import (
    get_revision_queue,
    complete_adaptive_revision,
    schedule_adaptive_revisions,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    award_user_xp
)

def render_revisions_page(user_id: int):
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); color: #38BDF8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>🧠</span> <span>ADAPTIVE SPACED REPETITION</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Revision Queue
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Never forget a concept. Nexus schedules smart revision intervals adapted to your understanding score.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    queue = get_revision_queue(user_id)
    overdue = queue.get("overdue", [])
    due_today = queue.get("due_today", [])
    due_this_week = queue.get("due_this_week", [])
    upcoming = queue.get("upcoming", [])
    recent = queue.get("recent_completed", [])

    # Metric Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #EF4444;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #EF4444; text-transform: uppercase;">Overdue</div>
                <div style="font-size: 2rem; font-weight: 800; color: #EF4444; margin: 4px 0;">{len(overdue)}</div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Needs immediate review</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #F97316;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #F97316; text-transform: uppercase;">Due Today</div>
                <div style="font-size: 2rem; font-weight: 800; color: #F97316; margin: 4px 0;">{len(due_today)}</div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Scheduled for today</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #38BDF8;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">This Week</div>
                <div style="font-size: 2rem; font-weight: 800; color: #38BDF8; margin: 4px 0;">{len(due_this_week)}</div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Next 7 days</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="metric-box" style="border-left: 4px solid #22C55E;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #22C55E; text-transform: uppercase;">Completed</div>
                <div style="font-size: 2rem; font-weight: 800; color: #22C55E; margin: 4px 0;">{len(recent)}</div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Recently mastered</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"🔴 Overdue ({len(overdue)})",
        f"⚡ Due Today ({len(due_today)})",
        f"📅 This Week ({len(due_this_week)})",
        f"⏳ Upcoming ({len(upcoming)})",
        f"✨ History ({len(recent)})"
    ])

    def render_queue_items(items, is_overdue=False, is_history=False):
        if not items:
            st.info("No revision tasks in this section. You are completely on track! 🎉")
            return

        for idx, item in enumerate(items):
            with st.container():
                c1, c2, c3 = st.columns([3, 1.2, 1.2])
                with c1:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <span style="font-size: 0.75rem; font-weight: 700; color: {item.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 12px;">
                                {item['subject_name']}
                            </span>
                            <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">
                                {item['chapter_name']}
                            </span>
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title);">
                            {item['topic_name']}
                        </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                        <div style="font-size: 0.8rem; color: var(--nexus-text-sub);">
                            Interval: <strong>Step #{item.get('interval_number', 1)}</strong><br/>
                            Due: <strong style="color: {'#EF4444' if is_overdue else 'var(--nexus-text-title)'};">{item['due_date']}</strong>
                        </div>
                    """, unsafe_allow_html=True)

                with c3:
                    if not is_history:
                        if st.button("✅ Mark Done", key=f"rev_done_btn_{item['id']}", use_container_width=True, type="primary" if is_overdue else "secondary"):
                            complete_adaptive_revision(user_id, item['id'])
                            st.toast(f"Revised {item['topic_name']}! +50 XP", icon="🎉")
                            st.rerun()
                    else:
                        st.markdown(f"<span style='color: #22C55E; font-size: 0.85rem; font-weight: 600;'>Done on {item.get('completed_at', 'Recently')}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'/>", unsafe_allow_html=True)

    with tab1:
        render_queue_items(overdue, is_overdue=True)

    with tab2:
        render_queue_items(due_today)

    with tab3:
        render_queue_items(due_this_week)

    with tab4:
        render_queue_items(upcoming)

    with tab5:
        render_queue_items(recent, is_history=True)

    # Manual Quick Revision Scheduler Card
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    with st.expander("➕ Manually Schedule an Adaptive Revision"):
        subjects = get_all_subjects(user_id)
        if subjects:
            s_map = {s["name"]: s["id"] for s in subjects}
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="man_rev_subj")
            
            sel_subj_id = s_map[sel_subj_name]
            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            
            with c_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="man_rev_chap")
            
            topics = get_topics_for_chapter(user_id, c_map[sel_chap_name]) if (c_map and sel_chap_name in c_map) else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            
            with c_s3:
                sel_top_name = st.selectbox("Topic", list(t_map.keys()) if t_map else ["None"], key="man_rev_top")
                
            if t_map and sel_top_name in t_map:
                if st.button("🚀 Schedule Spaced Revisions", type="primary", use_container_width=True):
                    schedule_adaptive_revisions(user_id, "topic", t_map[sel_top_name], understanding=3)
                    st.success(f"Scheduled 4 spaced revisions for '{sel_top_name}'!")
                    st.rerun()
