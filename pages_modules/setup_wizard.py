"""
setup_wizard.py — First-time onboarding setup page.

Collects: Name, Academic Year, Board, Class, and Exam Terms.
Shown only once; all values can be edited later in Settings.
"""

import streamlit as st
import datetime
from models import save_user_profile, add_term, clear_all_terms
from styles import render_header

STATE_BOARDS = [
    "UPMSP — Uttar Pradesh Madhyamik Shiksha Parishad",
    "BSEB — Bihar School Examination Board",
    "MPBSE — Madhya Pradesh Board of Secondary Education",
    "MSBSHSE — Maharashtra State Board of Secondary and Higher Secondary Education",
    "GSHSEB — Gujarat Secondary and Higher Secondary Education Board",
    "TNBSE — Tamil Nadu State Board of School Examination",
    "KSEEB — Karnataka School Examination and Assessment Board",
    "BIEAP — Board of Intermediate Education, Andhra Pradesh",
    "TSBIE — Telangana State Board of Intermediate Education",
    "WBBSE — West Bengal Board of Secondary Education",
    "AHSEC — Assam Higher Secondary Education Council",
    "HPBOSE — Himachal Pradesh Board of School Education",
    "JKBOSE — Jammu and Kashmir State Board of School Education",
    "CHSE — Council of Higher Secondary Education, Odisha",
    "PSEB — Punjab School Education Board",
    "RBSE — Rajasthan Board of Secondary Education",
    "CGBSE — Chhattisgarh Board of Secondary Education",
    "UBSE — Uttarakhand Board of School Education",
    "GBSHSE — Goa Board of Secondary and Higher Secondary Education",
    "Other State Board"
]

CLASS_OPTIONS = [
    "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
    "Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
    "Class 11", "Class 12", "College / University", "Other"
]


def render_setup_wizard(user_id: int):
    # Hero Section
    st.markdown("""
        <div class="setup-hero">
            <h1>⚡ NEXUS</h1>
            <p>Your Personal Syllabus & Exam Dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <p style="color: #CBD5E1; font-size: 1.05rem;">
                Welcome! Let's set up your profile in under a minute.<br>
                Your study progress is <strong>securely saved in the cloud</strong>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.info("💡 Complete this setup once. You can customize everything later in **Settings**.")

    # ── Step 1: Profile ──
    st.markdown("### 1️⃣ About You")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Your Name *", placeholder="e.g. Arjun, Priya, Alex", key="setup_user_name")
        board_type = st.selectbox("Board / Curriculum", ["CBSE", "ICSE", "State Board", "Other"], key="setup_board_type")
        
        final_board = board_type
        if board_type == "State Board":
            selected_sb = st.selectbox(
                "Select State Board *",
                STATE_BOARDS,
                key="setup_state_board_specific"
            )
            acronym = selected_sb.split(" — ")[0]
            final_board = f"State Board ({acronym})"

    with col2:
        current_year = datetime.date.today().year
        academic_year = st.text_input(
            "Academic Year",
            value=f"{current_year}-{current_year + 1}",
            key="setup_academic_year"
        )
        class_name = st.selectbox(
            "Class / Grade *",
            CLASS_OPTIONS,
            index=9,  # Default to Class 10
            key="setup_class_name"
        )

    st.markdown("---")

    # ── Step 2: Terms ──
    st.markdown("### 2️⃣ Exam Terms")
    st.caption("How many major exams or terms does your school/college have?")

    num_terms = st.radio(
        "Select number of terms/exams:",
        options=[1, 2, 3, 4, 5, 6],
        index=2,  # Defaults to 3 terms!
        horizontal=True,
        key="setup_num_terms_radio"
    )

    default_name_map = {
        1: ["Final Exam"],
        2: ["Mid-Term Exam", "Final Exam"],
        3: ["First Term / Unit Test", "Mid-Term Exam", "Final Exam"],
        4: ["First Term / Unit 1", "Mid-Term / Term 2", "Pre-Board / Term 3", "Final Exam"],
        5: ["Term 1", "Term 2", "Term 3", "Term 4", "Final Exam"],
        6: ["Term 1", "Term 2", "Term 3", "Term 4", "Term 5", "Final Exam"]
    }
    default_names = default_name_map.get(num_terms, [f"Term {i+1}" for i in range(num_terms)])

    st.markdown(f"#### 📅 Configure all **{num_terms}** Exam Terms:")

    term_data = []
    
    for i in range(num_terms):
        default_title = default_names[i] if i < len(default_names) else f"Term {i + 1}"
        default_date = datetime.date.today() + datetime.timedelta(days=75 * (i + 1))

        st.markdown(f"**Term {i + 1}:**")
        col_t1, col_t2 = st.columns([3, 2])

        with col_t1:
            t_name = st.text_input(
                f"Term {i + 1} Name",
                value=default_title,
                key=f"setup_t_name_{num_terms}_{i}"
            )
        with col_t2:
            t_date = st.date_input(
                f"Term {i + 1} Exam Date",
                value=default_date,
                key=f"setup_t_date_{num_terms}_{i}"
            )

        term_data.append((t_name, t_date.strftime("%Y-%m-%d")))

    st.markdown("---")

    submitted = st.button(
        "🚀 Complete Setup & Start Studying",
        type="primary",
        use_container_width=True,
        key="setup_submit_button"
    )

    if submitted:
        # Validation
        errors = []
        if not name.strip():
            errors.append("Please enter your name.")

        if errors:
            for err in errors:
                st.error(err)
            return

        # Save profile
        save_user_profile(
            user_id=user_id,
            name=name.strip(),
            academic_year=academic_year.strip(),
            board=final_board,
            class_name=class_name
        )

        # Save terms
        clear_all_terms(user_id=user_id)
        for idx, (t_name, t_date_str) in enumerate(term_data):
            if t_name.strip():
                add_term(user_id=user_id, name=t_name.strip(), exam_date=t_date_str, display_order=idx + 1)

        st.success("✅ Setup complete! Loading your dashboard...")
        st.rerun()
