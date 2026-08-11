"""
review.py — Nexus Spaced Repetition Review Module.

Provides adaptive SuperMemo SM-2 spaced repetition with:
- Overdue / Due Today / This Week / Upcoming / Mastered revision queues
- Manual quick-schedule for any topic
- 1-click "Recall" shortcut to Active Recall in Practice
"""

import streamlit as st
from models import (
    get_revision_queue,
    complete_adaptive_revision,
    schedule_adaptive_revisions,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    get_user_theme
)
from styles import render_top_header_bar, render_empty_state


def render_review_page(user_id: int):
    render_top_header_bar(
        user_id,
        "🧠 Review",
        "Master forgetting curves with adaptive SuperMemo SM-2 spaced repetition.",
        ["NEXUS", "Review"]
    )

    _render_revision_queue_view(user_id)



# ══════════════════════════════════════════════════════════════════════════
# SPACED REPETITION QUEUE
# ══════════════════════════════════════════════════════════════════════════

def _render_revision_queue_view(user_id: int):
    queue = get_revision_queue(user_id)
    overdue = queue.get("overdue", [])
    due_today = queue.get("due_today", [])
    due_this_week = queue.get("due_this_week", [])
    upcoming = queue.get("upcoming", [])
    recent = queue.get("recent_completed", [])

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
                <div style="font-size: 0.8rem; font-weight: 700; color: #22C55E; text-transform: uppercase;">Mastered</div>
                <div style="font-size: 2rem; font-weight: 800; color: #22C55E; margin: 4px 0;">{len(recent)}</div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Retention reinforced</div>
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
            render_empty_state("✨", "All Caught Up!", "No revision tasks in this section. You are completely on track with your spaced repetition schedule!")
            return

        for idx, item in enumerate(items):
            with st.container():
                c1, c2, c3 = st.columns([3, 1.4, 1.4])
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
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("💡 Recall", key=f"rev_rec_{item['id']}", help="Practice in Active Recall"):
                                st.session_state["practice_active_tab"] = "💡 Active Recall"
                                st.session_state["active_recall_target_topic_id"] = item.get("topic_id") or item.get("item_id")
                                st.session_state["current_page"] = "🎯 Practice"
                                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                                st.rerun()
                        with col_b2:
                            if st.button("✅ Done", key=f"rev_done_btn_{item['id']}", type="primary" if is_overdue else "secondary"):
                                complete_adaptive_revision(user_id, item['id'])
                                st.toast(f"Revised {item['topic_name']}! +50 XP", icon="🎉")
                                st.rerun()
                    else:
                        st.markdown(f"<span style='color: #22C55E; font-size: 0.85rem; font-weight: 600;'>Mastered on {item.get('completed_at', 'Recently')}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0; opacity: 0.15;'/>", unsafe_allow_html=True)

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

    # Manual Quick Revision Scheduler
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    with st.expander("➕ Manually Schedule an Adaptive Spaced Revision"):
        subjects = get_all_subjects(user_id)
        if subjects:
            s_map = {s["name"]: s["id"] for s in subjects}
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="rev_man_subj")
            sel_subj_id = s_map[sel_subj_name]

            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with c_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="rev_man_chap")

            topics = get_topics_for_chapter(user_id, c_map[sel_chap_name]) if (c_map and sel_chap_name in c_map) else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with c_s3:
                sel_top_name = st.selectbox("Topic", list(t_map.keys()) if t_map else ["None"], key="rev_man_top")

            if t_map and sel_top_name in t_map:
                if st.button("🚀 Schedule Spaced Revisions", type="primary", use_container_width=True, key="rev_man_sched_btn"):
                    schedule_adaptive_revisions(user_id, "topic", t_map[sel_top_name], understanding=3)
                    st.success(f"Scheduled 4 spaced revisions (1d, 3d, 7d, 14d) for '{sel_top_name}'!")
                    st.rerun()
