"""
settings.py — Application Settings and Academic Configuration.

Allows editing profile, changing board/class, reloading official syllabus,
managing exam terms, and data maintenance.
"""

import streamlit as st
import datetime
from models import (
    get_user_profile, save_user_profile, get_all_terms, add_term,
    update_term, delete_term, clear_all_terms, reset_all_data
)
from preloaded_syllabi import preload_standard_syllabus
from styles import render_header
from pages_modules.setup_wizard import STATE_BOARDS, CLASS_OPTIONS


def render_settings_page(user_id: int):
    render_header("⚙️ Application Settings", "Manage your profile, academic calendar, syllabus reload, and preferences.")

    profile = get_user_profile(user_id)

    # ── Section 1: User Profile & Curriculum ──
    st.subheader("👤 Student Profile & Curriculum")
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=profile.get("name", ""))
            curr_board_str = profile.get("board", "ICSE")
            
            # Detect primary board type
            primary_board = "State Board" if curr_board_str.startswith("State Board") else (curr_board_str if curr_board_str in ["ICSE", "CBSE", "Other"] else "ICSE")
            
            new_board_type = st.selectbox(
                "Board / Curriculum",
                ["ICSE", "CBSE", "State Board", "Other"],
                index=["ICSE", "CBSE", "State Board", "Other"].index(primary_board) if primary_board in ["ICSE", "CBSE", "State Board", "Other"] else 0
            )
            
            final_board = new_board_type
            if new_board_type == "State Board":
                selected_sb = st.selectbox(
                    "Select State Board",
                    STATE_BOARDS,
                    key="settings_state_board_specific"
                )
                acronym = selected_sb.split(" — ")[0]
                final_board = f"State Board ({acronym})"

        with col2:
            current_year = datetime.date.today().year
            new_academic_year = st.text_input(
                "Academic Session",
                value=profile.get("academic_year", f"{current_year}-{current_year + 1}")
            )
            
            curr_class = profile.get("class_name", "Class 10")
            class_idx = CLASS_OPTIONS.index(curr_class) if curr_class in CLASS_OPTIONS else 9
            new_class_name = st.selectbox(
                "Class / Grade",
                CLASS_OPTIONS,
                index=class_idx
            )
            
        save_profile_btn = st.form_submit_button("💾 Save Profile Settings", use_container_width=True)
        if save_profile_btn:
            save_user_profile(user_id, new_name.strip(), new_academic_year.strip(), final_board, new_class_name)
            st.success("✅ Profile settings updated successfully!")
            st.rerun()

    # ── Section 2: Syllabus Auto-Loader ──
    st.markdown("---")
    st.subheader("📚 Reload Official Board Syllabus")
    st.caption("Changed your class or board? Click below to instantly load the official syllabus into your account.")
    
    col_rel1, col_rel2 = st.columns([3, 1])
    with col_rel1:
        st.markdown(f"Current Target: **{profile.get('board', 'ICSE')} • {profile.get('class_name', 'Class 10')}**")
    with col_rel2:
        if st.button("⚡ Reload Full Syllabus", use_container_width=True, type="primary"):
            board = profile.get("board", "ICSE")
            cls = profile.get("class_name", "Class 10")
            with st.spinner(f"Loading official {board} {cls} syllabus..."):
                preload_standard_syllabus(user_id, board, cls)
            st.success(f"✅ Successfully loaded {board} {cls} syllabus!")
            st.rerun()

    # ── Section 3: Manage Exam Terms ──
    st.markdown("---")
    st.subheader("📅 Manage Exam Terms & Dates")
    terms = get_all_terms(user_id)
    
    if terms:
        for term in terms:
            c1, c2, c3 = st.columns([3, 3, 1])
            with c1:
                t_name = st.text_input("Term Name", value=term["name"], key=f"t_name_{term['id']}")
            with c2:
                curr_date = datetime.date.today()
                try:
                    curr_date = datetime.datetime.strptime(term["exam_date"], "%Y-%m-%d").date()
                except Exception:
                    pass
                t_date = st.date_input("Exam Date", value=curr_date, key=f"t_date_{term['id']}")
            with c3:
                st.write("") # Spacer
                if st.button("💾 Save", key=f"btn_update_t_{term['id']}"):
                    update_term(user_id, term["id"], t_name, t_date.strftime("%Y-%m-%d"))
                    st.toast("Term updated!", icon="✅")
                    st.rerun()
                if st.button("🗑️ Del", key=f"btn_del_t_{term['id']}", type="primary"):
                    delete_term(user_id, term["id"])
                    st.rerun()

    with st.expander("➕ Add New Exam Term"):
        with st.form("add_new_term_form", clear_on_submit=True):
            new_t_name = st.text_input("Term Name", placeholder="e.g. Pre-Board Examination")
            new_t_date = st.date_input("Exam Date", value=datetime.date.today() + datetime.timedelta(days=60))
            if st.form_submit_button("Add Term", use_container_width=True):
                if new_t_name.strip():
                    add_term(user_id, new_t_name.strip(), new_t_date.strftime("%Y-%m-%d"))
                    st.success("Term added!")
                    st.rerun()

    # ── Section 4: Data Reset ──
    st.markdown("---")
    st.subheader("⚠️ Reset All Data")
    st.warning("Resetting will wipe all subjects, chapters, topics, study sessions, and progress permanently.")
    
    confirm_reset = st.checkbox("I understand that resetting will permanently delete all my dashboard data.")
    if st.button("🔴 Reset All Data", type="primary", disabled=not confirm_reset):
        reset_all_data(user_id)
        st.success("All data has been reset! Reloading...")
        st.rerun()
