"""
mistakes.py — Nexus Mistake Vault & Error Pattern Analytics.
"""

import streamlit as st
import plotly.express as px
from models import (
    add_mistake,
    get_all_mistakes,
    get_mistake_analytics,
    toggle_mistake_reviewed,
    delete_mistake,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    generate_mistake_requiz,
    get_mistake_trend
)
from styles import render_breadcrumbs
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_mistakes_to_anki

MISTAKE_TYPES = [
    "Conceptual",
    "Calculation",
    "Memory",
    "Careless Reading",
    "Formula",
    "Interpretation",
    "Application"
]


def render_mistakes_page(user_id: int):
    render_breadcrumbs(["🏠 Dashboard", "❌ Mistake Vault"])

    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); color: #EF4444; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>❌</span> <span>ERROR PATTERN MASTERY & RE-QUIZ</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Mistake Vault
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Analyze past exam & quiz errors, master recurring misconceptions, launch targeted Re-Quizzes, and boost your Exam Readiness score.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    analytics = get_mistake_analytics(user_id)
    total_mistakes = analytics.get("total", 0)
    unreviewed_count = analytics.get("unreviewed", 0)
    reviewed_count = analytics.get("reviewed", 0)
    breakdown = analytics.get("breakdown", [])

    # Overview Analytics Bar
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
                    Mastered Errors
                </div>
                <div class="readiness-score-big" style="margin: 6px 0; color: #22C55E;">
                    {reviewed_count}
                </div>
                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">
                    Resolved & reinforced
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_m3:
        if breakdown:
            import pandas as pd
            df_err = pd.DataFrame(breakdown)
            fig = px.bar(
                df_err,
                x="count",
                y="type",
                orientation="h",
                color="type",
                text="pct",
                title="Common Error Pattern Distribution (%)",
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
            st.info("Log your practice or test questions to unlock Error Pattern Analytics!")

    # Action Quick Launch
    if unreviewed_count > 0:
        if st.button("🔥 Launch Interactive Mistake Re-Quiz (Take Test Now)", type="primary", use_container_width=True):
            req = generate_mistake_requiz(user_id, limit=min(10, unreviewed_count))
            if req:
                st.session_state["active_quiz_id"] = req["quiz_id"]
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_results"] = None
                st.session_state["current_page"] = "🎯 Quiz Engine"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Filter & Log Controls
    tab_list, tab_add, tab_review = st.tabs(["📋 View Vault", "➕ Log New Mistake", "🎯 Rapid Review Mode"])

    with tab_add:
        st.subheader("Log a Test or Practice Error")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="mst_subj_select")
            
            sel_subj_id = s_map[sel_subj_name]
            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            
            with col_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="mst_chap_select")
                
            topics = get_topics_for_chapter(user_id, c_map[sel_chap_name]) if (c_map and sel_chap_name in c_map) else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            
            with col_s3:
                sel_top_name = st.selectbox("Topic (Optional)", ["None"] + list(t_map.keys()), key="mst_top_select")
                
            sel_chap_id = c_map.get(sel_chap_name)
            sel_top_id = t_map.get(sel_top_name) if sel_top_name != "None" else None

            # Visual LaTeX Math Keyboard for science & math question entry
            render_latex_math_keyboard("mst_add_question_txt", label="LaTeX & Equation Formula Palette")

            question_txt = st.text_area("Question / Problem Prompt", placeholder="e.g. Find the focal length of a concave lens if power is -2.0 D... or $$E = \\frac{hc}{\\lambda}$$", key="mst_add_question_txt")
            
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                your_ans = st.text_input("Your Answer / Error Made", placeholder="e.g. +50 cm", key="mst_add_your_ans")
            with c_a2:
                corr_ans = st.text_input("Correct Answer", placeholder="e.g. -50 cm or -0.5 m", key="mst_add_corr_ans")
            
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                m_type = st.selectbox("Mistake Root Cause", MISTAKE_TYPES, key="mst_add_m_type")
            with c_t2:
                prev_strat = st.text_input("Prevention Strategy", placeholder="e.g. Always check sign convention: focal length of concave is negative", key="mst_add_prev_strat")
                
            expl = st.text_area("Detailed Concept Explanation", placeholder="Power P = 1/f(in meters) -> f = 1/(-2) = -0.5 m = -50 cm.", key="mst_add_expl")
            
            if st.button("⚡ Save to Mistake Vault (+20 XP)", use_container_width=True, type="primary", key="mst_save_btn"):
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
                    st.session_state["mst_add_question_txt"] = ""
                    st.session_state["mst_add_your_ans"] = ""
                    st.session_state["mst_add_corr_ans"] = ""
                    st.session_state["mst_add_prev_strat"] = ""
                    st.session_state["mst_add_expl"] = ""
                    st.rerun()

    with tab_list:
        subjects = get_all_subjects(user_id)
        s_filter_map = {"All Subjects": None}
        if subjects:
            s_filter_map.update({s["name"]: s["id"] for s in subjects})
            
        c_f1, c_f2, c_f3 = st.columns(3)
        with c_f1:
            filt_subj = st.selectbox("Filter Subject", list(s_filter_map.keys()), key="mst_filt_subj")
        with c_f2:
            filt_type = st.selectbox("Filter Mistake Type", ["All"] + MISTAKE_TYPES, key="mst_filt_type")
        with c_f3:
            filt_status = st.selectbox("Filter Status", ["All Mistakes", "Unreviewed Only", "Mastered Only"], key="mst_filt_status")

        is_rev_param = None
        if filt_status == "Unreviewed Only":
            is_rev_param = False
        elif filt_status == "Mastered Only":
            is_rev_param = True

        # ── 1-Click Anki & CSV Export Action Bar ──
        c_ank1, c_ank2 = st.columns(2)
        with c_ank1:
            anki_mst_tsv = export_mistakes_to_anki(
                user_id,
                subject_id=s_filter_map[filt_subj],
                unreviewed_only=(filt_status == "Unreviewed Only"),
                format_type="tsv"
            )
            st.download_button(
                label="📥 Export Mistakes to Anki Deck (.tsv)",
                data=anki_mst_tsv,
                file_name=f"Nexus_Mistakes_{filt_subj.replace(' ', '_')}.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="dl_mst_anki_tsv"
            )
        with c_ank2:
            anki_mst_csv = export_mistakes_to_anki(
                user_id,
                subject_id=s_filter_map[filt_subj],
                unreviewed_only=(filt_status == "Unreviewed Only"),
                format_type="csv"
            )
            st.download_button(
                label="📊 Export Mistakes (CSV for Sheets/Notion)",
                data=anki_mst_csv,
                file_name=f"Nexus_Mistakes_{filt_subj.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_mst_anki_csv"
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        mistakes = get_all_mistakes(user_id, subject_id=s_filter_map[filt_subj], mistake_type=filt_type, is_reviewed=is_rev_param)
        if not mistakes:
            st.info("No recorded mistakes matching the selected filter.")
        else:
            for m in mistakes:
                is_rev = bool(m.get("is_reviewed", 0))
                with st.container():
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {'#22C55E' if is_rev else '#EF4444'};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 6px; align-items: center;">
                                    <span class="{'nexus-pill-badge' if is_rev else 'nexus-pill-critical'}">{m.get('mistake_type', 'Conceptual')}</span>
                                    <span style="font-size: 0.8rem; font-weight: 700; color: {m.get('subject_color', '#38BDF8')};">{m.get('subject_name', '')}</span>
                                    <span style="font-size: 0.75rem; color: var(--nexus-text-sub);">{m.get('chapter_name', '')}</span>
                                </div>
                                <div>
                                    <span style="font-size: 0.75rem; font-weight: 700; color: {'#22C55E' if is_rev else '#EF4444'};">
                                        {'✨ MASTERED' if is_rev else '⚠️ UNREVIEWED'}
                                    </span>
                                    <span style="font-size: 0.75rem; color: var(--nexus-text-sub); margin-left: 8px;">{str(m.get('created_at', ''))[:10]}</span>
                                </div>
                            </div>
                            <div style="font-size: 1.0rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                                ❓ {m['question']}
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem; margin-bottom: 8px;">
                                <div style="background: rgba(239, 68, 68, 0.08); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.2);">
                                    <strong style="color: #EF4444;">❌ Your Answer:</strong> {m.get('your_answer') or 'N/A'}
                                </div>
                                <div style="background: rgba(34, 197, 94, 0.08); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(34, 197, 94, 0.2);">
                                    <strong style="color: #22C55E;">✅ Correct Answer:</strong> {m.get('correct_answer') or 'N/A'}
                                </div>
                            </div>
                            {f'<div style="font-size: 0.85rem; color: var(--nexus-text-sub); margin-bottom: 4px;"><strong>💡 Explanation:</strong> {m["explanation"]}</div>' if m.get('explanation') else ''}
                            {f'<div style="font-size: 0.85rem; color: #F97316;"><strong>🛡️ Prevention:</strong> {m["prevention_strategy"]}</div>' if m.get('prevention_strategy') else ''}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c_b1, c_b2, c_b3 = st.columns([4, 2, 1])
                    with c_b2:
                        toggle_label = "↩️ Reopen Error" if is_rev else "✅ Mark Mastered (+15 XP)"
                        if st.button(toggle_label, key=f"tog_mst_{m['id']}", use_container_width=True):
                            toggle_mistake_reviewed(user_id, m["id"])
                            st.toast("Mistake status updated!" if is_rev else "Mastered! +15 XP", icon="✨")
                            st.rerun()
                    with c_b3:
                        if st.button("🗑️ Delete", key=f"del_mst_{m['id']}", use_container_width=True):
                            delete_mistake(user_id, m['id'])
                            st.toast("Deleted from Vault", icon="🗑️")
                            st.rerun()

    with tab_review:
        st.subheader("🎯 Rapid Flashcard Mistake Review")
        mistakes = get_all_mistakes(user_id, is_reviewed=False)
        if not mistakes:
            st.info("🎉 All mistakes reviewed! You have zero unreviewed errors in your vault.")
        else:
            if "mst_review_idx" not in st.session_state:
                st.session_state["mst_review_idx"] = 0
            
            idx = st.session_state["mst_review_idx"] % len(mistakes)
            cur = mistakes[idx]
            
            st.markdown(f"""
                <div class="readiness-container" style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #38BDF8; font-weight: 700; text-transform: uppercase;">
                        Reviewing Unresolved Mistake {idx + 1} of {len(mistakes)} • {cur.get('subject_name')}
                    </div>
                    <h2 style="font-family: 'Outfit', sans-serif; color: var(--nexus-text-title); margin: 16px 0;">
                        {cur['question']}
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            
            show_ans = st.checkbox("👁️ Reveal Correct Solution & Prevention Rule", key=f"rev_sol_{cur['id']}")
            if show_ans:
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                        <div style="color: #22C55E; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px;">
                            ✅ Correct Answer: {cur.get('correct_answer')}
                        </div>
                        <div style="color: var(--nexus-text-sub); font-size: 0.9rem; margin-bottom: 6px;">
                            <strong>Explanation:</strong> {cur.get('explanation')}
                        </div>
                        <div style="color: #F97316; font-size: 0.9rem;">
                            <strong>Prevention Strategy:</strong> {cur.get('prevention_strategy')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            c_p, c_m, c_n = st.columns([1, 1.2, 1])
            with c_p:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state["mst_review_idx"] = (idx - 1) % len(mistakes)
                    st.rerun()
            with c_m:
                if st.button("✅ Mark Mastered (+15 XP)", use_container_width=True, type="primary"):
                    toggle_mistake_reviewed(user_id, cur["id"])
                    st.toast("Marked as Mastered! +15 XP", icon="✨")
                    st.session_state["mst_review_idx"] = idx % max(1, len(mistakes) - 1)
                    st.rerun()
            with c_n:
                if st.button("➡️ Next", use_container_width=True):
                    st.session_state["mst_review_idx"] = (idx + 1) % len(mistakes)
                    st.rerun()
