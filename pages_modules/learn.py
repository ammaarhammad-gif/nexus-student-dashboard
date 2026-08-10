"""
learn.py — Nexus Unified Learn Module.

Consolidates:
1. 📚 Syllabus Manager (CBSE/ICSE/Custom curriculum tracking, 1-click status tick, understanding stars, shortcuts)
2. 📝 Notes Repository (Markdown & LaTeX syllabus notes, tagging, pin to top, topic linking)
3. 📐 Formula Vault (KaTeX equations, interactive math keyboard, favorites, Anki export)
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
    add_formula, get_all_formulas, toggle_formula_favorite, delete_formula
)
from preloaded_syllabi import preload_standard_syllabus, reload_and_replace_syllabus
from styles import render_top_header_bar, render_header, render_breadcrumbs, render_empty_state, render_html
from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_formulas_to_anki


STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "Revision Done"]
STATUS_ICONS = {
    "Not Started": "⚪",
    "In Progress": "🟡",
    "Completed": "🟢",
    "Revision Done": "🔵"
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
        "Master your syllabus, one concept at a time.",
        ["NEXUS", "Learn"]
    )

    tab_syllabus, tab_notes, tab_formulas = st.tabs([
        "📚 Syllabus",
        "📝 Notes",
        "📐 Formulas"
    ])

    with tab_syllabus:
        _render_syllabus_view(user_id, board, class_name)

    with tab_notes:
        _render_notes_view(user_id)

    with tab_formulas:
        _render_formulas_view(user_id)



# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 1: SYLLABUS MANAGER
# ══════════════════════════════════════════════════════════════════════════

def _render_syllabus_view(user_id: int, board: str, class_name: str):
    subtab_manage, subtab_csv = st.tabs(["📖 My Syllabus", "📥 Import Custom CSV"])

    with subtab_manage:
        subjects = get_all_subjects(user_id)

        # Auto-load official syllabus if user has no subjects
        if not subjects:
            with st.spinner(f"⚡ Loading official {board} ({class_name}) syllabus for you..."):
                loaded = preload_standard_syllabus(user_id, board, class_name)
                if loaded:
                    st.toast(f"✅ Official {board} ({class_name}) syllabus loaded!", icon="🚀")
                    st.rerun()

        # Subject Action Toolbar
        col_tb1, col_tb2 = st.columns([3, 1])
        with col_tb1:
            st.caption(f"Curriculum: **{board} {class_name}**. Click any checkbox to mark a topic done, or use the 1-click shortcuts for Notes, Recall & Focus.")
        with col_tb2:
            with st.popover("⚙️ Syllabus Options"):
                st.markdown("**➕ Add Custom Subject**")
                with st.form("add_subject_form_learn", clear_on_submit=True):
                    new_sub_name = st.text_input("Subject Name", placeholder="e.g. Economics, Computer Apps")
                    sub_color = st.color_picker("Subject Color", value="#38BDF8")
                    if st.form_submit_button("Create Subject", use_container_width=True):
                        if new_sub_name.strip():
                            res = add_subject(user_id, new_sub_name.strip(), sub_color)
                            if res:
                                st.success(f"Created '{new_sub_name}'!")
                                st.rerun()
                            else:
                                st.error("Subject already exists.")

                st.markdown("---")
                if st.button(f"🔄 Reload Full {board} ({class_name}) Syllabus", use_container_width=True, key="reload_syl_learn_btn"):
                    with st.spinner("Replacing syllabus with official curriculum..."):
                        reload_and_replace_syllabus(user_id, board, class_name)
                    st.success("Official syllabus reloaded!")
                    st.rerun()

        if not subjects:
            st.info("📝 Loading your syllabus... Please refresh if it does not load automatically.")
            return

        # Subject Selector
        subject_names = [s["name"] for s in subjects]
        pre_sel_s_id = st.session_state.get("learn_preselected_subject_id")
        sel_idx = 0
        if pre_sel_s_id:
            for i, s in enumerate(subjects):
                if s["id"] == pre_sel_s_id:
                    sel_idx = i
                    break

        selected_idx = st.selectbox(
            "Select Subject to View & Track:",
            range(len(subject_names)),
            index=sel_idx,
            format_func=lambda i: f"📖 {subject_names[i]}",
            key="learn_subject_selector"
        )
        selected_subject = subjects[selected_idx]

        # Fetch subject hierarchy in single indexed query
        chapters = get_subject_hierarchy(user_id, selected_subject["id"])
        total_subject_topics = sum(len(ch["topics"]) for ch in chapters)
        completed_subject_topics = sum(
            1 for ch in chapters for t in ch["topics"]
            if t["status"] in ["Completed", "Revision Done"]
        )
        sub_pct = round((completed_subject_topics / total_subject_topics * 100)) if total_subject_topics > 0 else 0

        st.markdown(f"""
            <div class="nexus-card" style="border-top: 4px solid {selected_subject['color']}; margin-top: 10px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <h2 style="margin: 0; font-size: 1.6rem; color: var(--nexus-text-title);">{selected_subject['name']}</h2>
                        <span style="font-size: 0.9rem; color: var(--nexus-text-sub);">{len(chapters)} Chapters • {total_subject_topics} Topics</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.8rem; font-weight: 800; color: {selected_subject['color']};">{sub_pct}%</span>
                        <span style="font-size: 0.85rem; display: block; color: var(--nexus-text-sub);">{completed_subject_topics}/{total_subject_topics} Done</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Add Chapter Form
        with st.expander(f"➕ Add Custom Chapter to {selected_subject['name']}", expanded=False):
            with st.form(f"learn_add_chap_form_{selected_subject['id']}", clear_on_submit=True):
                chap_name = st.text_input("Chapter Name", placeholder="e.g. Chapter 6: Optics & Light Refraction")
                if st.form_submit_button("Add Chapter", use_container_width=True):
                    if chap_name.strip():
                        add_chapter(user_id, selected_subject["id"], chap_name.strip())
                        st.success(f"Added '{chap_name.strip()}'!")
                        st.rerun()

        if not chapters:
            st.info("No chapters in this subject yet. Add a chapter above or reload the official curriculum.")
            return

        # Render Chapters & Topics
        for chap_idx, chap in enumerate(chapters):
            topics = chap["topics"]
            ch_done = sum(1 for t in topics if t["status"] in ["Completed", "Revision Done"])
            ch_total = len(topics)
            ch_badge = f"{ch_done}/{ch_total} Done" if ch_total > 0 else "0 Topics"
            is_all_done = (ch_done == ch_total and ch_total > 0)
            icon_prefix = "✅" if is_all_done else "📌"

            with st.expander(f"{icon_prefix} {chap['name']}  ({ch_badge})", expanded=(chap_idx == 0)):
                col_ch_info, col_ch_act = st.columns([4, 1])
                with col_ch_act:
                    with st.popover("⚙️ Chapter"):
                        new_c_name = st.text_input("Rename Chapter", value=chap["name"], key=f"learn_ren_c_{chap['id']}")
                        if st.button("Save Name", key=f"learn_save_c_{chap['id']}"):
                            if new_c_name.strip():
                                rename_chapter(user_id, chap["id"], new_c_name.strip())
                                st.rerun()

                        st.markdown("---")
                        mv1, mv2 = st.columns(2)
                        with mv1:
                            if st.button("⬆️ Up", key=f"learn_up_c_{chap['id']}", disabled=(chap_idx == 0)):
                                move_chapter(user_id, chap["id"], "up")
                                st.rerun()
                        with mv2:
                            if st.button("⬇️ Down", key=f"learn_down_c_{chap['id']}", disabled=(chap_idx == len(chapters) - 1)):
                                move_chapter(user_id, chap["id"], "down")
                                st.rerun()

                        st.markdown("---")
                        if st.button("🗑️ Delete Chapter", type="primary", key=f"learn_del_c_{chap['id']}"):
                            delete_chapter(user_id, chap["id"])
                            st.rerun()

                # Add Topic form
                with st.form(f"learn_add_top_form_{chap['id']}", clear_on_submit=True):
                    col_t1, col_t2 = st.columns([4, 1])
                    with col_t1:
                        top_name = st.text_input(
                            "Add Topic",
                            placeholder="e.g. Total Internal Reflection, Snell's Law",
                            key=f"learn_inp_top_{chap['id']}",
                            label_visibility="collapsed"
                        )
                    with col_t2:
                        top_submitted = st.form_submit_button("➕ Add Topic", use_container_width=True)
                    if top_submitted and top_name.strip():
                        add_topic(user_id, chap["id"], top_name.strip())
                        st.success("Topic added!")
                        st.rerun()

                if not topics:
                    st.caption("No topics in this chapter yet.")
                    continue

                for topic in topics:
                    _render_learn_topic_card(user_id, topic, selected_subject, chap)

    with subtab_csv:
        _render_csv_import_view(user_id)


def _render_learn_topic_card(user_id: int, topic: dict, subject: dict, chapter: dict):
    """Render a topic with 1-click status ticking, understanding slider, and direct shortcuts."""
    is_completed = (topic["status"] in ["Completed", "Revision Done"])

    col_check, col_details_btn = st.columns([5, 1])

    with col_check:
        checked = st.checkbox(
            label=f"**{topic['name']}**",
            value=is_completed,
            key=f"learn_quick_tick_{topic['id']}",
            help="Click to tick off this topic as completed!"
        )

    with col_details_btn:
        with st.popover("⚙️ Edit"):
            st.markdown(f"**Options for: {topic['name']}**")
            new_status_select = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(topic["status"]) if topic["status"] in STATUS_OPTIONS else 0,
                key=f"learn_status_sel_{topic['id']}"
            )
            new_understanding = st.selectbox(
                "Understanding Level",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: UNDERSTANDING_LABELS[x],
                index=max(0, min(4, topic["understanding"] - 1)),
                key=f"learn_und_sel_{topic['id']}"
            )

            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                is_imp = st.checkbox("⭐ Important", value=bool(topic["is_important"]), key=f"learn_imp_{topic['id']}")
            with col_f2:
                is_diff = st.checkbox("⚠️ Difficult", value=bool(topic["is_difficult"]), key=f"learn_diff_{topic['id']}")
            with col_f3:
                is_prac = st.checkbox("🔄 Practice", value=bool(topic["needs_practice"]), key=f"learn_prac_{topic['id']}")

            edit_notes = st.text_input(
                "Quick Key Formulae / Note",
                value=topic.get("notes", "") or "",
                key=f"learn_notes_inp_{topic['id']}"
            )

            if st.button("💾 Save Changes", key=f"learn_save_det_{topic['id']}", use_container_width=True):
                save_progress(
                    user_id=user_id,
                    item_type="topic",
                    item_id=topic["id"],
                    status=new_status_select,
                    understanding=new_understanding,
                    notes=edit_notes,
                    is_important=int(is_imp),
                    is_difficult=int(is_diff),
                    needs_practice=int(is_prac)
                )
                if new_status_select == "Completed" and topic["status"] != "Completed":
                    schedule_revisions(user_id, "topic", topic["id"])
                st.toast("Saved changes!", icon="✅")
                st.rerun()

            st.markdown("---")
            ren_t = st.text_input("Rename Topic", value=topic["name"], key=f"learn_ren_t_{topic['id']}")
            if st.button("✏️ Rename", key=f"learn_btn_ren_{topic['id']}"):
                if ren_t.strip():
                    rename_topic(user_id, topic["id"], ren_t.strip())
                    st.rerun()

            if st.button("🗑️ Delete Topic", type="primary", key=f"learn_del_t_{topic['id']}"):
                delete_topic(user_id, topic["id"])
                st.rerun()

    # Detect 1-click status tick change
    if checked != is_completed:
        new_status = "Completed" if checked else "Not Started"
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
            st.toast(f"🌟 Completed '{topic['name']}'! Revision reminders scheduled.", icon="🎉")
        st.rerun()

    # Topic Shortcut Action Bar: Note, Recall, Focus
    c_sc1, c_sc2, c_sc3, c_sc_pad = st.columns([1.2, 1.4, 1.2, 3])
    with c_sc1:
        if st.button("📝 Note", key=f"sc_note_{topic['id']}", help="Write/view notes for this topic"):
            st.session_state["note_prefill_subj"] = subject["id"]
            st.session_state["note_prefill_chap"] = chapter["id"]
            st.session_state["note_prefill_top"] = topic["id"]
            st.toast(f"📝 Linked to Notes for '{topic['name']}'", icon="✨")
    with c_sc2:
        if st.button("💡 Recall", key=f"sc_recall_{topic['id']}", help="Launch Active Recall practice for this topic"):
            st.session_state["practice_active_tab"] = "💡 Active Recall"
            st.session_state["active_recall_target_topic_id"] = topic["id"]
            st.session_state["current_page"] = "🎯 Practice"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()
    with c_sc3:
        if st.button("⏱️ Focus", key=f"sc_focus_{topic['id']}", help="Launch Focus session on this topic"):
            st.session_state["focus_target_subject_id"] = subject["id"]
            st.session_state["focus_target_chapter_id"] = chapter["id"]
            st.session_state["focus_target_topic_id"] = topic["id"]
            st.session_state["current_page"] = "⏱️ Focus"
            st.session_state["nav_epoch"] = st.session_state.get("nav_epoch", 0) + 1
            st.rerun()

    # Display Badges
    flags_html = []
    if topic.get("is_important"):
        flags_html.append("<span style='color: #FDE047; font-size: 0.78rem;'>⭐ Important</span>")
    if topic.get("is_difficult"):
        flags_html.append("<span style='color: #F87171; font-size: 0.78rem;'>⚠️ Difficult</span>")
    if topic.get("needs_practice"):
        flags_html.append("<span style='color: #60A5FA; font-size: 0.78rem;'>🔄 Needs Practice</span>")
    if topic.get("notes"):
        flags_html.append(f"<span style='font-size: 0.78rem; font-style: italic; color: var(--nexus-text-sub);'>📝 {topic['notes']}</span>")

    if flags_html:
        st.markdown(f"<div style='margin-left: 28px; margin-bottom: 6px; display: flex; gap: 12px; flex-wrap: wrap;'>{' • '.join(flags_html)}</div>", unsafe_allow_html=True)

    # Subtopics
    subtopics = topic.get("subtopics", [])
    if subtopics:
        for sub in subtopics:
            sub_done = (sub["status"] == "Completed")
            sub_c1, sub_c2 = st.columns([5, 1])
            with sub_c1:
                sub_checked = st.checkbox(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;└ {sub['name']}",
                    value=sub_done,
                    key=f"learn_sub_tick_{sub['id']}"
                )
                if sub_checked != sub_done:
                    new_sub_stat = "Completed" if sub_checked else "Not Started"
                    save_progress(user_id, "subtopic", sub["id"], status=new_sub_stat,
                                understanding=sub["understanding"])
                    if sub_checked:
                        schedule_revisions(user_id, "subtopic", sub["id"])
                    st.rerun()
            with sub_c2:
                if st.button("❌", key=f"learn_del_sub_{sub['id']}", help="Delete subtopic"):
                    delete_subtopic(user_id, sub["id"])
                    st.rerun()

    with st.popover(f"➕ Add Subtopic", key=f"learn_add_sub_pop_{topic['id']}"):
        new_subtop = st.text_input("Subtopic Name", key=f"learn_inp_sub_{topic['id']}")
        if st.button("Save Subtopic", key=f"learn_save_sub_{topic['id']}"):
            if new_subtop.strip():
                add_subtopic(user_id, topic["id"], new_subtop.strip())
                st.rerun()

    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)


def _render_csv_import_view(user_id: int):
    st.subheader("📥 Import Syllabus from CSV")
    st.markdown("""
        Upload a CSV file with three columns: **Subject**, **Chapter**, **Topic**.  
        Existing subjects/chapters/topics are automatically skipped (no duplicates).
    """)

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"], key="learn_csv_syllabus_upload")
    if uploaded is not None:
        try:
            content = uploaded.getvalue().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            raw_fields = [f.strip() if f else "" for f in (reader.fieldnames or [])]
            sub_col = next((f for f in raw_fields if f.lower() == "subject"), None)
            chap_col = next((f for f in raw_fields if f.lower() == "chapter"), None)
            top_col = next((f for f in raw_fields if f.lower() == "topic"), None)

            if not (sub_col and chap_col and top_col):
                st.error(f"CSV must contain columns: **Subject**, **Chapter**, **Topic**. Found: {', '.join(raw_fields)}")
                return

            rows = []
            for r in reader:
                s_val = r.get(sub_col, "").strip()
                c_val = r.get(chap_col, "").strip()
                t_val = r.get(top_col, "").strip()
                if s_val and c_val and t_val:
                    rows.append({"Subject": s_val, "Chapter": c_val, "Topic": t_val})
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            return

        if not rows:
            st.warning("The CSV file has no valid rows.")
            return

        st.success(f"✅ Found **{len(rows)}** valid rows in the CSV.")
        st.table(rows[:10])

        if st.button("🚀 Import Syllabus", use_container_width=True, type="primary", key="btn_learn_import_csv"):
            with st.spinner("Importing syllabus..."):
                result = import_syllabus_from_csv(user_id, rows)
            st.success(
                f"✅ Import complete! "
                f"Created **{result['subjects']}** subjects, "
                f"**{result['chapters']}** chapters, "
                f"**{result['topics']}** topics."
            )
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 2: NOTES REPOSITORY
# ══════════════════════════════════════════════════════════════════════════

def _render_notes_view(user_id: int):
    tab_browse, tab_create = st.tabs(["📚 My Notes Repository", "➕ Write New Note"])

    with tab_create:
        st.subheader("Create Syllabus Note")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            
            # Check prefill from topic shortcut
            pre_s_id = st.session_state.get("note_prefill_subj")
            pre_s_idx = 0
            if pre_s_id:
                for i, (sn, sid) in enumerate(s_map.items()):
                    if sid == pre_s_id:
                        pre_s_idx = i
                        break

            c1, c2, c3 = st.columns(3)
            with c1:
                sel_s_name = st.selectbox("Subject", list(s_map.keys()), index=pre_s_idx, key="learn_note_add_s")
            sel_s_id = s_map[sel_s_name]

            chapters = get_chapters_for_subject(user_id, sel_s_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            pre_c_id = st.session_state.get("note_prefill_chap")
            pre_c_idx = 0
            if pre_c_id and c_map:
                for i, (cn, cid) in enumerate(c_map.items()):
                    if cid == pre_c_id:
                        pre_c_idx = i
                        break

            with c2:
                sel_c_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], index=pre_c_idx, key="learn_note_add_c")
            sel_c_id = c_map.get(sel_c_name)

            topics = get_topics_for_chapter(user_id, sel_c_id) if sel_c_id else []
            t_map = {t["name"]: t["id"] for t in topics} if topics else {}
            pre_t_id = st.session_state.get("note_prefill_top")
            pre_t_idx = 0
            if pre_t_id and t_map:
                for i, (tn, tid) in enumerate(t_map.items()):
                    if tid == pre_t_id:
                        pre_t_idx = i
                        break

            with c3:
                sel_t_name = st.selectbox("Topic", list(t_map.keys()) if t_map else ["None"], index=pre_t_idx, key="learn_note_add_t")
            sel_t_id = t_map.get(sel_t_name)

            render_latex_math_keyboard("learn_note_add_content", label="LaTeX & Equation Symbol Palette")

            title = st.text_input("Note Title", placeholder="e.g. Lens Formula & Sign Convention, Summary of French Revolution", key="learn_note_add_title")
            tags = st.text_input("Tags (comma separated)", placeholder="e.g. formula, high_weightage, quick_revision", key="learn_note_add_tags")
            content = st.text_area("Note Content (Supports Markdown & LaTeX)", height=220, placeholder="Write your notes here with **bold text**, bullet points, definitions, equations like $$E = mc^2$$...", key="learn_note_add_content")
            is_pinned = st.checkbox("📌 Pin note to top", value=False, key="learn_note_add_pinned")

            if st.button("⚡ Save Note (+25 XP)", type="primary", use_container_width=True, key="learn_save_note_btn"):
                if not title or not content or not sel_t_id:
                    st.error("Please provide Title, Content, and select a Topic.")
                else:
                    add_note(user_id, sel_s_id, sel_c_id, sel_t_id, title, content, tags, 1 if is_pinned else 0)
                    st.success(f"Note '{title}' saved successfully! +25 XP")
                    st.session_state["learn_note_add_content"] = ""
                    st.session_state["learn_note_add_title"] = ""
                    st.session_state["learn_note_add_tags"] = ""
                    st.session_state.pop("note_prefill_subj", None)
                    st.session_state.pop("note_prefill_chap", None)
                    st.session_state.pop("note_prefill_top", None)
                    st.rerun()

    with tab_browse:
        subjects = get_all_subjects(user_id)
        s_filt = {"All Subjects": None}
        if subjects:
            s_filt.update({s["name"]: s["id"] for s in subjects})

        c_f1, c_f2 = st.columns([1, 2])
        with c_f1:
            sel_f_s = st.selectbox("Filter Subject", list(s_filt.keys()), key="learn_notes_filt_subj")
        with c_f2:
            search_q = st.text_input("🔍 Search Notes", placeholder="Search title, content, or tag...", key="learn_notes_search_q")

        notes = get_all_notes(user_id, subject_id=s_filt[sel_f_s])
        if search_q:
            q = search_q.lower()
            notes = [n for n in notes if q in n["title"].lower() or q in n["content"].lower() or q in n.get("tags", "").lower()]

        if not notes:
            render_empty_state("📝", "No Notes Found", "Create your first syllabus note to build your personal knowledge repository!")
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
                        if st.button("🗑️ Delete", key=f"learn_del_note_{n['id']}", use_container_width=True):
                            delete_note(user_id, n['id'])
                            st.toast("Note deleted", icon="🗑️")
                            st.rerun()
                    st.markdown("<hr style='margin: 12px 0; opacity: 0.15;'/>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 3: FORMULA VAULT
# ══════════════════════════════════════════════════════════════════════════

def _render_formulas_view(user_id: int):
    tab_vault, tab_add = st.tabs(["📚 Formula Repository", "➕ Add Formula"])

    with tab_add:
        st.subheader("Add Formula to Vault")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            c1, c2 = st.columns(2)
            with c1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="learn_form_add_subj")
            sel_subj_id = s_map[sel_subj_name]

            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            with c2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="learn_form_add_chap")
            sel_chap_id = c_map.get(sel_chap_name)

            render_latex_math_keyboard("learn_form_add_latex_code", label="Interactive Equation & LaTeX Builder")

            title = st.text_input("Formula Title", placeholder="e.g. Lens Formula, Quadratic Equation, Ohm's Law", key="learn_form_add_title")
            latex_code = st.text_area("LaTeX / Math Code", placeholder=r"e.g. \frac{1}{f} = \frac{1}{v} - \frac{1}{u}  or  x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", key="learn_form_add_latex_code")
            desc = st.text_input("Conditions / Description / Notes", placeholder="e.g. Sign convention: u is always negative in Cartesian system", key="learn_form_add_desc")

            if st.button("⚡ Save Formula to Vault", type="primary", use_container_width=True, key="learn_save_form_btn"):
                if not title or not latex_code or not sel_chap_id:
                    st.error("Please provide Title, LaTeX code, and select a Chapter.")
                else:
                    add_formula(user_id, sel_subj_id, sel_chap_id, title, latex_code, description=desc)
                    st.success(f"Formula '{title}' saved successfully!")
                    st.session_state["learn_form_add_latex_code"] = ""
                    st.session_state["learn_form_add_title"] = ""
                    st.session_state["learn_form_add_desc"] = ""
                    st.rerun()

    with tab_vault:
        subjects = get_all_subjects(user_id)
        s_filt_map = {"All Subjects": None}
        if subjects:
            s_filt_map.update({s["name"]: s["id"] for s in subjects})

        c_f1, c_f2, c_f3 = st.columns([1, 2, 1])
        with c_f1:
            sel_filt_s = st.selectbox("Filter by Subject", list(s_filt_map.keys()), key="learn_form_filt_subj")
        with c_f2:
            search_txt = st.text_input("🔍 Search Formulas", placeholder="Search title or equation...", key="learn_form_search_q")
        with c_f3:
            anki_tsv_data = export_formulas_to_anki(user_id, subject_id=s_filt_map[sel_filt_s], format_type="tsv")
            st.download_button(
                label="📥 Export to Anki (.tsv)",
                data=anki_tsv_data,
                file_name=f"Nexus_Formulas_{sel_filt_s.replace(' ', '_')}.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="learn_dl_form_anki_tsv"
            )

        formulas = get_all_formulas(user_id, subject_id=s_filt_map[sel_filt_s])
        if search_txt:
            formulas = [f for f in formulas if search_txt.lower() in f["title"].lower() or search_txt.lower() in f["formula_latex"].lower() or search_txt.lower() in f.get("description", "").lower()]

        if not formulas:
            render_empty_state("📐", "No Formulas Found", "Add formulas to your vault to access them instantly during revision and export to Anki!")
        else:
            for f in formulas:
                with st.container():
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {f.get('subject_color', '#38BDF8')};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-size: 0.75rem; font-weight: 700; color: {f.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 12px;">
                                        {f.get('subject_name')}
                                    </span>
                                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">{f.get('chapter_name')}</span>
                                </div>
                                <span style="font-size: 0.85rem; color: #F97316;">{'⭐ Favorite' if f.get('is_favorite') else ''}</span>
                            </div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                                {f['title']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    st.latex(f["formula_latex"])

                    if f.get("description"):
                        st.caption(f"📝 {f['description']}")

                    c_act1, c_act2, c_act3 = st.columns([1, 1, 4])
                    with c_act1:
                        fav_label = "★ Unfavorite" if f.get("is_favorite") else "☆ Favorite"
                        if st.button(fav_label, key=f"learn_fav_btn_{f['id']}"):
                            toggle_formula_favorite(user_id, f['id'], 0 if f.get("is_favorite") else 1)
                            st.rerun()
                    with c_act2:
                        if st.button("🗑️ Delete", key=f"learn_del_form_{f['id']}"):
                            delete_formula(user_id, f['id'])
                            st.toast("Formula deleted", icon="🗑️")
                            st.rerun()
                    st.markdown("<hr style='margin: 10px 0; opacity: 0.15;'/>", unsafe_allow_html=True)
