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
    get_topics_for_chapter
)

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
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); color: #EF4444; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>❌</span> <span>ERROR PATTERN MASTERY</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Mistake Vault
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Analyze your past exam and practice mistakes to eliminate recurring errors and build exam-day perfection.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    analytics = get_mistake_analytics(user_id)
    total_mistakes = analytics.get("total", 0)
    breakdown = analytics.get("breakdown", [])

    # Overview Analytics Bar
    c_m1, c_m2 = st.columns([1, 2])
    with c_m1:
        st.markdown(f"""
            <div class="readiness-container" style="text-align: center; height: 100%;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #EF4444; text-transform: uppercase; letter-spacing: 0.05em;">
                    Total Mistakes Logged
                </div>
                <div class="readiness-score-big" style="margin: 10px 0; background: linear-gradient(135deg, #EF4444, #F97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {total_mistakes}
                </div>
                <div style="font-size: 0.8rem; color: var(--nexus-text-sub);">
                    Turn your errors into lifelong strengths
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_m2:
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
                height=160,
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

    st.markdown("---")

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

            with st.form("add_mistake_form", clear_on_submit=True):
                question_txt = st.text_area("Question / Problem Prompt", placeholder="e.g. Find the focal length of a concave lens if power is -2.0 D...")
                
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    your_ans = st.text_input("Your Answer / Error Made", placeholder="e.g. +50 cm")
                with c_a2:
                    corr_ans = st.text_input("Correct Answer", placeholder="e.g. -50 cm or -0.5 m")
                
                c_t1, c_t2 = st.columns(2)
                with c_t1:
                    m_type = st.selectbox("Mistake Root Cause", MISTAKE_TYPES)
                with c_t2:
                    prev_strat = st.text_input("Prevention Strategy", placeholder="e.g. Always check sign convention: focal length of concave is negative")
                    
                expl = st.text_area("Detailed Concept Explanation", placeholder="Power P = 1/f(in meters) -> f = 1/(-2) = -0.5 m = -50 cm.")
                
                submit_btn = st.form_submit_button("⚡ Save to Mistake Vault (+20 XP)", use_container_width=True, type="primary")
                if submit_btn:
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
                        st.rerun()

    with tab_list:
        subjects = get_all_subjects(user_id)
        s_filter_map = {"All Subjects": None}
        if subjects:
            s_filter_map.update({s["name"]: s["id"] for s in subjects})
            
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            filt_subj = st.selectbox("Filter Subject", list(s_filter_map.keys()), key="mst_filt_subj")
        with c_f2:
            filt_type = st.selectbox("Filter Mistake Type", ["All"] + MISTAKE_TYPES, key="mst_filt_type")
            
        mistakes = get_all_mistakes(user_id, subject_id=s_filter_map[filt_subj], mistake_type=filt_type)
        if not mistakes:
            st.info("No recorded mistakes matching the selected filter.")
        else:
            for m in mistakes:
                with st.container():
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: #EF4444;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 6px; align-items: center;">
                                    <span class="nexus-pill-critical">{m.get('mistake_type', 'Conceptual')}</span>
                                    <span style="font-size: 0.8rem; font-weight: 700; color: {m.get('subject_color', '#38BDF8')};">{m.get('subject_name', '')}</span>
                                    <span style="font-size: 0.75rem; color: var(--nexus-text-sub);">{m.get('chapter_name', '')}</span>
                                </div>
                                <span style="font-size: 0.75rem; color: var(--nexus-text-sub);">{str(m.get('created_at', ''))[:10]}</span>
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
                    
                    c_b1, c_b2 = st.columns([6, 1])
                    with c_b2:
                        if st.button("🗑️ Delete", key=f"del_mst_{m['id']}", use_container_width=True):
                            delete_mistake(user_id, m['id'])
                            st.toast("Deleted from Vault", icon="🗑️")
                            st.rerun()

    with tab_review:
        st.subheader("🎯 Rapid Flashcard Mistake Review")
        mistakes = get_all_mistakes(user_id)
        if not mistakes:
            st.info("Log some mistakes first to start your review session.")
        else:
            if "mst_review_idx" not in st.session_state:
                st.session_state["mst_review_idx"] = 0
            
            idx = st.session_state["mst_review_idx"] % len(mistakes)
            cur = mistakes[idx]
            
            st.markdown(f"""
                <div class="readiness-container" style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #38BDF8; font-weight: 700; text-transform: uppercase;">
                        Reviewing Mistake {idx + 1} of {len(mistakes)} • {cur.get('subject_name')}
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
                
            c_p, c_n = st.columns(2)
            with c_p:
                if st.button("⬅️ Previous Question", use_container_width=True):
                    st.session_state["mst_review_idx"] = (idx - 1) % len(mistakes)
                    st.rerun()
            with c_n:
                if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                    st.session_state["mst_review_idx"] = (idx + 1) % len(mistakes)
                    st.rerun()
