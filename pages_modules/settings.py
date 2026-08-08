import streamlit as st
import datetime
from models import get_user_profile, save_user_profile, get_all_terms, add_term, update_term, delete_term, clear_all_terms, reset_all_data
from styles import render_header
from pages_modules.setup_wizard import STATE_BOARDS

def render_settings_page(user_id: int):
    render_header("⚙️ Application Settings", "Manage your profile, academic calendar, database, and system configurations.")

    profile = get_user_profile(user_id)

    st.subheader("👤 User Profile")
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name", value=profile.get("name", ""))
            curr_board_str = profile.get("board", "CBSE")
            
            # Detect primary board type
            primary_board = "State Board" if curr_board_str.startswith("State Board") else (curr_board_str if curr_board_str in ["CBSE", "ICSE", "Other"] else "CBSE")
            
            new_board_type = st.selectbox("Board / Curriculum", ["CBSE", "ICSE", "State Board", "Other"],
                                         index=["CBSE", "ICSE", "State Board", "Other"].index(primary_board))
            
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
            new_academic_year = st.text_input("Academic Year", value=profile.get("academic_year", ""))
            new_class_name = st.text_input("Class", value=profile.get("class_name", ""))
            
        save_profile_btn = st.form_submit_button("Save Profile Settings")
        if save_profile_btn:
            save_user_profile(user_id, new_name, new_academic_year, final_board, new_class_name)
            st.success("Profile settings updated successfully!")
            st.rerun()

    st.markdown("---")

    st.subheader("📅 Manage Exam Terms")
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
                if st.button("Save", key=f"btn_update_t_{term['id']}"):
                    update_term(user_id, term["id"], t_name, t_date.strftime("%Y-%m-%d"))
                    st.toast("Term updated!")
                    st.rerun()
                if st.button("Delete", key=f"btn_del_t_{term['id']}", type="primary"):
                    delete_term(user_id, term["id"])
                    st.rerun()

    with st.expander("➕ Add New Term"):
        with st.form("add_new_term_form", clear_on_submit=True):
            new_t_name = st.text_input("Term Name", placeholder="e.g. Mid-Term Exam")
            new_t_date = st.date_input("Exam Date", value=datetime.date.today() + datetime.timedelta(days=60))
            if st.form_submit_button("Add Term"):
                if new_t_name.strip():
                    add_term(user_id, new_t_name.strip(), new_t_date.strftime("%Y-%m-%d"))
                    st.success("Term added!")
                    st.rerun()

    st.markdown("---")
    st.subheader("⚠️ Reset All Data")
    st.warning("Resetting will wipe all subjects, chapters, topics, progress, and terms permanently. This action cannot be undone.")
    
    confirm_reset = st.checkbox("I understand that resetting will permanently delete all my data.")
    if st.button("🔴 Reset All Data", type="primary", disabled=not confirm_reset):
        reset_all_data(user_id)
        st.success("All data has been reset!")
        st.rerun()
