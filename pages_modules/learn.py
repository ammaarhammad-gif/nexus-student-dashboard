"""
learn.py — Nexus Unified Learn Module (Hub, Subject Workspace, Chapter Tree & Topic Detail).

Consolidates:
1. 📚 Syllabus (Hub, Subject Workspaces, Chapter & Topic Detail Workspaces)
2. 📝 Notes Repository (2-Column Note Index & Markdown/LaTeX Editor with Pin)
3. 📐 Formulas Vault (KaTeX Reference Library, Search, Favorites, Anki Export)

Primary User Question Answered: "What do I need to understand?"
"""

import streamlit as st
import csv
import io
from models import (
    get_all_subjects, add_subject, rename_subject, delete_subject,
    add_chapter, rename_chapter, delete_chapter, move_chapter,
    add_topic, rename_topic, delete_topic,
    add_subtopic, delete_subtopic,
    save_progress, get_user_profile,
    import_syllabus_from_csv, schedule_revisions, get_user_theme,
    get_subject_hierarchy, get_chapters_for_subject, get_topics_for_chapter,
    add_note, get_all_notes, delete_note,
    add_formula, get_all_formulas, toggle_formula_favorite, delete_formula,
    get_weak_areas
)
from preloaded_syllabi import preload_standard_syllabus, reload_and_replace_syllabus
from styles import render_top_header_bar, render_empty_state, render_html
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_formulas_to_anki
from ui_optimistic import (
    get_optimistic_topic_status, set_optimistic_topic_status,
    render_animated_progress_bar, render_floating_xp_toast
)


STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "Revision Done"]
STATUS_BADGE_CLASSES = {
    "Not Started": "badge-not-started",
    "In Progress": "badge-in-progress",
    "Completed": "badge-completed",
    "Revision Done": "badge-revision-done"
}
UNDERSTANDING_LABELS = {
    1: "🔴 1 - Needs Help",
    2: "🟠 2 - Basic",
    3: "🟡 3 - Moderate",
    4: "🟢 4 - Good",
    5: "🌟 5 - Mastered"
}


def render_learn_page(user_id: int):
    profile = get_user_profile(user_id) or {}
    board = profile.get("board", "CBSE")
    class_name = profile.get("class_name", "Class 10")

    render_top_header_bar(
        user_id,
        "📚 Learn",
        "Build understanding, not just completion.",
        ["NEXUS", "Learn"]
    )

    tab_syllabus, tab_notes, tab_formulas = st.tabs([
        "📚 Syllabus",
        "📝 Notes",
        "📐 Formulas"
    ])

    with tab_syllabus:
        _render_syllabus_hub_and_workspace(user_id, board, class_name)

    with tab_notes:
        _render_notes_workspace(user_id)

    with tab_formulas:
        _render_formulas_vault(user_id)


# ══════════════════════════════════════════════════════════════════════════
# 1. SYLLABUS HUB & WORKSPACES
# ══════════════════════════════════════════════════════════════════════════

def _render_syllabus_hub_and_workspace(user_id: int, board: str, class_name: str):
    subjects = get_all_subjects(user_id)

    if not subjects:
        with st.spinner(f"⚡ Loading official {board} ({class_name}) syllabus for you..."):
            loaded = preload_standard_syllabus(user_id, board, class_name)
            if loaded:
                st.toast(f"✅ Official {board} ({class_name}) syllabus loaded!", icon="🚀")
                st.rerun()

    # Active Subject Selection
    selected_subject_id = st.session_state.get("learn_selected_subject_id")
    if not selected_subject_id and subjects:
        selected_subject_id = subjects[0]["id"]
        st.session_state["learn_selected_subject_id"] = selected_subject_id

    # Top Control Bar
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2.5, 1.2, 1.3])
    with col_ctrl1:
        s_names = [s["name"] for s in subjects]
        s_ids = [s["id"] for s in subjects]
        cur_idx = s_ids.index(selected_subject_id) if selected_subject_id in s_ids else 0
        
        sel_name = st.selectbox(
            "Subject Workspace",
            s_names,
            index=cur_idx,
            key="learn_subj_top_sel",
            label_visibility="collapsed"
        )
        if sel_name:
            st.session_state["learn_selected_subject_id"] = s_ids[s_names.index(sel_name)]
            selected_subject_id = s_ids[s_names.index(sel_name)]

    with col_ctrl2:
        with st.popover("⚙️ Syllabus Config"):
            st.markdown("**➕ Add Subject**")
            with st.form("learn_add_sub_modal", clear_on_submit=True):
                new_sub_name = st.text_input("Subject Name", placeholder="e.g. Economics, CS")
                sub_color = st.color_picker("Color", value="#38BDF8")
                if st.form_submit_button("Create Subject", use_container_width=True):
                    if new_sub_name.strip():
                        add_subject(user_id, new_sub_name.strip(), sub_color)
                        st.rerun()

            st.markdown("---")
            if st.button(f"🔄 Reload Full {board} Syllabus", use_container_width=True, key="learn_reload_syl_modal"):
                with st.spinner("Reloading official curriculum..."):
                    reload_and_replace_syllabus(user_id, board, class_name)
                st.rerun()

    with col_ctrl3:
        with st.popover("📥 Import CSV"):
            _render_csv_import_tool(user_id)

    # ── Subject Hub Cards Strip ──
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    active_subject = next((s for s in subjects if s["id"] == selected_subject_id), subjects[0] if subjects else None)
    if not active_subject:
        return

    # Fetch hierarchy for active subject
    chapters = get_subject_hierarchy(user_id, active_subject["id"])
    total_topics = sum(len(ch["topics"]) for ch in chapters)
    completed_topics = sum(1 for ch in chapters for t in ch["topics"] if t["status"] in ["Completed", "Revision Done"])
    subject_pct = round((completed_topics / total_topics * 100)) if total_topics > 0 else 0

    # Render Subject Workspace Header Card
    render_html(f"""
        <div class="nexus-card" style="border-top: 4px solid {active_subject.get('color', '#38BDF8')}; margin-bottom: 16px; padding: 18px 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0 0 2px 0; font-size: 1.55rem; color: var(--nexus-text-title); font-family: 'Outfit', sans-serif;">
                        {active_subject['name']}
                    </h2>
                    <span style="font-size: 0.85rem; color: var(--nexus-text-sub);">
                        {len(chapters)} Chapters • {total_topics} Topics • {completed_topics} Completed
                    </span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.7rem; font-weight: 800; color: {active_subject.get('color', '#38BDF8')};">
                        {subject_pct}%
                    </span>
                </div>
            </div>
        </div>
    """)
    render_animated_progress_bar(subject_pct, color=active_subject.get('color', '#38BDF8'), height_px=7)

    # Check if a specific topic is selected for Detail View
    selected_topic_id = st.session_state.get("learn_detail_topic_id")
    selected_topic_data = None
    selected_topic_chap = None

    if selected_topic_id:
        for ch in chapters:
            for top in ch["topics"]:
                if top["id"] == selected_topic_id:
                    selected_topic_data = top
                    selected_topic_chap = ch
                    break

    if selected_topic_data:
        _render_topic_detail_workspace(user_id, active_subject, selected_topic_chap, selected_topic_data)
        return

    # ── Subject Screen Tabs: Chapters, Overview, Performance ──
    tab_chaps, tab_ovw, tab_perf = st.tabs([
        "📖 Chapters & Topics",
        "📊 Subject Overview",
        "🎯 Pacing & Weak Areas"
    ])

    with tab_chaps:
        # Add Chapter popover
        with st.expander(f"➕ Add New Chapter to {active_subject['name']}", expanded=False):
            with st.form(f"add_chap_form_{active_subject['id']}", clear_on_submit=True):
                new_c_name = st.text_input("Chapter Name", placeholder="e.g. Chapter 5: Electricity & Magnetism")
                if st.form_submit_button("Create Chapter", use_container_width=True):
                    if new_c_name.strip():
                        add_chapter(user_id, active_subject["id"], new_c_name.strip())
                        st.rerun()

        for c_idx, chap in enumerate(chapters):
            ch_topics = chap["topics"]
            ch_done = sum(1 for t in ch_topics if t["status"] in ["Completed", "Revision Done"])
            ch_total = len(ch_topics)
            ch_pct = round((ch_done / ch_total * 100)) if ch_total > 0 else 0
            is_ch_complete = (ch_done == ch_total and ch_total > 0)

            with st.expander(f"{'✅' if is_ch_complete else '📖'} {chap['name']} ({ch_done}/{ch_total} • {ch_pct}%)", expanded=(c_idx == 0)):
                col_ch_act1, col_ch_act2 = st.columns([4, 1])
                with col_ch_act2:
                    with st.popover("⚙️ Manage"):
                        ren_c = st.text_input("Rename", value=chap["name"], key=f"ren_c_inp_{chap['id']}")
                        if st.button("Save", key=f"save_c_btn_{chap['id']}"):
                            if ren_c.strip():
                                rename_chapter(user_id, chap["id"], ren_c.strip())
                                st.rerun()
                        if st.button("🗑️ Delete Chapter", key=f"del_c_btn_{chap['id']}", type="primary"):
                            delete_chapter(user_id, chap["id"])
                            st.rerun()

                # Add topic inline form
                with st.form(f"inline_add_top_{chap['id']}", clear_on_submit=True):
                    c_ti1, c_ti2 = st.columns([4, 1])
                    with c_ti1:
                        in_t_name = st.text_input("New Topic", placeholder="e.g. Refraction through Prism", label_visibility="collapsed", key=f"in_t_name_{chap['id']}")
                    with c_ti2:
                        if st.form_submit_button("➕ Add Topic", use_container_width=True) and in_t_name.strip():
                            add_topic(user_id, chap["id"], in_t_name.strip())
                            st.rerun()

                if not ch_topics:
                    st.caption("No topics in this chapter yet.")
                else:
                    for top in ch_topics:
                        _render_compact_topic_row(user_id, active_subject, chap, top)

    with tab_ovw:
        st.markdown(f"### 📋 Overview: {active_subject['name']}")
        c_ov1, c_ov2 = st.columns(2)
        with c_ov1:
            st.metric("Total Topics", total_topics)
            st.metric("Completed", f"{completed_topics} ({subject_pct}%)")
        with c_ov2:
            st.metric("Total Chapters", len(chapters))
            st.metric("Mastery Level", f"{round(subject_pct * 0.9, 1)}%")

    with tab_perf:
        st.markdown(f"### 🎯 Weak Areas & Review Pacing for {active_subject['name']}")
        sub_weak = [t for ch in chapters for t in ch["topics"] if t.get("understanding", 3) < 3]
        if not sub_weak:
            st.success("🎉 No low-confidence topics in this subject! All topics rated 3 stars or above.")
        else:
            for w in sub_weak:
                render_html(f"""
                    <div style="padding: 10px 14px; margin-bottom: 6px; background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; border-radius: 8px;">
                        <strong style="color: var(--nexus-text-title);">{w['name']}</strong>
                        <div style="font-size: 0.78rem; color: var(--nexus-text-sub);">Understanding: {w.get('understanding', 2)}/5 • Needs practice</div>
                    </div>
                """)


@st.fragment
def _render_compact_topic_row(user_id: int, subject: dict, chapter: dict, topic: dict):
    """
    Renders an ultra-clean, high-performance topic row with instant checkbox,
    confidence stars, and an overflow '...' menu instead of 5 cluttered buttons.
    """
    curr_status = get_optimistic_topic_status(topic["id"], topic.get("status", "Not Started"))
    is_completed = (curr_status in ["Completed", "Revision Done"])

    col_chk, col_title, col_stars, col_menu = st.columns([0.6, 4.2, 1.4, 0.8])

    with col_chk:
        checked = st.checkbox(
            label="✓",
            value=is_completed,
            key=f"lrn_chk_{topic['id']}",
            label_visibility="collapsed"
        )

    with col_title:
        # Clicking the topic name opens its full Topic Workspace
        if st.button(f"{topic['name']}", key=f"lrn_top_open_{topic['id']}", help="Open Topic Workspace"):
            st.session_state["learn_detail_topic_id"] = topic["id"]
            st.rerun()

    with col_stars:
        und = topic.get("understanding", 3)
        stars = "★" * und + "☆" * (5 - und)
        st.markdown(f"<span style='color: #F59E0B; font-size: 0.85rem;'>{stars}</span>", unsafe_allow_html=True)

    with col_menu:
        with st.popover("···"):
            st.markdown(f"**Actions for: {topic['name']}**")
            if st.button("📖 Open Topic Workspace", key=f"pop_ws_{topic['id']}", use_container_width=True):
                st.session_state["learn_detail_topic_id"] = topic["id"]
                st.rerun()
            if st.button("📝 Link to Note", key=f"pop_note_{topic['id']}", use_container_width=True):
                st.session_state["note_prefill_subj"] = subject["id"]
                st.session_state["note_prefill_chap"] = chapter["id"]
                st.session_state["note_prefill_top"] = topic["id"]
                st.toast(f"Linked to Notes for '{topic['name']}'!", icon="✨")
            if st.button("💡 Active Recall", key=f"pop_rec_{topic['id']}", use_container_width=True):
                st.session_state["practice_active_tab"] = "💡 Active Recall"
                st.session_state["active_recall_target_topic_id"] = topic["id"]
                st.session_state["current_page"] = "🎯 Practice"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()
            if st.button("⏱️ Start Focus", key=f"pop_foc_{topic['id']}", use_container_width=True):
                st.session_state["focus_target_subject_id"] = subject["id"]
                st.session_state["focus_target_chapter_id"] = chapter["id"]
                st.session_state["focus_target_topic_id"] = topic["id"]
                st.session_state["current_page"] = "⏱️ Focus"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()
            st.markdown("---")
            if st.button("🗑️ Delete", key=f"pop_del_{topic['id']}", type="primary", use_container_width=True):
                delete_topic(user_id, topic["id"])
                st.rerun()

    # Instant Optimistic Persistence
    if checked != is_completed:
        new_status = "Completed" if checked else "Not Started"
        def _save():
            save_progress(
                user_id=user_id,
                item_type="topic",
                item_id=topic["id"],
                status=new_status,
                understanding=topic.get("understanding", 3),
                notes=topic.get("notes", "") or "",
                is_important=topic.get("is_important", 0),
                is_difficult=topic.get("is_difficult", 0),
                needs_practice=topic.get("needs_practice", 0)
            )
            if checked:
                schedule_revisions(user_id, "topic", topic["id"])
        set_optimistic_topic_status(user_id, topic["id"], new_status, _save)
        if checked:
            render_floating_xp_toast(25, f"Completed '{topic['name']}'! (+25 XP)")
        else:
            st.toast(f"Marked '{topic['name']}' as not started.", icon="⚪")


# ══════════════════════════════════════════════════════════════════════════
# 2. TOPIC DETAIL WORKSPACE (Central Workspace for a Concept)
# ══════════════════════════════════════════════════════════════════════════

def _render_topic_detail_workspace(user_id: int, subject: dict, chapter: dict, topic: dict):
    """
    Dedicated Topic Workspace containing Overview, Notes, Formulas, Mistakes, Revision,
    and Practice with a right-hand Action Panel [Explain with Nexus AI], [Start Focus], [Practice].
    """
    col_back, col_actions = st.columns([4, 1])
    with col_back:
        if st.button(f"‹ Back to {subject['name']} Chapters", key="btn_back_to_chaps"):
            st.session_state.pop("learn_detail_topic_id", None)
            st.rerun()

    und = topic.get("understanding", 3)
    stars = "★" * und + "☆" * (5 - und)

    render_html(f"""
        <div class="nexus-card" style="border-left: 4px solid {subject.get('color', '#38BDF8')}; margin: 12px 0 18px 0; padding: 20px 24px;">
            <div style="font-size: 0.8rem; color: var(--nexus-text-sub); margin-bottom: 2px;">
                {subject['name']} › {chapter['name']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--nexus-text-title); margin: 0;">
                    {topic['name']}
                </h1>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="nexus-pill-revision" style="font-size: 0.76rem;">{topic.get('status', 'Not Started')}</span>
                    <span style="color: #F59E0B; font-size: 1.05rem;">{stars}</span>
                </div>
            </div>
        </div>
    """)

    col_content, col_side_panel = st.columns([2.8, 1.2])

    with col_content:
        top_tab1, top_tab2, top_tab3 = st.tabs(["📖 Topic Overview & Notes", "📐 Formulas", "❌ Mistakes & Recall"])

        with top_tab1:
            st.markdown("### 📝 Notes & Concept Summary")
            notes = get_all_notes(user_id, subject_id=subject["id"])
            topic_notes = [n for n in notes if n.get("topic_id") == topic["id"]]
            if not topic_notes:
                st.info("No personal notes written for this topic yet.")
                if st.button("➕ Write Note for this Topic", key=f"write_n_top_{topic['id']}"):
                    st.session_state["note_prefill_subj"] = subject["id"]
                    st.session_state["note_prefill_chap"] = chapter["id"]
                    st.session_state["note_prefill_top"] = topic["id"]
                    st.toast("Opened note creator!", icon="✨")
            else:
                for n in topic_notes:
                    st.markdown(f"#### {n['title']}")
                    st.markdown(n["content"])
                    st.markdown("---")

        with top_tab2:
            st.markdown("### 📐 Key Equations & KaTeX Formulas")
            formulas = get_all_formulas(user_id, subject_id=subject["id"])
            sub_forms = [f for f in formulas if f.get("chapter_id") == chapter["id"]]
            if not sub_forms:
                st.info("No formulas logged for this chapter yet.")
            else:
                for f in sub_forms:
                    st.markdown(f"**{f['title']}**")
                    st.latex(f["formula_latex"])
                    if f.get("description"):
                        st.caption(f["description"])

        with top_tab3:
            st.markdown("### 🎯 Active Recall & Practice History")
            st.markdown(f"Practice active retrieval for **{topic['name']}** to lock concepts into long-term memory.")
            if st.button("🚀 Launch Active Recall Assessment", key=f"launch_rec_{topic['id']}", type="primary"):
                st.session_state["practice_active_tab"] = "💡 Active Recall"
                st.session_state["active_recall_target_topic_id"] = topic["id"]
                st.session_state["current_page"] = "🎯 Practice"
                st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
                st.rerun()

    with col_side_panel:
        render_html("""
            <div class="nexus-action-panel">
                <span style="font-size: 0.78rem; font-weight: 700; color: var(--nexus-accent); text-transform: uppercase; letter-spacing: 0.08em;">
                    ⚡ ACTIONS
                </span>
            </div>
        """)
        if st.button("🤖 Explain with Nexus AI", type="primary", use_container_width=True, key="top_exp_ai"):
            st.session_state["queued_ai_prompt"] = f"Explain the concept '{topic['name']}' in {subject['name']} from first principles."
            st.session_state["current_page"] = "🤖 Nexus AI"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

        if st.button("⏱️ Start 25m Focus", use_container_width=True, key="top_start_foc"):
            st.session_state["focus_target_subject_id"] = subject["id"]
            st.session_state["focus_target_chapter_id"] = chapter["id"]
            st.session_state["focus_target_topic_id"] = topic["id"]
            st.session_state["current_page"] = "⏱️ Focus"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

        if st.button("🎯 Practice Quiz", use_container_width=True, key="top_start_prac"):
            st.session_state["current_page"] = "🎯 Practice"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 3. NOTES WORKSPACE (2-Column Notes Layout)
# ══════════════════════════════════════════════════════════════════════════

def _render_notes_workspace(user_id: int):
    subjects = get_all_subjects(user_id)
    if not subjects:
        st.warning("Please configure subjects in the Syllabus Manager first.")
        return

    s_map = {s["name"]: s["id"] for s in subjects}

    col_note_list, col_note_editor = st.columns([1.1, 1.9])

    with col_note_list:
        st.markdown("### 📚 Notes Library")
        search_q = st.text_input("Search notes...", placeholder="🔍 Title, tag, or topic...", key="notes_ws_search_q")
        sel_subj_filter = st.selectbox("Subject Filter", ["All Subjects"] + list(s_map.keys()), key="notes_ws_subj_f")

        sub_id_f = s_map.get(sel_subj_filter) if sel_subj_filter != "All Subjects" else None
        all_notes = get_all_notes(user_id, subject_id=sub_id_f)

        if search_q:
            q = search_q.lower()
            all_notes = [n for n in all_notes if q in n["title"].lower() or q in n["content"].lower() or q in n.get("tags", "").lower()]

        if not all_notes:
            render_empty_state("📝", "No Notes Found", "Write your first note in the editor on the right!")
        else:
            for n in all_notes:
                is_sel = (st.session_state.get("active_note_id") == n["id"])
                border_col = "#38BDF8" if is_sel else "rgba(255,255,255,0.08)"
                
                if st.button(f"{'📌 ' if n.get('is_pinned') else '📝 '}{n['title']}\n({n.get('subject_name', '')})", key=f"note_sel_btn_{n['id']}", use_container_width=True):
                    st.session_state["active_note_id"] = n["id"]
                    st.rerun()

    with col_note_editor:
        st.markdown("### ✍️ Note Editor")
        active_n_id = st.session_state.get("active_note_id")
        active_note = next((n for n in all_notes if n["id"] == active_n_id), None) if active_n_id else None

        pre_s_idx = 0
        if active_note:
            for i, (sn, sid) in enumerate(s_map.items()):
                if sid == active_note.get("subject_id"):
                    pre_s_idx = i
                    break

        c_s, c_c, c_t = st.columns(3)
        with c_s:
            edit_subj_name = st.selectbox("Subject", list(s_map.keys()), index=pre_s_idx, key="note_ed_subj")
        edit_subj_id = s_map[edit_subj_name]

        chapters = get_chapters_for_subject(user_id, edit_subj_id)
        c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
        with c_c:
            edit_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="note_ed_chap")
        edit_chap_id = c_map.get(edit_chap_name)

        topics = get_topics_for_chapter(user_id, edit_chap_id) if edit_chap_id else []
        t_map = {t["name"]: t["id"] for t in topics} if topics else {}
        with c_t:
            edit_top_name = st.selectbox("Topic", list(t_map.keys()) if t_map else ["None"], key="note_ed_top")
        edit_top_id = t_map.get(edit_top_name)

        render_latex_math_keyboard("note_ed_content", label="LaTeX Math Symbols")

        n_title = st.text_input("Note Title", value=active_note["title"] if active_note else "", placeholder="e.g. Lens Formula and Derivations", key="note_ed_title")
        n_tags = st.text_input("Tags", value=active_note.get("tags", "") if active_note else "", placeholder="e.g. physics, formula, exam_target", key="note_ed_tags")
        n_content = st.text_area("Note Content (Markdown & LaTeX)", value=active_note["content"] if active_note else "", height=200, placeholder="Write note content with **bold**, equations $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$, and bullet points...", key="note_ed_content")
        is_pin = st.checkbox("📌 Pin to Top", value=bool(active_note.get("is_pinned", False)) if active_note else False, key="note_ed_pin")

        col_save_n, col_del_n = st.columns([3, 1])
        with col_save_n:
            if st.button("⚡ Save Note (+25 XP)", type="primary", use_container_width=True, key="note_ed_save_btn"):
                if not n_title.strip() or not n_content.strip() or not edit_top_id:
                    st.error("Please provide Title, Content, and select a Topic.")
                else:
                    add_note(user_id, edit_subj_id, edit_chap_id, edit_top_id, n_title.strip(), n_content, n_tags.strip(), 1 if is_pin else 0)
                    render_floating_xp_toast(25, f"Saved note '{n_title}'! (+25 XP)")
                    st.rerun()

        with col_del_n:
            if active_note and st.button("🗑️ Delete", key="note_ed_del_btn", use_container_width=True):
                delete_note(user_id, active_note["id"])
                st.session_state.pop("active_note_id", None)
                st.toast("Note deleted", icon="🗑️")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 4. FORMULAS VAULT
# ══════════════════════════════════════════════════════════════════════════

def _render_formulas_vault(user_id: int):
    subjects = get_all_subjects(user_id)
    if not subjects:
        st.warning("Please configure subjects in the Syllabus Manager first.")
        return

    s_filt_map = {"All Subjects": None}
    s_filt_map.update({s["name"]: s["id"] for s in subjects})

    col_f1, col_f2, col_f3 = st.columns([1.2, 2.2, 1.4])
    with col_f1:
        sel_s = st.selectbox("Subject Filter", list(s_filt_map.keys()), key="f_vault_s_filter")
    with col_f2:
        search_f = st.text_input("Search formulas...", placeholder="🔍 Formula name or keyword...", key="f_vault_search")
    with col_f3:
        anki_tsv = export_formulas_to_anki(user_id, subject_id=s_filt_map[sel_s], format_type="tsv")
        st.download_button(
            "📥 Export to Anki (.tsv)",
            data=anki_tsv,
            file_name="Nexus_Formulas.tsv",
            mime="text/tab-separated-values",
            use_container_width=True,
            key="f_vault_dl_anki"
        )

    # Add Formula Modal / Popover
    with st.expander("➕ Add New Formula to Reference Vault", expanded=False):
        s_map = {s["name"]: s["id"] for s in subjects}
        c1, c2 = st.columns(2)
        with c1:
            f_s_name = st.selectbox("Subject", list(s_map.keys()), key="add_f_subj")
        f_s_id = s_map[f_s_name]

        f_chaps = get_chapters_for_subject(user_id, f_s_id)
        f_c_map = {c["name"]: c["id"] for c in f_chaps} if f_chaps else {}
        with c2:
            f_c_name = st.selectbox("Chapter", list(f_c_map.keys()) if f_c_map else ["None"], key="add_f_chap")
        f_c_id = f_c_map.get(f_c_name)

        render_latex_math_keyboard("add_f_code", label="KaTeX Math Symbol Keyboard")

        f_title = st.text_input("Formula Title", placeholder="e.g. Mirror Formula, Snell's Law", key="add_f_title")
        f_code = st.text_area("LaTeX Formula Code", placeholder=r"e.g. \frac{1}{f} = \frac{1}{v} + \frac{1}{u}", key="add_f_code")
        f_desc = st.text_input("Description & Variable Conditions", placeholder="e.g. u = object distance, v = image distance, f = focal length", key="add_f_desc")

        if st.button("⚡ Save Formula to Vault", type="primary", use_container_width=True, key="add_f_save_btn"):
            if not f_title or not f_code or not f_c_id:
                st.error("Please provide Title, LaTeX code, and select a Chapter.")
            else:
                add_formula(user_id, f_s_id, f_c_id, f_title.strip(), f_code.strip(), description=f_desc.strip())
                st.toast(f"Formula '{f_title}' added to vault!", icon="📐")
                st.rerun()

    formulas = get_all_formulas(user_id, subject_id=s_filt_map[sel_s])
    if search_f:
        q = search_f.lower()
        formulas = [f for f in formulas if q in f["title"].lower() or q in f["formula_latex"].lower() or q in f.get("description", "").lower()]

    if not formulas:
        render_empty_state("📐", "Formula Vault is Empty", "Add your first formula above to build your quick-reference equation library!")
    else:
        for f in formulas:
            with st.container():
                render_html(f"""
                    <div class="nexus-formula-card" style="border-left: 4px solid {f.get('subject_color', '#38BDF8')};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.76rem; font-weight: 700; color: {f.get('subject_color', '#38BDF8')};">
                                {f.get('subject_name')} › {f.get('chapter_name')}
                            </span>
                            <span style="font-size: 0.85rem; color: #F97316;">{'⭐ Favorite' if f.get('is_favorite') else ''}</span>
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 800; color: var(--nexus-text-title); margin-bottom: 8px;">
                            {f['title']}
                        </div>
                    </div>
                """)
                st.latex(f["formula_latex"])
                if f.get("description"):
                    st.caption(f"📝 {f['description']}")

                c_fav, c_del, _ = st.columns([1.2, 1.2, 4])
                with c_fav:
                    fav_txt = "★ Unfavorite" if f.get("is_favorite") else "☆ Favorite"
                    if st.button(fav_txt, key=f"f_fav_{f['id']}"):
                        toggle_formula_favorite(user_id, f["id"], 0 if f.get("is_favorite") else 1)
                        st.rerun()
                with c_del:
                    if st.button("🗑️ Delete", key=f"f_del_{f['id']}"):
                        delete_formula(user_id, f["id"])
                        st.rerun()
                st.markdown("<hr style='margin: 10px 0; opacity: 0.1;'/>", unsafe_allow_html=True)


def _render_csv_import_tool(user_id: int):
    st.markdown("**Upload CSV (Subject, Chapter, Topic)**")
    uploaded = st.file_uploader("Choose CSV", type=["csv"], key="learn_csv_up_pop", label_visibility="collapsed")
    if uploaded is not None:
        try:
            content = uploaded.getvalue().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            raw_fields = [f.strip() if f else "" for f in (reader.fieldnames or [])]
            sub_col = next((f for f in raw_fields if f.lower() == "subject"), None)
            chap_col = next((f for f in raw_fields if f.lower() == "chapter"), None)
            top_col = next((f for f in raw_fields if f.lower() == "topic"), None)

            if sub_col and chap_col and top_col:
                rows = []
                for r in reader:
                    if len(rows) >= 500:
                        break
                    s_val, c_val, t_val = r.get(sub_col, "").strip(), r.get(chap_col, "").strip(), r.get(top_col, "").strip()
                    if s_val and c_val and t_val:
                        rows.append({"Subject": s_val[:100], "Chapter": c_val[:150], "Topic": t_val[:200]})
                if rows:
                    if st.button(f"🚀 Import {len(rows)} Rows", type="primary", use_container_width=True, key="btn_imp_csv_act"):
                        import_syllabus_from_csv(user_id, rows)
                        st.success("Syllabus imported successfully!")
                        st.rerun()
        except Exception as e:
            st.error("Invalid CSV format.")
