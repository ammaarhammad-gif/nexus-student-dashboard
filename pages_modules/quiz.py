"""
quiz.py — Nexus Interactive Quiz Engine & Adaptive Testing Studio.
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
    get_unreviewed_mistakes_for_quiz
)
from styles import render_breadcrumbs


def render_quiz_page(user_id: int):
    render_breadcrumbs(["🏠 Dashboard", "🎯 Quiz Engine"])
    
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38BDF8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>🎯</span> <span>ADAPTIVE ASSESSMENT ENGINE</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Nexus Quiz Engine
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Test your conceptual mastery with targeted syllabus quizzes, adaptive difficulty, instant scoring, and automated Mistake Vault syncing.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    unreviewed_mistakes = get_unreviewed_mistakes_for_quiz(user_id, limit=20)
    
    tab_take, tab_active, tab_history = st.tabs([
        "🎯 Quiz Generator",
        "📝 Active Quiz Player",
        "📊 History & Analytics"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1: QUIZ GENERATOR
    # ══════════════════════════════════════════════════════════
    with tab_take:
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
                    sel_subj_name = st.selectbox("Select Subject", list(s_map.keys()), key="qz_gen_subj")
                sel_subj_id = s_map[sel_subj_name]

                chapters = get_chapters_for_subject(user_id, sel_subj_id)
                c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
                with c_s2:
                    sel_chap_name = st.selectbox("Select Chapter", list(c_map.keys()) if c_map else ["All Chapters"], key="qz_gen_chap")
                sel_chap_id = c_map.get(sel_chap_name) if sel_chap_name != "All Chapters" else None

                topics = get_topics_for_chapter(user_id, sel_chap_id) if sel_chap_id else []
                t_map = {t["name"]: t["id"] for t in topics} if topics else {}
                
                sel_top_name = st.selectbox("Select Topic (Optional)", ["All Chapter Topics"] + list(t_map.keys()), key="qz_gen_top")
                sel_top_id = t_map.get(sel_top_name) if sel_top_name != "All Chapter Topics" else None

                c_opt1, c_opt2 = st.columns(2)
                with c_opt1:
                    difficulty = st.selectbox("Difficulty Level", ["Mixed", "Foundational", "Advanced", "Board Exam Level"], key="qz_gen_diff")
                with c_opt2:
                    q_count = st.selectbox("Number of Questions", [5, 10, 15], index=0, key="qz_gen_count")

                auto_save = st.checkbox("💾 Auto-send incorrect answers to Mistake Vault", value=True, key="qz_auto_save_opt")

                if st.button("🚀 Generate & Launch Quiz", type="primary", use_container_width=True, key="qz_launch_btn"):
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
                    st.success("Quiz generated! Redirecting to Active Quiz Player...")
                    st.rerun()

        with c_mode2:
            st.markdown("### ❌ Mistake Vault Re-Quiz")
            st.markdown(f"""
                <div class="readiness-container" style="padding: 20px; text-align: center;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #EF4444; text-transform: uppercase;">
                        TARGETED RETESTING
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #EF4444; margin: 6px 0;">
                        {len(unreviewed_mistakes)}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--nexus-text-sub); margin-bottom: 14px;">
                        Unresolved errors awaiting mastery
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if unreviewed_mistakes:
                if st.button("🔥 Launch Mistake Vault Re-Quiz", type="secondary", use_container_width=True, key="qz_launch_requiz_btn"):
                    req = generate_mistake_requiz(user_id, limit=min(10, len(unreviewed_mistakes)))
                    if req:
                        st.session_state["active_quiz_id"] = req["quiz_id"]
                        st.session_state["quiz_submitted"] = False
                        st.session_state["quiz_results"] = None
                        st.session_state["quiz_auto_save"] = True
                        st.success("Mistake Re-Quiz generated! Let's eliminate those errors.")
                        st.rerun()
            else:
                st.info("🎉 No pending mistakes! You can generate a standard topic quiz.")

    # ══════════════════════════════════════════════════════════
    # TAB 2: ACTIVE QUIZ PLAYER
    # ══════════════════════════════════════════════════════════
    with tab_active:
        active_quiz_id = st.session_state.get("active_quiz_id")
        
        if not active_quiz_id:
            st.info("No active quiz in session. Generate a quiz from the **🎯 Quiz Generator** tab above to get started!")
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
                    with st.form("active_quiz_form"):
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
                                key=f"qz_ans_{active_quiz_id}_{q['id']}",
                                label_visibility="collapsed"
                            )
                            user_answers[str(q["id"])] = ans
                            st.markdown("<hr style='opacity: 0.15; margin: 12px 0;'/>", unsafe_allow_html=True)

                        submit_quiz_btn = st.form_submit_button("⚡ Submit & Grade Quiz", type="primary", use_container_width=True)
                        if submit_quiz_btn:
                            auto_save = st.session_state.get("quiz_auto_save", True)
                            res = submit_quiz_and_sync_nexus(
                                user_id=user_id,
                                quiz_id=active_quiz_id,
                                user_answers=user_answers,
                                time_taken_seconds=60,
                                auto_save_mistakes=auto_save
                            )
                            st.session_state["quiz_submitted"] = True
                            st.session_state["quiz_results"] = res
                            st.session_state["user_answers_snapshot"] = user_answers
                            st.rerun()

                else:
                    # ── Results & Detailed Scorecard ──
                    acc = results["accuracy_pct"]
                    score = results["score"]
                    total = results["total"]
                    xp = results["earned_xp"]
                    mistakes_logged = results.get("mistakes_logged", 0)
                    solved_count = results.get("solved_mistakes_count", 0)

                    if acc >= 80.0:
                        st.balloons()
                        status_color = "#22C55E"
                        status_badge = "🏆 EXCELLENT CONCEPT MASTERY"
                    elif acc >= 60.0:
                        status_color = "#38BDF8"
                        status_badge = "👍 SOLID PERFORMANCE"
                    else:
                        status_color = "#EF4444"
                        status_badge = "⚠️ NEEDS REVISION"

                    st.markdown(f"""
                        <div class="readiness-container" style="text-align: center; padding: 26px 20px; margin-bottom: 20px;">
                            <div style="display: inline-block; background: rgba(56,189,248,0.12); color: {status_color}; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                                {status_badge}
                            </div>
                            <div style="font-family: 'Outfit', sans-serif; font-size: 3.5rem; font-weight: 800; color: {status_color}; margin: 4px 0;">
                                {score} / {total} <span style="font-size: 1.6rem; color: var(--nexus-text-sub);">({acc}%)</span>
                            </div>
                            <div style="font-size: 1rem; color: var(--nexus-text-title); font-weight: 700;">
                                +{xp} XP Earned • Study Streak Updated! 🔥
                            </div>
                            {f'<div style="font-size: 0.85rem; color: #EF4444; margin-top: 6px;">📥 {mistakes_logged} incorrect question(s) automatically saved to Mistake Vault</div>' if mistakes_logged > 0 else ''}
                            {f'<div style="font-size: 0.85rem; color: #22C55E; margin-top: 6px;">✨ {solved_count} mistake(s) marked MASTERED in Mistake Vault!</div>' if solved_count > 0 else ''}
                        </div>
                    """, unsafe_allow_html=True)

                    st.subheader("📋 Question by Question Breakdown")
                    answers_snapshot = st.session_state.get("user_answers_snapshot", {})

                    for idx, q in enumerate(questions, 1):
                        user_ans = answers_snapshot.get(str(q["id"]), "")
                        corr_ans = q.get("correct_answer", "")
                        is_correct = (user_ans == corr_ans)

                        border_col = "#22C55E" if is_correct else "#EF4444"
                        icon = "✅" if is_correct else "❌"

                        st.markdown(f"""
                            <div class="priority-item-card" style="border-left-color: {border_col}; margin-bottom: 12px;">
                                <div style="font-size: 0.95rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 6px;">
                                    {icon} Q{idx}. {q['question']}
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85rem; margin-bottom: 6px;">
                                    <div style="background: {'rgba(34,197,94,0.08)' if is_correct else 'rgba(239,68,68,0.08)'}; padding: 6px 10px; border-radius: 6px;">
                                        <strong>Your Answer:</strong> {user_ans}
                                    </div>
                                    <div style="background: rgba(34,197,94,0.08); padding: 6px 10px; border-radius: 6px;">
                                        <strong style="color: #22C55E;">Correct Answer:</strong> {corr_ans}
                                    </div>
                                </div>
                                <div style="font-size: 0.85rem; color: var(--nexus-text-sub);">
                                    💡 <strong>Explanation:</strong> {q.get('explanation', '')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    c_act1, c_act2 = st.columns(2)
                    with c_act1:
                        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
                            st.session_state["active_quiz_id"] = None
                            st.session_state["quiz_submitted"] = False
                            st.session_state["quiz_results"] = None
                            st.rerun()
                    with c_act2:
                        if st.button("❌ Open Mistake Vault ➔", use_container_width=True):
                            st.session_state["current_page"] = "❌ Mistake Vault"
                            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                            st.rerun()

    # ══════════════════════════════════════════════════════════
    # TAB 3: HISTORY & ANALYTICS
    # ══════════════════════════════════════════════════════════
    with tab_history:
        st.subheader("📊 Quiz Performance History")
        history = get_quiz_history(user_id, limit=20)
        
        if not history:
            st.info("No quiz attempts recorded yet. Take your first quiz to start tracking analytics!")
        else:
            total_attempts = len(history)
            avg_acc = sum(h["accuracy_pct"] for h in history) / total_attempts if total_attempts > 0 else 0
            total_correct = sum(h["score"] for h in history)
            total_q_all = sum(h["total_questions"] for h in history)

            c_h1, c_h2, c_h3, c_h4 = st.columns(4)
            with c_h1:
                st.markdown(f"""
                    <div class="metric-box" style="border-left: 4px solid #38BDF8;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">Quizzes Taken</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #38BDF8; margin: 4px 0;">{total_attempts}</div>
                        <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Assessment sessions</div>
                    </div>
                """, unsafe_allow_html=True)
            with c_h2:
                st.markdown(f"""
                    <div class="metric-box" style="border-left: 4px solid #22C55E;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #22C55E; text-transform: uppercase;">Average Accuracy</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #22C55E; margin: 4px 0;">{round(avg_acc, 1)}%</div>
                        <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Overall benchmark</div>
                    </div>
                """, unsafe_allow_html=True)
            with c_h3:
                st.markdown(f"""
                    <div class="metric-box" style="border-left: 4px solid #8B5CF6;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #8B5CF6; text-transform: uppercase;">Questions Solved</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #8B5CF6; margin: 4px 0;">{total_correct} / {total_q_all}</div>
                        <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Total problems answered</div>
                    </div>
                """, unsafe_allow_html=True)
            with c_h4:
                readiness_est = min(100, int(avg_acc * 0.95))
                st.markdown(f"""
                    <div class="metric-box" style="border-left: 4px solid #F97316;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #F97316; text-transform: uppercase;">Quiz Index</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #F97316; margin: 4px 0;">{readiness_est}/100</div>
                        <div style="font-size: 0.75rem; color: var(--nexus-text-sub);">Feeds Exam Readiness</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            
            # Accuracy Trend Chart
            import pandas as pd
            df_hist = pd.DataFrame(history)
            if not df_hist.empty and "created_at" in df_hist.columns:
                df_hist["date_str"] = df_hist["created_at"].astype(str).str[:16]
                df_hist_sorted = df_hist.sort_values("created_at")
                
                fig = px.line(
                    df_hist_sorted,
                    x="date_str",
                    y="accuracy_pct",
                    markers=True,
                    title="Accuracy Progression Over Time (%)",
                    labels={"accuracy_pct": "Accuracy (%)", "date_str": "Attempt Date"}
                )
                fig.update_layout(
                    height=240,
                    margin=dict(l=10, r=10, t=35, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8", size=11),
                    yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,0.06)")
                )
                fig.update_traces(line_color="#38BDF8", marker=dict(size=8, color="#38BDF8"))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # History Log Cards
            for h in history:
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: {'#22C55E' if h['accuracy_pct'] >= 75 else '#EF4444'}; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 0.75rem; font-weight: 700; color: {h.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 10px;">
                                    {h.get('subject_name', 'Quiz')}
                                </span>
                                <strong style="color: var(--nexus-text-title); margin-left: 6px; font-size: 0.95rem;">{h.get('quiz_title')}</strong>
                                <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-top: 2px;">
                                    {str(h.get('created_at'))[:16]} • {h.get('difficulty', 'Mixed')} Difficulty
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.15rem; font-weight: 800; color: {'#22C55E' if h['accuracy_pct'] >= 75 else '#EF4444'};">
                                    {h['score']} / {h['total_questions']} ({h['accuracy_pct']}%)
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
