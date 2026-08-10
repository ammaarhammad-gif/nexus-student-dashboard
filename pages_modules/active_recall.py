"""
active_recall.py — Nexus Active Recall Studio & Feynman Technique Workspace.
"""

import streamlit as st
from models import (
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    get_active_recall_prompt,
    save_active_recall_session,
    get_recall_history,
    get_recall_stats
)
from styles import render_breadcrumbs
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_active_recall_to_anki


def render_active_recall_page(user_id: int):
    render_breadcrumbs(["🏠 Dashboard", "💡 Active Recall"])
    
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.35); color: #A855F7; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>💡</span> <span>FEYNMAN COGNITIVE MASTERY</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Active Recall Studio
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Explain concepts from memory without looking at notes. Test real comprehension, benchmark understanding, and trigger adaptive revisions automatically.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_practice, tab_history = st.tabs([
        "💡 Active Recall Session",
        "📜 Recall Logs & Insights"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1: ACTIVE RECALL PRACTICE
    # ══════════════════════════════════════════════════════════
    with tab_practice:
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please configure subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="rec_subj")
            sel_subj_id = s_map[sel_subj_name]

            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with col_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="rec_chap")
            sel_chap_id = c_map.get(sel_chap_name)

            topics = get_topics_for_chapter(user_id, sel_chap_id) if sel_chap_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with col_s3:
                sel_top_name = st.selectbox("Topic to Recall", list(t_map.keys()) if t_map else ["None"], key="rec_top")
            sel_top_id = t_map.get(sel_top_name)

            if not sel_top_id:
                st.info("Select a topic above to generate your Active Recall prompt.")
            else:
                prompt_info = get_active_recall_prompt(user_id, sel_top_id)
                
                # Active Recall Prompt Box
                st.markdown(f"""
                    <div class="readiness-container" style="padding: 24px; margin: 18px 0; border-left: 4px solid #A855F7;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #A855F7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                            🎯 FEYNMAN RECALL CHALLENGE
                        </div>
                        <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--nexus-text-title); margin: 0 0 10px 0;">
                            {prompt_info['topic_name']} ({prompt_info['chapter_name']})
                        </h2>
                        <p style="font-size: 1.0rem; color: var(--nexus-text-title); line-height: 1.5; margin: 0;">
                            {prompt_info['prompt_text']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                # Embed Visual LaTeX Math Keyboard for derivations and science formulas
                render_latex_math_keyboard("active_recall_input_text", label="LaTeX & Equation Formula Palette")

                user_recall_text = st.text_area(
                    "✍️ Your Recall Explanation (Write from memory without notes):",
                    placeholder="Start typing your explanation here... Define the term, explain the step-by-step mechanism, state formulas like $$F = G \\frac{m_1 m_2}{r^2}$$, and list real-world applications...",
                    height=200,
                    key="active_recall_input_text"
                )

                reveal_rubric = st.checkbox("👁️ Reveal Key Concept Rubric Checklist", value=False)
                if reveal_rubric:
                    st.markdown("""
                        <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                            <strong style="color: #A855F7; font-size: 0.9rem;">📌 Core Verification Rubric:</strong>
                            <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 0.85rem; color: var(--nexus-text-title);">
                    """, unsafe_allow_html=True)
                    for pt in prompt_info["rubric_points"]:
                        st.markdown(f"<li>{pt}</li>", unsafe_allow_html=True)
                    if prompt_info.get("formulas_text"):
                        st.markdown(f"<li><strong>Key Formulas:</strong> {prompt_info['formulas_text']}</li>", unsafe_allow_html=True)
                    st.markdown("</ul></div>", unsafe_allow_html=True)

                st.markdown("### 🌟 Self-Evaluation Understanding Score")
                st.caption("How accurately and completely were you able to recall this concept?")
                
                understanding_slider = st.select_slider(
                    "Understanding Rating:",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: {
                        1: "⭐ 1 - Blank / Severe Gaps (Auto-Schedules 1d Revision)",
                        2: "⭐⭐ 2 - Weak / Struggled with core steps (Auto-Schedules 1d Revision)",
                        3: "⭐⭐⭐ 3 - Moderate / Grasped main idea (Schedules Standard Revision)",
                        4: "⭐⭐⭐⭐ 4 - Strong / Minor details missing (Advances Mastery)",
                        5: "⭐⭐⭐⭐⭐ 5 - Flawless / Mastered & Complete (Mastery Locked)"
                    }[x]
                )

                feedback_notes = st.text_input("Self-Reflection / What did you miss?", placeholder="e.g. Remembered formula but missed the sign convention condition.", key="active_recall_fb_notes")

                if st.button("⚡ Save Active Recall & Update Topic Mastery", type="primary", use_container_width=True, key="save_recall_btn"):
                    if not user_recall_text.strip():
                        st.error("Please write your recall response before submitting.")
                    else:
                        rec_id = save_active_recall_session(
                            user_id=user_id,
                            topic_id=sel_top_id,
                            prompt_text=prompt_info["prompt_text"],
                            user_response=user_recall_text,
                            evaluation_feedback=feedback_notes,
                            understanding_score=understanding_slider
                        )
                        if understanding_slider >= 4:
                            st.balloons()
                            st.success(f"Excellent recall! Topic understanding updated to {understanding_slider}/5 stars. +35 XP awarded!")
                        elif understanding_slider <= 2:
                            st.warning(f"Recall recorded. Topic marked for urgent review. Adaptive Spaced Revision automatically scheduled for tomorrow!")
                        else:
                            st.success(f"Recall session saved! Topic understanding updated to 3/5 stars. +25 XP awarded!")
                        st.session_state["active_recall_input_text"] = ""
                        st.session_state["active_recall_fb_notes"] = ""
                        st.rerun()

    # ══════════════════════════════════════════════════════════
    # TAB 2: RECALL LOGS & INSIGHTS
    # ══════════════════════════════════════════════════════════
    with tab_history:
        st.subheader("📊 Active Recall History & Mastery")
        stats = get_recall_stats(user_id)
        history = get_recall_history(user_id, limit=20)

        c_r1, c_r2, c_r3, c_r4 = st.columns(4)
        with c_r1:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #A855F7;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #A855F7; text-transform: uppercase;">Recall Sessions</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #A855F7; margin: 4px 0;">{stats['total_sessions']}</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Feynman practice attempts</div>
                </div>
            """, unsafe_allow_html=True)
        with c_r2:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #38BDF8;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">Average Self-Eval</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #38BDF8; margin: 4px 0;">{stats['avg_score']} / 5</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Understanding average</div>
                </div>
            """, unsafe_allow_html=True)
        with c_r3:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #22C55E;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #22C55E; text-transform: uppercase;">Strong Recalls</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #22C55E; margin: 4px 0;">{stats['strong_recalls']}</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">4-5 star masteries</div>
                </div>
            """, unsafe_allow_html=True)
        with c_r4:
            st.markdown(f"""
                <div class="metric-box" style="border-left: 4px solid #F97316;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F97316; text-transform: uppercase;">Unique Topics</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #F97316; margin: 4px 0;">{stats['unique_topics']}</div>
                    <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Curriculum coverage</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # ── 1-Click Anki & CSV Export Action Bar ──
        c_exp1, c_exp2 = st.columns([1, 1])
        with c_exp1:
            anki_recall_tsv = export_active_recall_to_anki(user_id, format_type="tsv")
            st.download_button(
                label="📥 Export Active Recall Deck to Anki (.tsv)",
                data=anki_recall_tsv,
                file_name="Nexus_Active_Recall_Deck.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="dl_recall_anki_tsv"
            )
        with c_exp2:
            anki_recall_csv = export_active_recall_to_anki(user_id, format_type="csv")
            st.download_button(
                label="📊 Export Active Recall (CSV for Notion/Sheets)",
                data=anki_recall_csv,
                file_name="Nexus_Active_Recall_Deck.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_recall_anki_csv"
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        if not history:
            st.info("No active recall logs recorded yet. Practice your first topic in the session tab above!")
        else:
            for h in history:
                score = h.get("understanding_score", 3)
                stars_str = "⭐" * score
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {'#22C55E' if score >= 4 else ('#F59E0B' if score == 3 else '#EF4444')}; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <div>
                                <span style="font-size: 0.75rem; font-weight: 700; color: {h.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 10px;">
                                    {h.get('subject_name')}
                                </span>
                                <strong style="color: var(--nexus-text-title); margin-left: 6px; font-size: 1.0rem;">{h.get('topic_name')}</strong>
                                <span style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-left: 6px;">({h.get('chapter_name')})</span>
                            </div>
                            <span style="font-size: 0.95rem; font-weight: 700; color: {'#22C55E' if score >= 4 else ('#F59E0B' if score == 3 else '#EF4444')};">
                                {stars_str} ({score}/5)
                            </span>
                        </div>
                        <div style="background: rgba(255,255,255,0.03); padding: 10px 12px; border-radius: 8px; font-size: 0.88rem; color: var(--nexus-text-title); margin-bottom: 6px; white-space: pre-wrap;">
                            {h.get('user_response', '')}
                        </div>
                        {f'<div style="font-size: 0.82rem; color: #F97316;"><strong>Reflection Notes:</strong> {h["evaluation_feedback"]}</div>' if h.get('evaluation_feedback') else ''}
                        <div style="font-size: 0.75rem; color: var(--nexus-text-sub); margin-top: 4px;">
                            Practiced on {str(h.get('created_at'))[:16]}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
