"""
syllabus.py — Syllabus Manager & Progress Tracker page.

Full CRUD for: Subjects → Chapters → Topics → Subtopics
Plus inline progress tracking (status, understanding, notes, flags).
"""

import streamlit as st
from models import (
    get_all_subjects, add_subject, rename_subject, delete_subject,
    get_chapters_for_subject, add_chapter, rename_chapter, delete_chapter,
    move_chapter,
    get_topics_for_chapter, add_topic, rename_topic, delete_topic,
    get_subtopics_for_topic, add_subtopic, rename_subtopic, delete_subtopic,
    get_progress, save_progress
)
from styles import render_header

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "Revision Done"]
STATUS_ICONS = {
    "Not Started":   "⚪",
    "In Progress":   "🟡",
    "Completed":     "🟢",
    "Revision Done": "🔵"
}

UNDERSTANDING_LABELS = {
    1: "1 — Very Difficult 🔴",
    2: "2 — Difficult 🟠",
    3: "3 — Okay 🟡",
    4: "4 — Good 🟢",
    5: "5 — Mastered 🌟"
}


def render_syllabus_page(user_id: int):
    render_header(
        "📚 Syllabus Manager",
        "Add subjects, chapters, and topics. Track your progress for each item."
    )

    subjects = get_all_subjects(user_id)

    # ── Add New Subject ──
    with st.expander("➕ Add New Subject", expanded=(len(subjects) == 0)):
        with st.form("add_subject_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_sub_name = st.text_input(
                    "Subject Name",
                    placeholder="e.g. Mathematics, Physics, English"
                )
            with col2:
                sub_color = st.color_picker("Color", value="#6366F1")
            sub_submitted = st.form_submit_button("Save Subject", use_container_width=True)
            if sub_submitted:
                if not new_sub_name.strip():
                    st.error("Please enter a subject name.")
                else:
                    result = add_subject(user_id, new_sub_name.strip(), sub_color)
                    if result is None:
                        st.error(f"Subject '{new_sub_name.strip()}' already exists!")
                    else:
                        st.success(f"✅ Subject '{new_sub_name.strip()}' created!")
                        st.rerun()

    if not subjects:
        st.info("📝 No subjects yet. Use the form above to add your first subject!")
        return

    st.markdown("---")

    # ── Subject Selection ──
    subject_names = [s["name"] for s in subjects]
    selected_idx = st.selectbox(
        "Select Subject",
        range(len(subject_names)),
        format_func=lambda i: f"📖 {subject_names[i]}",
        key="subject_selector"
    )
    selected_subject = subjects[selected_idx]

    # ── Subject Header & Actions ──
    col_sub_title, col_sub_actions = st.columns([3, 1])
    with col_sub_title:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <div style="width: 8px; height: 36px; background: {selected_subject['color']};
                     border-radius: 4px;"></div>
                <h3 style="margin: 0; color: #F8FAFC;">{selected_subject['name']}</h3>
            </div>
        """, unsafe_allow_html=True)

    with col_sub_actions:
        with st.popover("⚙️ Subject Options"):
            st.markdown("**Rename Subject**")
            edit_sub_name = st.text_input(
                "New name",
                value=selected_subject["name"],
                key=f"rename_sub_{selected_subject['id']}"
            )
            if st.button("✏️ Rename", key=f"btn_rename_sub_{selected_subject['id']}"):
                if edit_sub_name.strip() and edit_sub_name.strip() != selected_subject["name"]:
                    success = rename_subject(user_id, selected_subject["id"], edit_sub_name.strip())
                    if success:
                        st.success("Subject renamed!")
                        st.rerun()
                    else:
                        st.error("A subject with that name already exists.")

            st.markdown("---")
            st.markdown("**⚠️ Danger Zone**")
            st.caption("Deleting a subject removes ALL its chapters, topics, and progress.")
            if st.button("🗑️ Delete This Subject", type="primary",
                        key=f"btn_del_sub_{selected_subject['id']}"):
                delete_subject(user_id, selected_subject["id"])
                st.warning("Subject deleted!")
                st.rerun()

    # ── Add Chapter ──
    with st.expander(f"➕ Add Chapter to {selected_subject['name']}"):
        with st.form(f"add_chap_form_{selected_subject['id']}", clear_on_submit=True):
            chap_name = st.text_input(
                "Chapter Name",
                placeholder="e.g. Chapter 1: Real Numbers"
            )
            chap_submitted = st.form_submit_button("Add Chapter", use_container_width=True)
            if chap_submitted:
                if chap_name.strip():
                    add_chapter(user_id, selected_subject["id"], chap_name.strip())
                    st.success(f"✅ Chapter '{chap_name.strip()}' added!")
                    st.rerun()
                else:
                    st.error("Chapter name cannot be empty.")

    chapters = get_chapters_for_subject(user_id, selected_subject["id"])

    if not chapters:
        st.info("No chapters yet. Add your first chapter above!")
        return

    # ── Render Chapters & Topics ──
    for chap_idx, chap in enumerate(chapters):
        with st.expander(f"📌 {chap['name']}", expanded=False):
            # Chapter controls
            col_c_title, col_c_actions = st.columns([3, 1])
            with col_c_actions:
                with st.popover(f"Edit Chapter"):
                    new_c_name = st.text_input(
                        "Rename", value=chap["name"],
                        key=f"ren_c_{chap['id']}"
                    )
                    if st.button("Save", key=f"save_c_{chap['id']}"):
                        if new_c_name.strip():
                            rename_chapter(user_id, chap["id"], new_c_name.strip())
                            st.rerun()

                    st.markdown("---")

                    # Move buttons
                    move_col1, move_col2 = st.columns(2)
                    with move_col1:
                        if st.button("⬆️ Up", key=f"up_c_{chap['id']}",
                                    disabled=(chap_idx == 0)):
                            move_chapter(user_id, chap["id"], "up")
                            st.rerun()
                    with move_col2:
                        if st.button("⬇️ Down", key=f"down_c_{chap['id']}",
                                    disabled=(chap_idx == len(chapters) - 1)):
                            move_chapter(user_id, chap["id"], "down")
                            st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Delete Chapter", type="primary",
                                key=f"del_c_{chap['id']}"):
                        delete_chapter(user_id, chap["id"])
                        st.rerun()

            # Add Topic form
            with st.form(f"add_topic_form_{chap['id']}", clear_on_submit=True):
                col_t1, col_t2 = st.columns([3, 1])
                with col_t1:
                    top_name = st.text_input(
                        "New Topic",
                        placeholder="e.g. Introduction, Properties, Applications",
                        key=f"input_top_{chap['id']}"
                    )
                with col_t2:
                    st.write("")  # spacer
                    top_submitted = st.form_submit_button("➕ Add", use_container_width=True)
                if top_submitted and top_name.strip():
                    add_topic(user_id, chap["id"], top_name.strip())
                    st.success("Topic added!")
                    st.rerun()

            topics = get_topics_for_chapter(user_id, chap["id"])

            if not topics:
                st.caption("No topics in this chapter yet.")
                continue

            for topic in topics:
                _render_topic_card(user_id, topic)


def _render_topic_card(user_id: int, topic):
    """Render a single topic with status controls, understanding, flags, notes, and subtopics."""
    prog = get_progress(user_id, "topic", topic["id"])
    icon = STATUS_ICONS.get(prog["status"], "⚪")

    st.markdown(f"""
        <div class="topic-row">
            <span style="font-size: 0.95rem; color: #F8FAFC;">
                {icon} <strong>{topic['name']}</strong>
            </span>
        </div>
    """, unsafe_allow_html=True)

    # ── Status & Understanding row ──
    col_s1, col_s2, col_s3 = st.columns([2, 2, 2])

    with col_s1:
        new_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(prog["status"]) if prog["status"] in STATUS_OPTIONS else 0,
            key=f"status_{topic['id']}",
            label_visibility="collapsed"
        )

    with col_s2:
        understanding_val = st.selectbox(
            "Understanding",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: UNDERSTANDING_LABELS[x],
            index=max(0, min(4, prog["understanding"] - 1)),
            key=f"und_{topic['id']}",
            label_visibility="collapsed"
        )

    with col_s3:
        f1, f2, f3 = st.columns(3)
        with f1:
            is_imp = st.checkbox("⭐", value=bool(prog["is_important"]),
                                key=f"imp_{topic['id']}", help="Important")
        with f2:
            is_diff = st.checkbox("⚠️", value=bool(prog["is_difficult"]),
                                 key=f"diff_{topic['id']}", help="Difficult")
        with f3:
            is_prac = st.checkbox("🔄", value=bool(prog["needs_practice"]),
                                 key=f"prac_{topic['id']}", help="Needs Practice")

    # Notes
    notes = st.text_input(
        "Notes",
        value=prog.get("notes", ""),
        key=f"notes_{topic['id']}",
        placeholder="Quick notes or key points...",
        label_visibility="collapsed"
    )

    # Detect changes and auto-save
    changed = (
        new_status != prog["status"] or
        understanding_val != prog["understanding"] or
        notes != prog.get("notes", "") or
        int(is_imp) != prog["is_important"] or
        int(is_diff) != prog["is_difficult"] or
        int(is_prac) != prog["needs_practice"]
    )

    if changed:
        save_progress(
            user_id=user_id,
            item_type="topic",
            item_id=topic["id"],
            status=new_status,
            understanding=understanding_val,
            notes=notes,
            is_important=int(is_imp),
            is_difficult=int(is_diff),
            needs_practice=int(is_prac)
        )
        st.toast(f"💾 Saved '{topic['name']}'", icon="✅")
        st.rerun()

    # ── Subtopics ──
    subtopics = get_subtopics_for_topic(user_id, topic["id"])

    if subtopics:
        for sub in subtopics:
            sub_prog = get_progress(user_id, "subtopic", sub["id"])
            sub_c1, sub_c2, sub_c3, sub_c4 = st.columns([3, 2, 1, 1])
            with sub_c1:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;└ {sub['name']}")
            with sub_c2:
                sub_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(sub_prog["status"]) if sub_prog["status"] in STATUS_OPTIONS else 0,
                    key=f"sub_status_{sub['id']}",
                    label_visibility="collapsed"
                )
                if sub_status != sub_prog["status"]:
                    save_progress(user_id, "subtopic", sub["id"], status=sub_status,
                                understanding=sub_prog["understanding"])
                    st.rerun()
            with sub_c3:
                with st.popover("✏️", key=f"edit_subtop_{sub['id']}"):
                    new_sub_name = st.text_input("Rename", value=sub["name"],
                                                key=f"ren_subtop_{sub['id']}")
                    if st.button("Save", key=f"save_subtop_{sub['id']}"):
                        if new_sub_name.strip():
                            rename_subtopic(user_id, sub["id"], new_sub_name.strip())
                            st.rerun()
            with sub_c4:
                if st.button("❌", key=f"del_subtop_{sub['id']}", help="Delete subtopic"):
                    delete_subtopic(user_id, sub["id"])
                    st.rerun()

    # Add subtopic + Topic actions
    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        with st.popover("➕ Subtopic", key=f"pop_subtop_{topic['id']}"):
            new_subtop = st.text_input("Subtopic Name", key=f"input_subtop_{topic['id']}")
            if st.button("Save", key=f"btn_subtop_{topic['id']}"):
                if new_subtop.strip():
                    add_subtopic(user_id, topic["id"], new_subtop.strip())
                    st.rerun()
    with action_col2:
        with st.popover("⚙️ Topic", key=f"opts_topic_{topic['id']}"):
            ren_t = st.text_input("Rename Topic", value=topic["name"],
                                 key=f"ren_t_{topic['id']}")
            if st.button("✏️ Rename", key=f"save_t_{topic['id']}"):
                if ren_t.strip():
                    rename_topic(user_id, topic["id"], ren_t.strip())
                    st.rerun()
            st.markdown("---")
            if st.button("🗑️ Delete Topic", type="primary",
                        key=f"del_t_{topic['id']}"):
                delete_topic(user_id, topic["id"])
                st.rerun()

    st.markdown("---")
