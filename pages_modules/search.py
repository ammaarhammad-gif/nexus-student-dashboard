"""
search.py — Global Nexus Search Portal (Phase 2).
"""

import streamlit as st
from models import global_nexus_search
from styles import render_top_header_bar, render_section_header, render_breadcrumbs, render_empty_state

def render_search_page(user_id: int):
    render_top_header_bar(
        user_id,
        "🔍 Search",
        "Omnipresent search across topics, notes, formulas, mistakes, and exams.",
        ["NEXUS", "Search"]
    )


    query = st.text_input(
        "Search Query",
        placeholder="Type a topic, formula, chapter, mistake, or exam (e.g. 'Newton', 'Trigonometry', 'Optics')...",
        key="full_search_input",
        label_visibility="collapsed"
    )

    if not query or len(query.strip()) < 2:
        render_empty_state(
            icon="🔎",
            title="Search Your Entire Study OS",
            message="Enter at least 2 characters to search across all syllabus items, personal study notes, error vault questions, and exam dates."
        )
        return

    results = global_nexus_search(user_id, query)
    total_hits = sum(len(v) for v in results.values())

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0 18px 0;">
            <span style="font-size: 0.95rem; font-weight: 700; color: #38BDF8;">
                Found {total_hits} match{'es' if total_hits != 1 else ''} for "<span style="color: var(--nexus-text-title);">{query}</span>"
            </span>
        </div>
    """, unsafe_allow_html=True)

    if total_hits == 0:
        render_empty_state(
            icon="📭",
            title="No Results Found",
            message=f"No syllabus topics, notes, or tasks matched '{query}'. Check your spelling or search by general subject keywords."
        )
        return

    tab_all, tab_top, tab_chap, tab_notes, tab_mist, tab_exams, tab_tasks = st.tabs([
        f"🌟 All ({total_hits})",
        f"📚 Topics ({len(results.get('topics', []))})",
        f"📖 Chapters ({len(results.get('chapters', []))})",
        f"📝 Notes ({len(results.get('notes', []))})",
        f"❌ Mistakes ({len(results.get('mistakes', []))})",
        f"⏰ Exams ({len(results.get('exams', []))})",
        f"🗓️ Tasks ({len(results.get('tasks', []))})"
    ])

    def render_topics(topics):
        if not topics:
            st.caption("No topic matches.")
            return
        for t in topics:
            st.markdown(f"""
                <div class="search-hit-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="nexus-pill-revision">Topic</span>
                            <span style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; margin-left: 6px;">{t['subject_name']}</span>
                            <span style="font-size: 0.78rem; color: var(--nexus-text-sub);">› {t['chapter_name']}</span>
                            <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                                {t['topic_name']}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">Status: <strong>{t.get('status', 'Not Started')}</strong></span><br/>
                            <span style="font-size: 0.8rem; color: #EAB308;">★ {t.get('understanding', 3)}/5</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def render_chapters(chapters):
        if not chapters:
            st.caption("No chapter matches.")
            return
        for c in chapters:
            st.markdown(f"""
                <div class="search-hit-box">
                    <span class="nexus-pill-high">Chapter</span>
                    <span style="font-size: 0.8rem; font-weight: 700; color: #F97316; margin-left: 6px;">{c['subject_name']}</span>
                    <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                        {c['chapter_name']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def render_notes(notes):
        if not notes:
            st.caption("No note matches.")
            return
        for n in notes:
            st.markdown(f"""
                <div class="search-hit-box">
                    <span class="nexus-pill-low">Note</span>
                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-left: 6px;">{n.get('subject_name', '')} › {n.get('topic_name', '')}</span>
                    <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                        {n['title']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def render_mistakes(mistakes):
        if not mistakes:
            st.caption("No mistake matches.")
            return
        for m in mistakes:
            st.markdown(f"""
                <div class="search-hit-box" style="border-left: 4px solid #EF4444;">
                    <span class="nexus-pill-critical">{m.get('mistake_type', 'Mistake')}</span>
                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-left: 6px;">{m.get('subject_name', '')}</span>
                    <div style="font-size: 1.0rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                        ❓ {m['question']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def render_exams(exams):
        if not exams:
            st.caption("No exam matches.")
            return
        for e in exams:
            st.markdown(f"""
                <div class="search-hit-box" style="border-left: 4px solid #EC4899;">
                    <span class="nexus-pill-high">Exam Term</span>
                    <div style="font-size: 1.05rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                        ⏰ {e['exam_name']} — <span style="color: #38BDF8;">{e.get('exam_date')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def render_tasks(tasks):
        if not tasks:
            st.caption("No study task matches.")
            return
        for tk in tasks:
            st.markdown(f"""
                <div class="search-hit-box">
                    <span class="nexus-pill-medium">Task</span>
                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-left: 6px;">Date: {tk.get('plan_date')}</span>
                    <div style="font-size: 1.0rem; font-weight: 700; color: var(--nexus-text-title); margin-top: 4px;">
                        {'✅' if tk.get('is_completed') else '🗓️'} {tk['description']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab_all:
        if results.get("topics"):
            st.markdown("#### 📚 Syllabus Topics")
            render_topics(results["topics"])
        if results.get("chapters"):
            st.markdown("#### 📖 Chapters")
            render_chapters(results["chapters"])
        if results.get("notes"):
            st.markdown("#### 📝 Study Notes")
            render_notes(results["notes"])
        if results.get("mistakes"):
            st.markdown("#### ❌ Mistake Vault")
            render_mistakes(results["mistakes"])
        if results.get("exams"):
            st.markdown("#### ⏰ Exams")
            render_exams(results["exams"])
        if results.get("tasks"):
            st.markdown("#### 🗓️ Daily Tasks")
            render_tasks(results["tasks"])

    with tab_top:
        render_topics(results.get("topics", []))

    with tab_chap:
        render_chapters(results.get("chapters", []))

    with tab_notes:
        render_notes(results.get("notes", []))

    with tab_mist:
        render_mistakes(results.get("mistakes", []))

    with tab_exams:
        render_exams(results.get("exams", []))

    with tab_tasks:
        render_tasks(results.get("tasks", []))
