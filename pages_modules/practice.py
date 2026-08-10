"""
practice.py — Nexus Unified Practice Module.

Consolidates:
1. 🎯 Quiz Engine (Adaptive testing, MCQs, Mistake Vault auto-sync, Mistake Re-Quiz, History)
2. 💡 Active Recall Studio (Feynman technique retrieval, LaTeX formula keyboard, self-evaluation 1-5, Anki export)
"""

import streamlit as st
import json
import plotly.express as px
from models import (
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    create_quiz,
    get_quiz_by_id,
    get_question_bank_for_topic,
    submit_quiz_and_sync_nexus,
    get_quiz_history,
    generate_mistake_requiz,
    get_unreviewed_mistakes_for_quiz,
    get_active_recall_prompt,
    save_active_recall_session,
    get_recall_history,
    get_recall_stats,
    get_user_theme
)
from styles import render_header, render_breadcrumbs, render_empty_state
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_active_recall_to_anki


def render_practice_page(user_id: int):
    user_theme = get_user_theme(user_id)
    render_breadcrumbs(["🏠 Dashboard", "🎯 Practice"])

    render_header(
        "🎯 Adaptive Practice & Retrieval Studio",
        "Test conceptual mastery with targeted syllabus quizzes, Feynman active recall, and error retesting.",
        theme=user_theme
    )

    # Check if a tab was requested via shortcut
    active_tab = st.session_state.get("practice_active_tab", "🎯 Quiz Engine")

    tab_quiz, tab_recall = st.tabs([
        "🎯 Quiz Engine",
        "💡 Active Recall"
    ])

    with tab_quiz:
        _render_quiz_engine_view(user_id)

    with tab_recall:
        _render_active_recall_view(user_id)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 1: QUIZ ENGINE
# ══════════════════════════════════════════════════════════════════════════

def _render_quiz_engine_view(user_id: int):
    unreviewed_mistakes = get_unreviewed_mistakes_for_quiz(user_id, limit=20)

    subtab_gen, subtab_active, subtab_hist = st.tabs([
        "🎯 Quiz Generator",
        "📝 Active Quiz Player",
        "📊 History & Analytics"
    ])

    with subtab_gen:
        c_mode1, c_mode2 = st.columns([1.5, 1])

        with c_mode1:
            st.markdown("### 📚 Create Syllabus Quiz")
            subjects = get_all_subjects(user_id)
            if not subjects:
                st.warning("Please configure subjects in the Syllabus Manager first.")
            else:
                s_map = {s["name"]: s["id"] for s in subjects}
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    sel_subj_name = st.selectbox("Select Subject", list(s_map.keys()), key="prac_qz_gen_subj")
                sel_subj_id = s_map[sel_subj_name]

                chapters = get_chapters_for_subject(user_id, sel_subj_id)
                c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
                with c_s2:
                    sel_chap_name = st.selectbox("Select Chapter", list(c_map.keys()) if c_map else ["All Chapters"], key="prac_qz_gen_chap")
                sel_chap_id = c_map.get(sel_chap_name) if sel_chap_name != "All Chapters" else None

                topics = get_topics_for_chapter(user_id, sel_chap_id) if sel_chap_id else []
                t_map = {t["name"]: t["id"] for t in topics} if topics else {}

                sel_top_name = st.selectbox("Select Topic (Optional)", ["All Chapter Topics"] + list(t_map.keys()), key="prac_qz_gen_top")
                sel_top_id = t_map.get(sel_top_name) if sel_top_name != "All Chapter Topics" else None

                c_opt1, c_opt2 = st.columns(2)
                with c_opt1:
                    difficulty = st.selectbox("Difficulty Level", ["Mixed", "Foundational", "Advanced", "Board Exam Level"], key="prac_qz_gen_diff")
                with c_opt2:
                    q_count = st.selectbox("Number of Questions", [5, 10, 15], index=0, key="prac_qz_gen_count")

                auto_save = st.checkbox("💾 Auto-send incorrect answers to Mistake Vault", value=True, key="prac_qz_auto_save_opt")

                if st.button("🚀 Generate & Launch Quiz", type="primary", use_container_width=True, key="prac_qz_launch_btn"):
                    questions = get_question_bank_for_topic(
                        user_id=user_id,
                        subject_id=sel_subj_id,
                        chapter_id=sel_chap_id,
                        topic_id=sel_top_id,
                        difficulty=difficulty,
                        count=q_count
                    )

                    target_label = sel_top_name if sel_top_id else (sel_chap_name if sel_chap_id else sel_subj_name)
                    quiz_title = f"{sel_subj_name} • {target_label} ({difficulty})"

                    quiz_id = create_quiz(
                        user_id=user_id,
                        title=quiz_title,
                        subject_id=sel_subj_id,
                        chapter_id=sel_chap_id,
                        topic_id=sel_top_id,
                        difficulty=difficulty,
                        questions_json=json.dumps(questions)
                    )

                    st.session_state["active_quiz_id"] = quiz_id
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_results"] = None
                    st.session_state["quiz_auto_save"] = auto_save
                    st.success("Quiz generated! Switched to Active Quiz Player.")
                    st.rerun()

        with c_mode2:
            st.markdown("### ❌ Mistake Vault Re-Quiz")
            st.markdown(f"""
                <div class="readiness-container" style="padding: 20px; text-align: center;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #EF4444; text-transform: uppercase;">
                        TARGETED RETESTING
                    </div>
                    <div class="readiness-score-big" style="color: #EF4444; margin: 6px 0;">
                        {len(unreviewed_mistakes)}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--nexus-text-sub); margin-bottom: 14px;">
                        Unresolved errors awaiting mastery
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if unreviewed_mistakes:
                if st.button("🔥 Launch Mistake Vault Re-Quiz", type="secondary", use_container_width=True, key="prac_qz_launch_requiz_btn"):
                    req = generate_mistake_requiz(user_id, limit=min(10, len(unreviewed_mistakes)))
                    if req:
                        st.session_state["active_quiz_id"] = req["quiz_id"]
                        st.session_state["quiz_submitted"] = False
                        st.session_state["quiz_results"] = None
                        st.session_state["quiz_auto_save"] = True
                        st.success("Mistake Re-Quiz generated! Let's eliminate those errors.")
                        st.rerun()
            else:
                st.info("🎉 No pending mistakes! All errors resolved.")

    with subtab_active:
        active_quiz_id = st.session_state.get("active_quiz_id")

        if not active_quiz_id:
            render_empty_state("🎯", "No Active Quiz in Session", "Generate a topic quiz or launch a Mistake Re-Quiz from the generator tab above!")
        else:
            quiz = get_quiz_by_id(user_id, active_quiz_id)
            if not quiz:
                st.warning("Quiz session not found.")
            else:
                questions = json.loads(quiz.get("questions_json", "[]"))

                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <span style="font-size: 0.78rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">
                                {quiz.get('subject_name', 'General')} • {quiz.get('difficulty', 'Mixed')}
                            </span>
                            <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--nexus-text-title); margin: 2px 0 0 0;">
                                {quiz.get('title')}
                            </h2>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.85rem; color: var(--nexus-text-sub);">
                                Total: <strong>{len(questions)} Questions</strong>
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                is_submitted = st.session_state.get("quiz_submitted", False)
                results = st.session_state.get("quiz_results")

                if not is_submitted:
                    with st.form("prac_active_quiz_form"):
                        user_answers = {}
                        for idx, q in enumerate(questions, 1):
                            st.markdown(f"""
                                <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 14px; margin-bottom: 6px;">
                                    Q{idx}. {q['question']}
                                </div>
                            """, unsafe_allow_html=True)

                            opts = q.get("options", [])
                            ans = st.radio(
                                f"Options for Q{idx}",
                                opts,
                                key=f"prac_qz_ans_{active_quiz_id}_{q['id']}",
                                label_visibility="collapsed"
                            )
                            user_answers[str(q["id"])] = ans
                            st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

                        submit_quiz_btn = st.form_submit_button("🏁 Submit Assessment & Score", type="primary", use_container_width=True)
                        if submit_quiz_btn:
                            with st.spinner("Scoring assessment & syncing analytics..."):
                                res = submit_quiz_and_sync_nexus(
                                    user_id=user_id,
                                    quiz_id=active_quiz_id,
                                    user_answers=user_answers,
                                    auto_save_mistakes=st.session_state.get("quiz_auto_save", True)
                                )
                            st.session_state["quiz_submitted"] = True
                            st.session_state["quiz_results"] = res
                            st.rerun()

                else:
                    # Results Display
                    score = results["score"]
                    total = results["total"]
                    pct = results["accuracy_pct"]
                    res_color = "#22C55E" if pct >= 80 else ("#38BDF8" if pct >= 60 else ("#F59E0B" if pct >= 40 else "#EF4444"))

                    st.markdown(f"""
                        <div class="readiness-container" style="text-align: center; padding: 28px 20px; border-top: 4px solid {res_color};">
                            <div style="font-size: 0.85rem; font-weight: 700; color: {res_color}; text-transform: uppercase; letter-spacing: 0.08em;">
                                ASSESSMENT RESULT
                            </div>
                            <div class="readiness-score-big" style="color: {res_color}; margin: 8px 0;">
                                {score} / {total}
                            </div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: var(--nexus-text-title);">
                                {pct}% Conceptual Accuracy
                            </div>
                            <div style="font-size: 0.88rem; color: var(--nexus-text-sub); margin-top: 4px;">
                                {results['message']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 📋 Question Review & Solutions")
                    for idx, q_res in enumerate(results.get("detailed_breakdown", []), 1):
                        is_corr = q_res["is_correct"]
                        stat_badge = "✅ Correct" if is_corr else "❌ Incorrect"
                        badge_bg = "rgba(34, 197, 94, 0.15)" if is_corr else "rgba(239, 68, 68, 0.15)"
                        badge_col = "#22C55E" if is_corr else "#EF4444"

                        st.markdown(f"""
                            <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid {'rgba(34, 197, 94, 0.3)' if is_corr else 'rgba(239, 68, 68, 0.3)'}; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <strong style="color: var(--nexus-text-title);">Q{idx}. {q_res['question']}</strong>
                                    <span style="background: {badge_bg}; color: {badge_col}; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 12px;">
                                        {stat_badge}
                                    </span>
                                </div>
                                <div style="font-size: 0.88rem; margin: 6px 0;">
                                    <strong>Your Answer:</strong> <span style="color: {badge_col};">{q_res['user_answer']}</span>
                                </div>
                                <div style="font-size: 0.88rem; margin: 4px 0; color: #22C55E;">
                                    <strong>Correct Answer:</strong> {q_res['correct_answer']}
                                </div>
                                <div style="font-size: 0.82rem; color: var(--nexus-text-sub); border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; margin-top: 6px;">
                                    💡 <strong>Explanation:</strong> {q_res.get('explanation', 'Review this concept carefully.')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("🔄 Retake This Quiz", use_container_width=True, key="prac_retake_qz_btn"):
                            st.session_state["quiz_submitted"] = False
                            st.session_state["quiz_results"] = None
                            st.rerun()
                    with c_btn2:
                        if st.button("➕ Generate New Quiz", type="primary", use_container_width=True, key="prac_new_qz_btn"):
                            st.session_state["active_quiz_id"] = None
                            st.session_state["quiz_submitted"] = False
                            st.session_state["quiz_results"] = None
                            st.rerun()

    with subtab_hist:
        st.subheader("📊 Quiz Performance History")
        history = get_quiz_history(user_id, limit=20)
        if not history:
            render_empty_state("📊", "No Quiz History Yet", "Complete your first quiz above to track accuracy trends and mastery progression!")
        else:
            for h in history:
                pct = h["accuracy_pct"]
                col_c = "#22C55E" if pct >= 80 else ("#38BDF8" if pct >= 60 else ("#F59E0B" if pct >= 40 else "#EF4444"))
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {col_c}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: var(--nexus-text-title); font-size: 1.05rem;">{h['title']}</span>
                                <div style="font-size: 0.82rem; color: var(--nexus-text-sub); margin-top: 2px;">
                                    {h.get('subject_name', '')} • {h['created_at']}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.4rem; font-weight: 800; color: {col_c};">{pct}%</span>
                                <div style="font-size: 0.78rem; color: var(--nexus-text-sub);">{h['score']}/{h['total_questions']} correct</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 2: ACTIVE RECALL STUDIO
# ══════════════════════════════════════════════════════════════════════════

def _render_active_recall_view(user_id: int):
    tab_practice, tab_history = st.tabs([
        "💡 Active Recall Session",
        "📜 Recall Logs & Insights"
    ])

    with tab_practice:
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please configure subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            
            # Check prefill from shortcut
            target_topic_id = st.session_state.get("active_recall_target_topic_id")

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="prac_rec_subj")
            sel_subj_id = s_map[sel_subj_name]

            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with col_s2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="prac_rec_chap")
            sel_chap_id = c_map.get(sel_chap_name)

            topics = get_topics_for_chapter(user_id, sel_chap_id) if sel_chap_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            
            # Topic preselect index
            top_idx = 0
            if target_topic_id and t_map:
                for i, (tn, tid) in enumerate(t_map.items()):
                    if tid == target_topic_id:
                        top_idx = i
                        break

            with col_s3:
                sel_top_name = st.selectbox("Topic to Recall", list(t_map.keys()) if t_map else ["None"], index=top_idx, key="prac_rec_top")
            sel_top_id = t_map.get(sel_top_name)

            if not sel_top_id:
                st.info("Select a topic above to generate your Feynman Active Recall prompt.")
            else:
                prompt_info = get_active_recall_prompt(user_id, sel_top_id)

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

                render_latex_math_keyboard("prac_active_recall_input_text", label="LaTeX & Equation Formula Palette")

                user_recall_text = st.text_area(
                    "✍️ Your Recall Explanation (Write from memory without notes):",
                    placeholder="Start typing your explanation here... Define the term, explain the step-by-step mechanism, state formulas like $$F = G \\frac{m_1 m_2}{r^2}$$, and list key applications...",
                    height=200,
                    key="prac_active_recall_input_text"
                )

                reveal_rubric = st.checkbox("👁️ Reveal Key Concept Rubric Checklist", value=False, key="prac_reveal_rubric")
                if reveal_rubric:
                    li_items = "".join([f"<li>{pt}</li>" for pt in prompt_info["rubric_points"]])
                    if prompt_info.get("formulas_text"):
                        li_items += f"<li><strong>Key Formulas:</strong> {prompt_info['formulas_text']}</li>"
                    st.markdown(f"""
                        <div style="background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                            <strong style="color: #A855F7; font-size: 0.9rem;">📌 Core Verification Rubric:</strong>
                            <ul style="margin: 6px 0 0 0; padding-left: 20px; font-size: 0.85rem; color: var(--nexus-text-title);">
                                {li_items}
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("### 🌟 Self-Evaluation Understanding Score")
                st.caption("How accurately and completely were you able to retrieve this concept from memory?")

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
                    }[x],
                    key="prac_recall_slider"
                )

                feedback_notes = st.text_input("Self-Reflection / What did you miss?", placeholder="e.g. Remembered formula but forgot the sign convention condition.", key="prac_active_recall_fb_notes")

                if st.button("⚡ Save Active Recall & Update Topic Mastery", type="primary", use_container_width=True, key="prac_save_recall_btn"):
                    if not user_recall_text.strip():
                        st.error("Please write your recall response before submitting.")
                    else:
                        save_active_recall_session(
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
                            st.warning("Recall recorded. Topic marked for urgent review. Adaptive Spaced Revision automatically scheduled for tomorrow!")
                        else:
                            st.success("Recall session saved! Topic understanding updated to 3/5 stars. +25 XP awarded!")
                        st.session_state["prac_active_recall_input_text"] = ""
                        st.session_state["prac_active_recall_fb_notes"] = ""
                        st.session_state.pop("active_recall_target_topic_id", None)
                        st.rerun()

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
                    <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">Average Score</div>
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

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            anki_data = export_active_recall_to_anki(user_id, format_type="tsv")
            st.download_button(
                label="📥 Export Recall Decks to Anki (.tsv)",
                data=anki_data,
                file_name="Nexus_Active_Recall_Decks.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="prac_dl_recall_anki"
            )
        with c_exp2:
            csv_data = export_active_recall_to_anki(user_id, format_type="csv")
            st.download_button(
                label="📊 Export Recall Decks to CSV (.csv)",
                data=csv_data,
                file_name="Nexus_Active_Recall_Decks.csv",
                mime="text/csv",
                use_container_width=True,
                key="prac_dl_recall_csv"
            )

        st.markdown("---")
        if not history:
            render_empty_state("💡", "No Recall History Yet", "Complete a Feynman recall session above to build your retrieval log.")
        else:
            for item in history:
                sc = item.get("understanding_score", 3)
                col = "#22C55E" if sc >= 4 else ("#38BDF8" if sc == 3 else "#EF4444")
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {col}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; color: var(--nexus-text-title); font-size: 1.05rem;">{item['topic_name']}</span>
                                <span style="color: var(--nexus-text-sub); font-size: 0.82rem;"> • {item.get('subject_name', '')} › {item.get('chapter_name', '')}</span>
                                <div style="font-size: 0.88rem; color: var(--nexus-text-title); margin-top: 4px;">
                                    📝 <em>"{item.get('user_response', '')[:120]}..."</em>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.1rem; font-weight: 800; color: {col};">★ {sc}/5</span>
                                <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">{item['created_at']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
