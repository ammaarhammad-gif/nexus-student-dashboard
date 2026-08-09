"""
syllabus.py — Syllabus Management and Progress Tracking page.

Allows viewing auto-loaded official syllabi, 1-click ticking off completed topics,
adjusting understanding levels, adding custom notes, and managing chapters/topics.
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
    get_subject_hierarchy
)
from preloaded_syllabi import preload_standard_syllabus, reload_and_replace_syllabus
from styles import render_header


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


def render_syllabus_page(user_id: int):
    profile = get_user_profile(user_id)
    board = profile.get("board", "ICSE")
    class_name = profile.get("class_name", "Class 10")
    user_theme = get_user_theme(user_id)

    render_header(
        "📚 Syllabus Manager",
        f"Official {board} ({class_name}) Syllabus • Tick off topics as you finish studying them.",
        theme=user_theme
    )

    tab_manage, tab_csv = st.tabs(["📚 My Syllabus", "📥 Import Custom CSV"])

    with tab_manage:
        _render_manage_syllabus_tab(user_id, board, class_name)

    with tab_csv:
        _render_csv_import_tab(user_id)


def _render_csv_import_tab(user_id: int):
    """CSV import tab: upload, preview, and import syllabus from a CSV file."""
    st.subheader("📥 Import Syllabus from CSV")
    st.markdown("""
        Upload a CSV file with three columns: **Subject**, **Chapter**, **Topic**.  
        Existing subjects/chapters/topics are automatically skipped (no duplicates).
    """)

    with st.expander("📋 Example CSV Format", expanded=False):
        st.code(
            "Subject,Chapter,Topic\n"
            "Mathematics,Chapter 1: Commercial Mathematics,Goods and Services Tax (GST)\n"
            "Mathematics,Chapter 1: Commercial Mathematics,Banking (Recurring Deposit)\n"
            "Physics,Chapter 1: Force Work and Energy,Turning Effect of Force\n"
            "Physics,Chapter 1: Force Work and Energy,Center of Gravity",
            language="csv"
        )

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"], key="csv_syllabus_upload")

    if uploaded is not None:
        try:
            content = uploaded.getvalue().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            raw_fields = [f.strip() if f else "" for f in (reader.fieldnames or [])]
            
            # Case-insensitive column resolution
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
            st.warning("The CSV file has no valid rows after filtering empty values.")
            return

        st.success(f"✅ Found **{len(rows)}** valid rows in the CSV.")
        
        # Display preview table
        preview_rows = rows[:15]
        st.table(preview_rows)
        if len(rows) > 15:
            st.caption(f"Showing first 15 of {len(rows)} rows.")

        # Summary preview
        unique_subjects = len(set(r["Subject"] for r in rows))
        unique_chapters = len(set((r["Subject"], r["Chapter"]) for r in rows))
        st.markdown(f"**Preview:** {unique_subjects} subjects, {unique_chapters} chapters, {len(rows)} topics")

        if st.button("🚀 Import Syllabus", use_container_width=True, type="primary"):
            with st.spinner("Importing syllabus..."):
                result = import_syllabus_from_csv(user_id, rows)
            st.success(
                f"✅ Import complete! "
                f"Created **{result['subjects']}** subjects, "
                f"**{result['chapters']}** chapters, "
                f"**{result['topics']}** topics. "
                f"Skipped **{result['skipped']}** duplicates/empty rows."
            )
            st.rerun()


def _render_manage_syllabus_tab(user_id: int, board: str, class_name: str):
    """Main syllabus management tab with instant single-query hierarchy and 1-click topic completion."""
    subjects = get_all_subjects(user_id)

    # ── Auto-load official syllabus if user has no subjects ──
    if not subjects:
        with st.spinner(f"⚡ Loading official {board} ({class_name}) syllabus for you..."):
            loaded = preload_standard_syllabus(user_id, board, class_name)
            if loaded:
                st.toast(f"✅ Official {board} ({class_name}) syllabus loaded!", icon="🚀")
                st.rerun()

    # ── Subject Action Toolbar ──
    col_tb1, col_tb2 = st.columns([3, 1])
    with col_tb1:
        st.caption(f"Showing syllabus for **{board} {class_name}**. Click the checkbox on any topic to mark it done!")
    with col_tb2:
        with st.popover("⚙️ Syllabus Options"):
            st.markdown("**➕ Add Custom Subject**")
            with st.form("add_subject_form", clear_on_submit=True):
                new_sub_name = st.text_input("Subject Name", placeholder="e.g. Economics, Art")
                sub_color = st.color_picker("Subject Color", value="#6366F1")
                if st.form_submit_button("Create Subject", use_container_width=True):
                    if new_sub_name.strip():
                        res = add_subject(user_id, new_sub_name.strip(), sub_color)
                        if res:
                            st.success(f"Created '{new_sub_name}'!")
                            st.rerun()
                        else:
                            st.error("Subject already exists.")
            
            st.markdown("---")
            if st.button(f"🔄 Reload Full {board} ({class_name}) Syllabus", use_container_width=True):
                with st.spinner("Replacing syllabus with official curriculum..."):
                    reload_and_replace_syllabus(user_id, board, class_name)
                st.success("Official syllabus reloaded!")
                st.rerun()


    if not subjects:
        st.info("📝 Loading your syllabus... Please refresh if it does not load automatically.")
        return

    # ── Subject Selection Tabs/Dropdown ──
    subject_names = [s["name"] for s in subjects]
    selected_idx = st.selectbox(
        "Select Subject to View & Track:",
        range(len(subject_names)),
        format_func=lambda i: f"📖 {subject_names[i]}",
        key="subject_selector"
    )
    selected_subject = subjects[selected_idx]

    # ── Fetch entire subject hierarchy in ONE fast indexed query ──
    chapters = get_subject_hierarchy(user_id, selected_subject["id"])
    
    # Calculate subject completion
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
                    <h2 style="margin: 0; font-size: 1.6rem;">{selected_subject['name']}</h2>
                    <span style="font-size: 0.9rem;">{len(chapters)} Chapters • {total_subject_topics} Topics</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.8rem; font-weight: 700; color: {selected_subject['color']};">{sub_pct}%</span>
                    <span style="font-size: 0.85rem; display: block;">{completed_subject_topics}/{total_subject_topics} Done</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Add Chapter Form ──
    with st.expander(f"➕ Add Custom Chapter to {selected_subject['name']}", expanded=False):
        with st.form(f"add_chap_form_{selected_subject['id']}", clear_on_submit=True):
            chap_name = st.text_input("Chapter Name", placeholder="e.g. Chapter 7: Probability")
            if st.form_submit_button("Add Chapter", use_container_width=True):
                if chap_name.strip():
                    add_chapter(user_id, selected_subject["id"], chap_name.strip())
                    st.success(f"Added '{chap_name.strip()}'!")
                    st.rerun()

    if not chapters:
        st.info("No chapters in this subject yet. Click above to add a chapter or reload official syllabus.")
        return

    # ── Render Chapters & Topics ──
    for chap_idx, chap in enumerate(chapters):
        topics = chap["topics"]
        
        # Calculate chapter completion
        ch_done = sum(1 for t in topics if t["status"] in ["Completed", "Revision Done"])
        ch_total = len(topics)
        ch_badge = f"{ch_done}/{ch_total} Done" if ch_total > 0 else "0 Topics"
        is_all_done = (ch_done == ch_total and ch_total > 0)

        icon_prefix = "✅" if is_all_done else "📌"

        with st.expander(f"{icon_prefix} {chap['name']}  ({ch_badge})", expanded=(chap_idx == 0)):
            # Chapter controls in popover
            col_ch_info, col_ch_act = st.columns([4, 1])
            with col_ch_act:
                with st.popover("⚙️ Chapter"):
                    new_c_name = st.text_input("Rename Chapter", value=chap["name"], key=f"ren_c_{chap['id']}")
                    if st.button("Save Name", key=f"save_c_{chap['id']}"):
                        if new_c_name.strip():
                            rename_chapter(user_id, chap["id"], new_c_name.strip())
                            st.rerun()

                    st.markdown("---")
                    mv1, mv2 = st.columns(2)
                    with mv1:
                        if st.button("⬆️ Up", key=f"up_c_{chap['id']}", disabled=(chap_idx == 0)):
                            move_chapter(user_id, chap["id"], "up")
                            st.rerun()
                    with mv2:
                        if st.button("⬇️ Down", key=f"down_c_{chap['id']}", disabled=(chap_idx == len(chapters) - 1)):
                            move_chapter(user_id, chap["id"], "down")
                            st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Delete Chapter", type="primary", key=f"del_c_{chap['id']}"):
                        delete_chapter(user_id, chap["id"])
                        st.rerun()

            # Add Topic to Chapter Form
            with st.form(f"add_topic_form_{chap['id']}", clear_on_submit=True):
                col_t1, col_t2 = st.columns([4, 1])
                with col_t1:
                    top_name = st.text_input(
                        "Add Topic",
                        placeholder="e.g. Formulae, Important Concepts, Derivations",
                        key=f"input_top_{chap['id']}",
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
                _render_topic_card(user_id, topic)


def _render_topic_card(user_id: int, topic: dict):
    """Render a single topic with instant 1-click ticking and rich controls."""
    is_completed = (topic["status"] in ["Completed", "Revision Done"])

    # ── Top Row: 1-Click Checkbox + Topic Name + Status Badge ──
    col_check, col_details_btn = st.columns([5, 1])

    with col_check:
        # Instant 1-Click Completion Toggle
        checked = st.checkbox(
            label=f"**{topic['name']}**",
            value=is_completed,
            key=f"quick_tick_{topic['id']}",
            help="Click to tick off this topic as completed!"
        )

    with col_details_btn:
        with st.popover("⚙️ Edit"):
            st.markdown(f"**Options for: {topic['name']}**")
            
            # Status Selector
            new_status_select = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(topic["status"]) if topic["status"] in STATUS_OPTIONS else 0,
                key=f"status_sel_{topic['id']}"
            )

            # Understanding Rating
            new_understanding = st.selectbox(
                "Understanding Level",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: UNDERSTANDING_LABELS[x],
                index=max(0, min(4, topic["understanding"] - 1)),
                key=f"und_sel_{topic['id']}"
            )

            # Flags
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                is_imp = st.checkbox("⭐ Important", value=bool(topic["is_important"]), key=f"imp_{topic['id']}")
            with col_f2:
                is_diff = st.checkbox("⚠️ Difficult", value=bool(topic["is_difficult"]), key=f"diff_{topic['id']}")
            with col_f3:
                is_prac = st.checkbox("🔄 Practice", value=bool(topic["needs_practice"]), key=f"prac_{topic['id']}")

            # Notes
            edit_notes = st.text_input(
                "Notes / Key Formulae",
                value=topic.get("notes", "") or "",
                key=f"notes_input_{topic['id']}"
            )

            if st.button("💾 Save Changes", key=f"save_details_{topic['id']}", use_container_width=True):
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
            ren_t = st.text_input("Rename Topic", value=topic["name"], key=f"ren_t_{topic['id']}")
            if st.button("✏️ Rename", key=f"btn_ren_{topic['id']}"):
                if ren_t.strip():
                    rename_topic(user_id, topic["id"], ren_t.strip())
                    st.rerun()

            if st.button("🗑️ Delete Topic", type="primary", key=f"del_t_{topic['id']}"):
                delete_topic(user_id, topic["id"])
                st.rerun()

    # Detect 1-click tick change
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

    # ── Display Badges and Notes if present ──
    flags_html = []
    if topic.get("is_important"):
        flags_html.append("<span style='color: #FDE047; font-size: 0.78rem;'>⭐ Important</span>")
    if topic.get("is_difficult"):
        flags_html.append("<span style='color: #F87171; font-size: 0.78rem;'>⚠️ Difficult</span>")
    if topic.get("needs_practice"):
        flags_html.append("<span style='color: #60A5FA; font-size: 0.78rem;'>🔄 Needs Practice</span>")
    if topic.get("notes"):
        flags_html.append(f"<span style='font-size: 0.78rem; font-style: italic;'>📝 {topic['notes']}</span>")

    if flags_html:
        st.markdown(f"<div style='margin-left: 28px; margin-bottom: 6px; display: flex; gap: 12px; flex-wrap: wrap;'>{' • '.join(flags_html)}</div>", unsafe_allow_html=True)

    # ── Subtopics ──
    subtopics = topic.get("subtopics", [])
    if subtopics:
        for sub in subtopics:
            sub_done = (sub["status"] == "Completed")
            
            sub_c1, sub_c2 = st.columns([5, 1])
            with sub_c1:
                sub_checked = st.checkbox(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;└ {sub['name']}",
                    value=sub_done,
                    key=f"sub_tick_{sub['id']}"
                )
                if sub_checked != sub_done:
                    new_sub_stat = "Completed" if sub_checked else "Not Started"
                    save_progress(user_id, "subtopic", sub["id"], status=new_sub_stat,
                                understanding=sub["understanding"])
                    if sub_checked:
                        schedule_revisions(user_id, "subtopic", sub["id"])
                    st.rerun()
            with sub_c2:
                if st.button("❌", key=f"del_sub_{sub['id']}", help="Delete subtopic"):
                    delete_subtopic(user_id, sub["id"])
                    st.rerun()

    # Add Subtopic trigger
    with st.popover(f"➕ Add Subtopic", key=f"add_sub_pop_{topic['id']}"):
        new_subtop = st.text_input("Subtopic Name", key=f"inp_sub_{topic['id']}")
        if st.button("Save Subtopic", key=f"save_sub_{topic['id']}"):
            if new_subtop.strip():
                add_subtopic(user_id, topic["id"], new_subtop.strip())
                st.rerun()

    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

