"""
ai_command_center.py — Nexus AI Command Center UI & Cognitive Workspace.

Features:
- Dual-Engine AI Support:
  * Autonomous Cognitive Mode (Instantly active with 100% syllabus intelligence, Feynman explainer & quiz generators)
  * Cloud LLM Mode (Gemini / OpenAI / Groq / Anthropic)
- 7 Interactive Command Tabs:
  1. 🌟 Daily Intelligence Blueprint
  2. 💡 Concept Mentor & Feynman Explainer
  3. 🎯 AI Quiz Crafter (with 1-click Quiz Engine Export)
  4. 🗓️ Smart Study Planner (with 1-click Daily Planner Sync)
  5. 📊 Deep Progress Diagnostic
  6. 🔄 Spaced Revision Retention Strategist
  7. ❌ Mistake Vault Root-Cause Diagnostic
"""

import streamlit as st
import json
import datetime
from ai_service import nexus_ai, NexusContextBuilder
from models import (
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    create_quiz,
    add_daily_plan
)
from styles import render_breadcrumbs


def render_ai_command_center_page(user_id: int):
    render_breadcrumbs(["🏠 Dashboard", "🧠 AI Command Center"])

    status = nexus_ai.get_status()
    is_cloud = status.get("is_cloud", False)
    provider = status["provider"]
    model = status["model"]
    masked_key = status["masked_key"]

    # Header & Engine Status
    status_bg = "rgba(34, 197, 94, 0.12)"
    status_border = "rgba(34, 197, 94, 0.35)"
    status_color = "#22C55E"
    status_text = f"🟢 NEXUS COGNITIVE AI ACTIVE ({provider.upper() if is_cloud else 'AUTONOMOUS MODE'})"

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 16px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: {status_bg}; border: 1px solid {status_border}; color: {status_color}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>🧠</span> <span>{status_text}</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Nexus AI Command Center
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Your cognitive copilot powered by real-time syllabus analytics, adaptive diagnostic intelligence, and Feynman pedagogy.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # API Configuration Expander (Optional)
    with st.expander(f"⚙️ Optional: Connect External Cloud LLM {f'(Active: {provider.title()} {masked_key})' if is_cloud else '(Gemini / OpenAI / Groq)'}", expanded=False):
        c_k1, c_k2 = st.columns([1.5, 1])
        with c_k1:
            st.markdown("""
                **Nexus Cognitive AI runs autonomously out of the box.**
                If you wish to supercharge it with Google Gemini or OpenAI, configure keys in `.streamlit/secrets.toml` or Streamlit Cloud Secrets.
            """)
            st.markdown(status["setup_guide"])
        with c_k2:
            st.markdown("**Quick Session-Level Key**")
            st.caption("Enter an API key for testing during this browser session:")
            
            sel_prov = st.selectbox("Select Provider", ["gemini", "openai", "groq", "anthropic"], index=0, key="ai_prov_sel")
            custom_key_input = st.text_input("Enter API Key", type="password", placeholder="AIzaSy... / sk-...", key="ai_key_input")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("💾 Apply Key", use_container_width=True, type="primary"):
                    if custom_key_input.strip():
                        st.session_state["nexus_custom_ai_key"] = custom_key_input.strip()
                        st.session_state["nexus_custom_ai_provider"] = sel_prov
                        st.toast(f"Connected {sel_prov.upper()} key for this session!", icon="✨")
                        st.rerun()
            with c_btn2:
                if st.button("🔄 Reset to Default", use_container_width=True):
                    if "nexus_custom_ai_key" in st.session_state:
                        del st.session_state["nexus_custom_ai_key"]
                    st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # 7 Core Command Tabs
    tab_daily, tab_mentor, tab_quiz, tab_plan, tab_diag, tab_rev, tab_mistakes = st.tabs([
        "🌟 Daily Intelligence",
        "💡 Concept Mentor",
        "🎯 Quiz Crafter",
        "🗓️ Study Planner",
        "📊 Progress Diagnostic",
        "🔄 Revision Strategist",
        "❌ Error Diagnostic"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1: DAILY INTELLIGENCE BLUEPRINT
    # ══════════════════════════════════════════════════════════
    with tab_daily:
        st.subheader("🌟 Daily Academic Intelligence Blueprint")
        st.caption("AI analyzes today's exam proximity, weak understanding topics, and overdue revisions to build your personalized study strategy.")

        if st.button("🚀 Generate Today's AI Study Blueprint", type="primary", use_container_width=True, key="ai_gen_daily_btn"):
            with st.spinner("🧠 Nexus AI is analyzing your curriculum analytics and building your blueprint..."):
                try:
                    res = nexus_ai.generate_daily_recommendations(user_id)
                    st.session_state["ai_daily_blueprint"] = res["content"]
                except Exception as e:
                    st.error(f"AI Generation Failed: {e}")

        if "ai_daily_blueprint" in st.session_state:
            st.markdown(f"""
                <div class="readiness-container" style="padding: 24px; margin-top: 16px;">
                    {st.session_state['ai_daily_blueprint']}
                </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 2: CONCEPT MENTOR & FEYNMAN EXPLAINER
    # ══════════════════════════════════════════════════════════
    with tab_mentor:
        st.subheader("💡 AI Concept Mentor (Feynman Technique)")
        st.caption("Select any topic in your syllabus for a crystal-clear pedagogical explanation.")

        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please configure subjects in Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                sel_s_name = st.selectbox("Subject", list(s_map.keys()), key="ai_ment_subj")
            sel_s_id = s_map[sel_s_name]

            chapters = get_chapters_for_subject(user_id, sel_s_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with col_m2:
                sel_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="ai_ment_chap")
            sel_c_id = c_map.get(sel_c_name)

            topics = get_topics_for_chapter(user_id, sel_c_id) if sel_c_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with col_m3:
                sel_t_name = st.selectbox("Target Topic", list(t_map.keys()) if t_map else ["None"], key="ai_ment_top")
            sel_t_id = t_map.get(sel_t_name)

            c_st1, c_st2 = st.columns([1, 2])
            with c_st1:
                style_choice = st.selectbox(
                    "Explanation Pedagogical Style",
                    ["Feynman Technique (Plain English & Analogies)", "Board Exam Derivation (Step-by-Step & Formal)", "Visual Analogy (Mental Models)", "Socratic Derivation (Guided Questions)"],
                    key="ai_ment_style"
                )
            with c_st2:
                student_query = st.text_input("Specific Doubt / Question (Optional)", placeholder="e.g. Why is the focal length of a concave mirror considered negative?", key="ai_ment_query")

            if st.button("🧠 Explain Topic", type="primary", use_container_width=True, key="ai_ment_btn"):
                if not sel_t_id:
                    st.error("Please select a topic to explain.")
                else:
                    with st.spinner(f"🧠 Nexus AI is preparing your {style_choice} explanation for '{sel_t_name}'..."):
                        try:
                            res = nexus_ai.generate_explanation(user_id, sel_t_id, style_choice, student_query)
                            st.session_state["ai_explanation_result"] = res
                        except Exception as e:
                            st.error(f"AI Generation Failed: {e}")

            if "ai_explanation_result" in st.session_state:
                exp_res = st.session_state["ai_explanation_result"]
                st.markdown(f"""
                    <div class="readiness-container" style="padding: 24px; margin-top: 16px; border-left: 4px solid #A855F7;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #A855F7; text-transform: uppercase;">
                            {exp_res['subject_name']} • {exp_res['chapter_name']} • {exp_res['style']}
                        </div>
                        <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--nexus-text-title); margin: 4px 0 14px 0;">
                            {exp_res['topic_name']}
                        </h2>
                        {exp_res['content']}
                    </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 3: AI QUIZ CRAFTER (WITH 1-CLICK QUIZ ENGINE EXPORT)
    # ══════════════════════════════════════════════════════════
    with tab_quiz:
        st.subheader("🎯 AI Custom Quiz Crafter")
        st.caption("Generate tailored, board-exam caliber MCQs targeting specific topics or weak spots, with 1-click export directly into the interactive Quiz Engine.")

        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please configure subjects in Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            c_qz1, c_qz2, c_qz3 = st.columns(3)
            with c_qz1:
                sel_qz_s_name = st.selectbox("Subject", list(s_map.keys()), key="ai_qz_subj")
            sel_qz_s_id = s_map[sel_qz_s_name]

            chapters = get_chapters_for_subject(user_id, sel_qz_s_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with c_qz2:
                sel_qz_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["All Chapters"], key="ai_qz_chap")
            sel_qz_c_id = c_map.get(sel_qz_c_name) if sel_qz_c_name != "All Chapters" else None

            topics = get_topics_for_chapter(user_id, sel_qz_c_id) if sel_qz_c_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with c_qz3:
                sel_qz_t_name = st.selectbox("Topic (Optional)", ["All Topics"] + list(t_map.keys()), key="ai_qz_top")
            sel_qz_t_id = t_map.get(sel_qz_t_name) if sel_qz_t_name != "All Topics" else None

            c_qzo1, c_qzo2, c_qzo3 = st.columns(3)
            with c_qzo1:
                qz_diff = st.selectbox("Difficulty", ["Adaptive", "Foundational", "Board Exam Hard", "Tricky & Trap-Heavy"], key="ai_qz_diff")
            with c_qzo2:
                qz_cnt = st.selectbox("Question Count", [5, 8, 10], index=0, key="ai_qz_cnt")
            with c_qzo3:
                qz_focus = st.text_input("Custom Focus Prompt", placeholder="e.g. Focus on numerical problem traps", key="ai_qz_focus")

            if st.button("⚡ Craft AI Quiz", type="primary", use_container_width=True, key="ai_craft_qz_btn"):
                with st.spinner(f"🧠 Nexus AI is crafting {qz_cnt} high-rigor questions..."):
                    try:
                        qz_payload = nexus_ai.generate_ai_quiz(
                            user_id=user_id,
                            subject_id=sel_qz_s_id,
                            chapter_id=sel_qz_c_id,
                            topic_id=sel_qz_t_id,
                            difficulty=qz_diff,
                            count=qz_cnt,
                            focus_prompt=qz_focus
                        )
                        st.session_state["ai_crafted_quiz"] = qz_payload
                        st.success("AI Quiz crafted successfully!")
                    except Exception as e:
                        st.error(f"Quiz Generation Error: {e}")

            if "ai_crafted_quiz" in st.session_state:
                quiz_data = st.session_state["ai_crafted_quiz"]
                questions = quiz_data["questions"]
                
                st.markdown(f"""
                    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px; margin: 16px 0;">
                        <h3 style="margin: 0; color: #38BDF8; font-family: 'Outfit', sans-serif;">{quiz_data['title']}</h3>
                        <p style="margin: 4px 0 0 0; color: var(--nexus-text-sub); font-size: 0.9rem;">{len(questions)} Questions Ready for Testing</p>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("🚀 Export & Play Now in Quiz Engine ➔", type="primary", use_container_width=True, key="ai_export_quiz_btn"):
                    new_quiz_id = create_quiz(
                        user_id=user_id,
                        title=quiz_data["title"],
                        subject_id=quiz_data["subject_id"],
                        chapter_id=quiz_data["chapter_id"],
                        topic_id=quiz_data["topic_id"],
                        difficulty=quiz_data["difficulty"],
                        questions_json=json.dumps(questions)
                    )
                    st.session_state["active_quiz_id"] = new_quiz_id
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_results"] = None
                    st.session_state["current_page"] = "🎯 Quiz Engine"
                    st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                    st.toast("Quiz transferred to Quiz Engine!", icon="🚀")
                    st.rerun()

                for idx, q in enumerate(questions, 1):
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: #38BDF8; margin-bottom: 10px;">
                            <strong>Q{idx}. {q['question']}</strong>
                            <div style="font-size: 0.85rem; color: var(--nexus-text-sub); margin: 6px 0;">
                                Options: {', '.join(q['options'])}
                            </div>
                            <div style="font-size: 0.85rem; color: #22C55E;">
                                <strong>Answer:</strong> {q['correct_answer']}
                            </div>
                            <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-top: 4px;">
                                💡 <em>{q['explanation']}</em>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 4: SMART STUDY PLANNER
    # ══════════════════════════════════════════════════════════
    with tab_plan:
        st.subheader("🗓️ AI Smart Study Schedule Generator")
        st.caption("AI allocates your pending syllabus topics, revision milestones, and problem sets into an optimal multi-day timetable.")

        c_pl1, c_pl2 = st.columns(2)
        with c_pl1:
            plan_days = st.selectbox("Schedule Duration", [3, 7, 14], index=1, key="ai_plan_days")
        with c_pl2:
            plan_hours = st.slider("Daily Available Study Hours", min_value=1.0, max_value=8.0, value=3.5, step=0.5, key="ai_plan_hrs")

        if st.button("📅 Generate Intelligent Study Plan", type="primary", use_container_width=True, key="ai_gen_plan_btn"):
            with st.spinner(f"🧠 Nexus AI is scheduling your {plan_days}-day curriculum roadmap..."):
                try:
                    res = nexus_ai.generate_ai_study_plan(user_id, daily_hours=plan_hours, target_days=plan_days)
                    st.session_state["ai_generated_plan"] = res["plan_data"]
                    st.success("Study schedule created!")
                except Exception as e:
                    st.error(f"Plan Generation Error: {e}")

        if "ai_generated_plan" in st.session_state:
            p_data = st.session_state["ai_generated_plan"]
            st.markdown(f"""
                <div class="readiness-container" style="padding: 18px; margin: 16px 0;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase;">EXECUTIVE STRATEGY</div>
                    <p style="font-size: 1.0rem; color: var(--nexus-text-title); margin: 6px 0 0 0;">{p_data.get('strategy_summary', '')}</p>
                </div>
            """, unsafe_allow_html=True)

            if st.button("📥 Sync All Tasks to Study Planner", type="primary", use_container_width=True, key="ai_sync_planner_btn"):
                today = datetime.date.today()
                synced_count = 0
                for d_idx, day in enumerate(p_data.get("daily_plans", [])):
                    target_date_str = (today + datetime.timedelta(days=d_idx)).strftime("%Y-%m-%d")
                    for t in day.get("tasks", []):
                        add_daily_plan(
                            user_id=user_id,
                            plan_date=target_date_str,
                            description=t.get("task", "Study Task"),
                            duration_minutes=t.get("duration_minutes", 30),
                            subject_id=None
                        )
                        synced_count += 1
                st.balloons()
                st.success(f"Successfully synced {synced_count} AI-scheduled tasks directly into your Study Planner!")

            for day in p_data.get("daily_plans", []):
                st.markdown(f"""
                    <div class="priority-item-card" style="border-left-color: #F97316; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: var(--nexus-text-title); font-size: 1.05rem;">{day.get('date_label', f'Day {day.get("day_number")}')}</strong>
                            <span style="font-size: 0.8rem; font-weight: 700; color: #F97316;">⏱️ {day.get('target_focus_hours')} hrs</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #38BDF8; margin-bottom: 8px;">
                            🎯 <strong>Daily Milestone:</strong> {day.get('daily_goal')}
                        </div>
                """, unsafe_allow_html=True)
                for t in day.get("tasks", []):
                    st.markdown(f"• **{t.get('subject_name', 'General')}:** {t.get('task')} *({t.get('duration_minutes', 30)} min — {t.get('task_type', 'Study')})*")
                st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 5: DEEP PROGRESS DIAGNOSTIC
    # ══════════════════════════════════════════════════════════
    with tab_diag:
        st.subheader("📊 Deep Academic Progress Diagnostic")
        st.caption("AI-powered diagnostic of syllabus coverage velocity, bottleneck chapters, and exam preparedness projection.")

        if st.button("📈 Run Deep Progress Audit", type="primary", use_container_width=True, key="ai_run_diag_btn"):
            with st.spinner("🧠 Nexus AI is analyzing your academic data and running predictive diagnostics..."):
                try:
                    res = nexus_ai.generate_progress_diagnostic(user_id)
                    st.session_state["ai_progress_diagnostic"] = res["content"]
                except Exception as e:
                    st.error(f"Diagnostic Error: {e}")

        if "ai_progress_diagnostic" in st.session_state:
            st.markdown(f"""
                <div class="readiness-container" style="padding: 24px; margin-top: 16px;">
                    {st.session_state['ai_progress_diagnostic']}
                </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 6: SPACED REVISION STRATEGIST
    # ══════════════════════════════════════════════════════════
    with tab_rev:
        st.subheader("🔄 Spaced Revision Retention Strategist")
        st.caption("AI optimizes your spaced repetition queue using forgetting curve intervals and cognitive priority weights.")

        if st.button("🧠 Generate Revision Advisory", type="primary", use_container_width=True, key="ai_gen_rev_btn"):
            with st.spinner("🧠 Nexus AI is calculating optimal retention intervals..."):
                try:
                    res = nexus_ai.generate_revision_recommendations(user_id)
                    st.session_state["ai_revision_advisory"] = res["content"]
                except Exception as e:
                    st.error(f"Revision Advisory Error: {e}")

        if "ai_revision_advisory" in st.session_state:
            st.markdown(f"""
                <div class="readiness-container" style="padding: 24px; margin-top: 16px;">
                    {st.session_state['ai_revision_advisory']}
                </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 7: MISTAKE VAULT ROOT-CAUSE DIAGNOSTIC
    # ══════════════════════════════════════════════════════════
    with tab_mistakes:
        st.subheader("❌ Mistake Vault Root-Cause Diagnostic")
        st.caption("AI analyzes your recorded quiz errors and common misconceptions to build your customized anti-mistake checklist.")

        if st.button("🔍 Diagnose Cognitive Error Traps", type="primary", use_container_width=True, key="ai_diag_mistakes_btn"):
            with st.spinner("🧠 Nexus AI is diagnosing error root causes across your Mistake Vault..."):
                try:
                    res = nexus_ai.generate_mistake_root_cause_analysis(user_id)
                    st.session_state["ai_mistake_diagnosis"] = res["content"]
                except Exception as e:
                    st.error(f"Mistake Diagnostic Error: {e}")

        if "ai_mistake_diagnosis" in st.session_state:
            st.markdown(f"""
                <div class="readiness-container" style="padding: 24px; margin-top: 16px;">
                    {st.session_state['ai_mistake_diagnosis']}
                </div>
            """, unsafe_allow_html=True)
