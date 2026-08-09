"""
notes.py — Nexus Notes System with Markdown rendering and Syllabus linking.
"""

import streamlit as st
from models import (
    add_note,
    get_all_notes,
    delete_note,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter
)

def render_notes_page(user_id: int):
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38BDF8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>📝</span> <span>SYLLABUS-LINKED KNOWLEDGE</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Nexus Notes
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Rich, structured study summaries directly tied to your chapters and topics for effortless recall.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_notes, tab_create = st.tabs(["📚 My Notes Repository", "➕ Write New Note"])

    with tab_create:
        st.subheader("Create Syllabus Note")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_s_name = st.selectbox("Subject", list(s_map.keys()), key="note_add_s")
            sel_s_id = s_map[sel_s_name]
            
            chapters = get_chapters_for_subject(user_id, sel_s_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with c2:
                sel_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="note_add_c")
            sel_c_id = c_map.get(sel_c_name)
            
            topics = get_topics_for_chapter(user_id, sel_c_id) if sel_c_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            with c3:
                sel_t_name = st.selectbox("Topic", list(t_map.keys()) if t_map else ["None"], key="note_add_t")
            sel_t_id = t_map.get(sel_t_name)

            with st.form("create_note_form", clear_on_submit=True):
                title = st.text_input("Note Title", placeholder="e.g. Key Theorems, Summary of French Revolution, Cell Organelles")
                tags = st.text_input("Tags (comma separated)", placeholder="e.g. formula, high_weightage, quick_revision")
                content = st.text_area("Note Content (Supports Markdown)", height=220, placeholder="Write your notes here with **bold text**, bullet points, definitions...")
                is_pinned = st.checkbox("📌 Pin note to top", value=False)
                
                submitted = st.form_submit_button("⚡ Save Note (+25 XP)", type="primary", use_container_width=True)
                if submitted:
                    if not title or not content or not sel_t_id:
                        st.error("Please provide Title, Content, and select a Topic.")
                    else:
                        add_note(user_id, sel_s_id, sel_c_id, sel_t_id, title, content, tags, 1 if is_pinned else 0)
                        st.success(f"Note '{title}' saved successfully! +25 XP")
                        st.rerun()

    with tab_notes:
        subjects = get_all_subjects(user_id)
        s_filt = {"All Subjects": None}
        if subjects:
            s_filt.update({s["name"]: s["id"] for s in subjects})
            
        c_f1, c_f2 = st.columns([1, 2])
        with c_f1:
            sel_f_s = st.selectbox("Filter Subject", list(s_filt.keys()), key="notes_filt_subj")
        with c_f2:
            search_q = st.text_input("🔍 Search Notes", placeholder="Search title, content, or tag...", key="notes_search_q")
            
        notes = get_all_notes(user_id, subject_id=s_filt[sel_f_s])
        if search_q:
            q = search_q.lower()
            notes = [n for n in notes if q in n["title"].lower() or q in n["content"].lower() or q in n.get("tags", "").lower()]

        if not notes:
            st.info("No notes found. Create your first syllabus note to build your personal knowledge base!")
        else:
            for n in notes:
                with st.container():
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {n.get('subject_color', '#38BDF8')};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-size: 0.75rem; font-weight: 700; color: {n.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 12px;">
                                        {n.get('subject_name')}
                                    </span>
                                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">{n.get('chapter_name')} → {n.get('topic_name')}</span>
                                </div>
                                <span style="font-size: 0.85rem; color: #F97316;">{'📌 Pinned' if n.get('is_pinned') else ''}</span>
                            </div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: var(--nexus-text-title); margin-bottom: 8px;">
                                {n['title']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(n["content"])
                    
                    if n.get("tags"):
                        tags_list = [t.strip() for t in n["tags"].split(",") if t.strip()]
                        tags_html = " ".join([f"<span class='auth-feature-pill' style='font-size: 0.7rem; padding: 2px 8px;'>#{t}</span>" for t in tags_list])
                        st.markdown(f"<div style='margin: 6px 0;'>{tags_html}</div>", unsafe_allow_html=True)
                        
                    c_del1, c_del2 = st.columns([6, 1])
                    with c_del2:
                        if st.button("🗑️ Delete", key=f"del_note_{n['id']}", use_container_width=True):
                            delete_note(user_id, n['id'])
                            st.toast("Note deleted", icon="🗑️")
                            st.rerun()
                    st.markdown("<hr style='margin: 12px 0; opacity: 0.15;'/>", unsafe_allow_html=True)
