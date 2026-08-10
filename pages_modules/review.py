"""
review.py — Nexus Unified Review Module.

Consolidates:
1. 🧠 Revision Queue (Spaced repetition intervals: Overdue, Due Today, This Week, Upcoming, Mastered)
2. ❌ Mistake Vault (Error pattern analysis, 7 root-cause categories, Re-Quiz generator, Anki export)
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from models import (
    get_revision_queue,
    complete_adaptive_revision,
    schedule_adaptive_revisions,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    add_mistake,
    get_all_mistakes,
    get_mistake_analytics,
    toggle_mistake_reviewed,
    delete_mistake,
    generate_mistake_requiz,
    get_user_theme
)
from styles import render_top_header_bar, render_metric_card, render_breadcrumbs, render_empty_state
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_mistakes_to_anki

MISTAKE_TYPES = [
    "Conceptual Gap",
    "Calculation Slip",
    "Formula Confusion",
    "Memory Lapse",
    "Careless Reading",
    "Time Pressure",
    "Application Error"
]


def render_review_page(user_id: int):
    render_top_header_bar(
        user_id,
        "🧠 Review",
        "Master forgetting curves with adaptive SuperMemo SM-2 spaced repetition.",
        ["NEXUS", "Review"]
    )

    tab_revisions, tab_mistakes = st.tabs([
        "🧠 Spaced Repetition Queue",
        "❌ Mistake Vault"
    ])

    with tab_revisions:
        _render_revision_queue_view(user_id)

    with tab_mistakes:
        _render_mistake_vault_view(user_id)



# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 1: REVISION QUEUE
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


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 2: MISTAKE VAULT
# ══════════════════════════════════════════════════════════════════════════

def _render_mistake_vault_view(user_id: int):
    analytics = get_mistake_analytics(user_id)
    total_mistakes = analytics.get("total", 0)
    unreviewed_count = analytics.get("unreviewed", 0)
    reviewed_count = analytics.get("reviewed", 0)
    breakdown = analytics.get("breakdown", [])

    c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
    with c_m1:
        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; height: 100%; padding: 18px 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #EF4444; text-transform: uppercase; letter-spacing: 0.05em;">
                    Unreviewed Errors
                </div>
                <div class="readiness-score-big" style="margin: 6px 0; color: #EF4444;">
                    {unreviewed_count}
                </div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">
                    Pending mastery
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_m2:
        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; height: 100%; padding: 18px 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #22C55E; text-transform: uppercase; letter-spacing: 0.05em;">
                    Resolved Errors
                </div>
                <div class="readiness-score-big" style="margin: 6px 0; color: #22C55E;">
                    {reviewed_count}
                </div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">
                    Reinforced & mastered
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_m3:
        if breakdown:
            df_err = pd.DataFrame(breakdown)
            fig = px.bar(
                df_err,
                x="count",
                y="type",
                orientation="h",
                color="type",
                text="pct",
                title="Error Pattern Distribution (%)",
                color_discrete_sequence=["#EF4444", "#F97316", "#EAB308", "#38BDF8", "#A855F7", "#EC4899", "#10B981"]
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=30, b=10),
                height=140,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", size=11),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False)
            )
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Log test or quiz errors to unlock Error Pattern Analytics!")

    if unreviewed_count > 0:
        if st.button("🔥 Launch Interactive Mistake Re-Quiz", type="primary", use_container_width=True, key="rev_launch_requiz_btn"):
            req = generate_mistake_requiz(user_id, limit=min(10, unreviewed_count))
            if req:
                st.session_state["active_quiz_id"] = req["quiz_id"]
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_results"] = None
                st.session_state["practice_active_tab"] = "🎯 Quiz Engine"
                st.session_state["current_page"] = "🎯 Practice"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    tab_list, tab_add = st.tabs(["📋 View Vault", "➕ Log New Mistake"])

    with tab_add:
        st.subheader("Log a Test or Practice Error")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="mst_rev_subj_select")
            sel_subj_id = s_map[sel_subj_name]

            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with col_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="mst_rev_chap_select")

            topics = get_topics_for_chapter(user_id, c_map[sel_chap_name]) if (c_map and sel_chap_name in c_map) else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with col_s3:
                sel_top_name = st.selectbox("Topic (Optional)", ["None"] + list(t_map.keys()), key="mst_rev_top_select")

            sel_chap_id = c_map.get(sel_chap_name)
            sel_top_id = t_map.get(sel_top_name) if sel_top_name != "None" else None

            render_latex_math_keyboard("mst_rev_add_question_txt", label="LaTeX & Equation Formula Palette")

            question_txt = st.text_area("Question / Problem Prompt", placeholder="e.g. Find the focal length of a concave lens if power is -2.0 D... or $$E = \\frac{hc}{\\lambda}$$", key="mst_rev_add_question_txt")

            c_a1, c_a2 = st.columns(2)
            with c_a1:
                your_ans = st.text_input("Your Answer / Error Made", placeholder="e.g. +50 cm", key="mst_rev_add_your_ans")
            with c_a2:
                corr_ans = st.text_input("Correct Answer", placeholder="e.g. -50 cm or -0.5 m", key="mst_rev_add_corr_ans")

            c_t1, c_t2 = st.columns(2)
            with c_t1:
                m_type = st.selectbox("Mistake Root Cause", MISTAKE_TYPES, key="mst_rev_add_m_type")
            with c_t2:
                prev_strat = st.text_input("Prevention Strategy", placeholder="e.g. Always check sign convention: concave focal length is negative", key="mst_rev_add_prev_strat")

            expl = st.text_area("Detailed Concept Explanation", placeholder="Power P = 1/f(in meters) -> f = 1/(-2) = -0.5 m = -50 cm.", key="mst_rev_add_expl")

            if st.button("⚡ Save to Mistake Vault (+20 XP)", use_container_width=True, type="primary", key="mst_rev_save_btn"):
                if not question_txt.strip():
                    st.error("Please enter the question text.")
                else:
                    add_mistake(
                        user_id=user_id,
                        question=question_txt,
                        mistake_type=m_type,
                        subject_id=sel_subj_id,
                        chapter_id=sel_chap_id,
                        topic_id=sel_top_id,
                        your_answer=your_ans,
                        correct_answer=corr_ans,
                        explanation=expl,
                        prevention_strategy=prev_strat
                    )
                    st.success("Mistake recorded in Vault! +20 XP awarded.")
                    st.session_state["mst_rev_add_question_txt"] = ""
                    st.session_state["mst_rev_add_your_ans"] = ""
                    st.session_state["mst_rev_add_corr_ans"] = ""
                    st.session_state["mst_rev_add_expl"] = ""
                    st.session_state["mst_rev_add_prev_strat"] = ""
                    st.rerun()

    with tab_list:
        subjects = get_all_subjects(user_id)
        s_filt_opts = {"All Subjects": None}
        if subjects:
            s_filt_opts.update({s["name"]: s["id"] for s in subjects})

        c_f1, c_f2, c_f3 = st.columns([1, 1, 2])
        with c_f1:
            sel_s_filt = st.selectbox("Filter Subject", list(s_filt_opts.keys()), key="mst_rev_filt_subj")
        with c_f2:
            status_filter = st.selectbox("Status", ["All", "Unreviewed (Pending)", "Resolved (Mastered)"], key="mst_rev_filt_stat")
        with c_f3:
            search_query = st.text_input("🔍 Search Mistakes", placeholder="Search questions, concepts, or prevention rules...", key="mst_rev_search_q")

        # Anki & CSV Export Action Buttons
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            anki_data = export_mistakes_to_anki(user_id, subject_id=s_filt_opts[sel_s_filt], format_type="tsv")
            st.download_button(
                label="📥 Export Mistake Deck to Anki (.tsv)",
                data=anki_data,
                file_name="Nexus_Mistake_Vault.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="mst_rev_dl_anki"
            )
        with c_exp2:
            csv_data = export_mistakes_to_anki(user_id, subject_id=s_filt_opts[sel_s_filt], format_type="csv")
            st.download_button(
                label="📊 Export Mistake Deck to CSV (.csv)",
                data=csv_data,
                file_name="Nexus_Mistake_Vault.csv",
                mime="text/csv",
                use_container_width=True,
                key="mst_rev_dl_csv"
            )

        st.markdown("---")

        is_rev_bool = None
        if status_filter == "Unreviewed (Pending)":
            is_rev_bool = False
        elif status_filter == "Resolved (Mastered)":
            is_rev_bool = True

        mistakes = get_all_mistakes(user_id, subject_id=s_filt_opts[sel_s_filt], is_reviewed=is_rev_bool)
        if search_query:
            q = search_query.lower()
            mistakes = [m for m in mistakes if q in m["question"].lower() or q in m.get("explanation", "").lower() or q in m.get("prevention_strategy", "").lower()]

        if not mistakes:
            render_empty_state("❌", "No Mistakes Found", "Log your exam and quiz errors to build a resilient error-prevention system!")
        else:
            for m in mistakes:
                with st.container():
                    is_rev = bool(m.get("is_reviewed", 0))
                    border_c = "#22C55E" if is_rev else "#EF4444"
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {border_c};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span class="nexus-pill-critical" style="background: rgba(239,68,68,0.12); color: {border_c};">
                                        {m.get('mistake_type', 'Mistake')}
                                    </span>
                                    <span style="font-size: 0.8rem; font-weight: 700; color: {m.get('subject_color', '#38BDF8')};">
                                        {m.get('subject_name')}
                                    </span>
                                    <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">› {m.get('chapter_name')}</span>
                                </div>
                                <span style="font-size: 0.8rem; color: {'#22C55E' if is_rev else '#EF4444'}; font-weight: 700;">
                                    {'✅ Mastered' if is_rev else '⚠️ Pending Review'}
                                </span>
                            </div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 6px;">
                                ❓ {m['question']}
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 8px 0; font-size: 0.85rem;">
                                <div style="background: rgba(239, 68, 68, 0.08); padding: 8px 10px; border-radius: 8px; border-left: 3px solid #EF4444;">
                                    <strong style="color: #EF4444;">Your Error:</strong> {m.get('your_answer') or 'N/A'}
                                </div>
                                <div style="background: rgba(34, 197, 94, 0.08); padding: 8px 10px; border-radius: 8px; border-left: 3px solid #22C55E;">
                                    <strong style="color: #22C55E;">Correct Solution:</strong> {m.get('correct_answer') or 'N/A'}
                                </div>
                            </div>
                            {f'<div style="font-size: 0.85rem; color: var(--nexus-text-title); margin: 6px 0;">💡 <strong>Explanation:</strong> {m["explanation"]}</div>' if m.get("explanation") else ''}
                            {f'<div style="font-size: 0.82rem; color: #38BDF8; margin: 4px 0;">🛡️ <strong>Prevention Rule:</strong> {m["prevention_strategy"]}</div>' if m.get("prevention_strategy") else ''}
                        </div>
                    """, unsafe_allow_html=True)

                    c_act1, c_act2, c_pad = st.columns([1.5, 1, 4])
                    with c_act1:
                        lbl = "↩️ Mark Unresolved" if is_rev else "✅ Mark Resolved"
                        if st.button(lbl, key=f"mst_rev_tog_{m['id']}", use_container_width=True):
                            toggle_mistake_reviewed(user_id, m['id'], 0 if is_rev else 1)
                            st.rerun()
                    with c_act2:
                        if st.button("🗑️ Delete", key=f"mst_rev_del_{m['id']}", use_container_width=True):
                            delete_mistake(user_id, m['id'])
                            st.toast("Mistake removed", icon="🗑️")
                            st.rerun()
                    st.markdown("<hr style='margin: 10px 0; opacity: 0.15;'/>", unsafe_allow_html=True)
