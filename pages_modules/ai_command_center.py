"""
ai_command_center.py — Nexus AI Autonomous Academic Workspace & Intelligent Copilot.

Features:
1. Unified Conversational Intelligence Interface (Tutor, Mentor, Planner, Diagnostic, Controller)
2. Interactive Follow-up Action Chips (1-click deep derivations, quizzes, revisions, notes)
3. Live Workspace Action Badges (Shows executed database & navigation actions)
4. Context & Status Pill (Online engine status, Class & Board context)
5. Guarded Destructive Action Confirmations
"""

import streamlit as st
from ai_service import nexus_ai, NexusConversationSession, NexusContextBuilder
from styles import render_top_header_bar, render_html


def render_ai_command_center_page(user_id: int):
    context = NexusContextBuilder.assemble_full_context(user_id)
    profile = context["profile"]
    status_info = nexus_ai.get_status()

    render_top_header_bar(
        user_id,
        "🤖 Nexus AI",
        "Your intelligent academic copilot & command center.",
        ["NEXUS", "Nexus AI"]
    )

    # ══════════════════════════════════════════════════════════
    # STATUS & CONTEXT BAR
    # ══════════════════════════════════════════════════════════
    c_st1, c_st2, c_st3 = st.columns([2, 1.5, 1])
    with c_st1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; padding: 4px 0;">
                <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 8px #22C55E;"></span>
                <span style="font-size: 0.85rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.04em;">NEXUS COGNITIVE ENGINE ACTIVE</span>
                <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">• {status_info['engine_mode']}</span>
            </div>
        """, unsafe_allow_html=True)
    with c_st2:
        st.markdown(f"""
            <div style="text-align: center; padding: 4px 0;">
                <span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; font-size: 0.8rem; font-weight: 700; padding: 3px 12px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.25);">
                    🎓 {profile.get('class_name', 'Class 10')} • {profile.get('board', 'CBSE')}
                </span>
            </div>
        """, unsafe_allow_html=True)
    with c_st3:
        if st.button("🗑️ Clear Chat", key="ai_clear_chat_btn", use_container_width=True):
            NexusConversationSession.clear_history()
            st.rerun()

    st.markdown("<hr style='margin: 10px 0 16px 0; opacity: 0.15;'/>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # QUICK ACTION SHORTCUT CHIPS
    # ══════════════════════════════════════════════════════════
    st.caption("⚡ Quick Academic Actions:")
    qa1, qa2, qa3, qa4, qa5, qa6 = st.columns(6)
    
    with qa1:
        if st.button("💡 Explain Concept", use_container_width=True, key="qa_exp"):
            st.session_state["queued_ai_prompt"] = "Explain Newton's Third Law from first principles"
            st.rerun()
    with qa2:
        if st.button("🎯 Quiz Me", use_container_width=True, key="qa_quiz"):
            st.session_state["queued_ai_prompt"] = "Quiz me on my current topics"
            st.rerun()
    with qa3:
        if st.button("🗓️ Plan My Day", use_container_width=True, key="qa_plan"):
            st.session_state["queued_ai_prompt"] = "Plan my study schedule for today"
            st.rerun()
    with qa4:
        if st.button("📊 Progress Audit", use_container_width=True, key="qa_diag"):
            st.session_state["queued_ai_prompt"] = "How am I progressing towards my exams?"
            st.rerun()
    with qa5:
        if st.button("❌ Review Mistakes", use_container_width=True, key="qa_mist"):
            st.session_state["queued_ai_prompt"] = "Show me everything I got wrong in practice"
            st.rerun()
    with qa6:
        if st.button("⏱️ Start Focus", use_container_width=True, key="qa_foc"):
            st.session_state["queued_ai_prompt"] = "Start a 25 minute focus session"
            st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # MESSAGE STREAM & CHAT HISTORY
    # ══════════════════════════════════════════════════════════
    history = NexusConversationSession.get_history()

    if not history:
        # Welcoming Empty State Guide
        st.markdown(f"""
            <div class="readiness-container" style="padding: 32px 24px; text-align: center; margin: 18px 0; border: 1px dashed rgba(56, 189, 248, 0.35);">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🤖</div>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--nexus-text-title); margin: 0 0 6px 0;">
                    Nexus Academic Intelligence Copilot
                </h2>
                <p style="color: var(--nexus-text-sub); font-size: 0.95rem; max-width: 600px; margin: 0 auto 20px auto; line-height: 1.5;">
                    I teach concepts conversationally from first principles, generate high-rigor board exam quizzes, schedule study sprints, and control your Nexus workspace through natural language.
                </p>
                <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
                    TRY ASKING:
                </div>
            </div>
        """, unsafe_allow_html=True)

        e_col1, e_col2, e_col3 = st.columns(3)
        with e_col1:
            if st.button("🗣️ \"Teach me Newton's Third Law simply\"", use_container_width=True, key="emp_p1"):
                st.session_state["queued_ai_prompt"] = "Explain Newton's Third Law simply"
                st.rerun()
            if st.button("📐 \"Explain it mathematically\"", use_container_width=True, key="emp_p2"):
                st.session_state["queued_ai_prompt"] = "Explain Newton's Third Law mathematically with derivations"
                st.rerun()
        with e_col2:
            if st.button("🗓️ \"Schedule 45 min Physics tomorrow\"", use_container_width=True, key="emp_p3"):
                st.session_state["queued_ai_prompt"] = "Schedule 45 minutes of Physics tomorrow"
                st.rerun()
            if st.button("🎯 \"Quiz me on Chemical Bonding\"", use_container_width=True, key="emp_p4"):
                st.session_state["queued_ai_prompt"] = "Quiz me on Chemical Bonding"
                st.rerun()
        with e_col3:
            if st.button("🧠 \"Teach me using questions (Socratic)\"", use_container_width=True, key="emp_p5"):
                st.session_state["queued_ai_prompt"] = "Teach me Newton's Third Law using questions"
                st.rerun()
            if st.button("📊 \"How am I progressing?\"", use_container_width=True, key="emp_p6"):
                st.session_state["queued_ai_prompt"] = "How am I progressing towards my exams?"
                st.rerun()
    else:
        # Render Chat Thread
        for idx, msg in enumerate(history):
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"**{msg['content']}**")
                    if msg.get("timestamp"):
                        st.caption(f"Sent at {msg['timestamp']}")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    if msg.get("action_badge"):
                        st.markdown(
                            f'<div style="margin-bottom: 10px;"><span style="background: rgba(34, 197, 94, 0.18); color: #22C55E; font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.35); display: inline-flex; align-items: center; gap: 6px;">{msg["action_badge"]}</span></div>',
                            unsafe_allow_html=True
                        )

                    # Render Markdown/LaTeX content cleanly in Streamlit container
                    st.markdown(msg["content"])

                    # Render Interactive Follow-up Action Chips
                    if msg.get("follow_ups"):
                        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                        f_cols = st.columns(len(msg["follow_ups"]))
                        for f_idx, chip_text in enumerate(msg["follow_ups"]):
                            with f_cols[f_idx]:
                                if st.button(f"👉 {chip_text}", key=f"chip_{idx}_{f_idx}", use_container_width=True):
                                    st.session_state["queued_ai_prompt"] = chip_text
                                    st.rerun()

    # ══════════════════════════════════════════════════════════
    # CHAT INPUT BAR & PROMPT DISPATCHER
    # ══════════════════════════════════════════════════════════
    # Check queued prompt from quick chips
    queued_prompt = st.session_state.pop("queued_ai_prompt", None)
    
    # Native Streamlit Chat Input (or fallback triggered via quick chip)
    chat_prompt = st.chat_input("Ask Nexus anything about your studies, or give an action command...")
    prompt_to_process = chat_prompt or queued_prompt

    if prompt_to_process and prompt_to_process.strip():
        user_query = prompt_to_process.strip()
        NexusConversationSession.add_message("user", user_query)

        with st.spinner("Nexus is thinking & orchestrating academic workspace..."):
            try:
                ai_response = nexus_ai.process_chat_message(user_id, user_query)
                NexusConversationSession.add_message(
                    role="nexus",
                    content=ai_response.get("content", "I am ready to help with your academic goals."),
                    action_badge=ai_response.get("action_badge"),
                    follow_ups=ai_response.get("follow_ups", [])
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).exception(f"Error in ai_command_center: {e}")
                NexusConversationSession.add_message(
                    role="nexus",
                    content="I encountered a momentary issue while processing that request. Please rephrase or ask about a specific study topic!",
                    action_badge="⚠️ Copilot Notice"
                )

        st.rerun()
