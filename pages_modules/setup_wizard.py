"""
setup_wizard.py — First-time onboarding setup page.

Collects: Name, Class (1 to 10), Board (ICSE, CBSE, State Board), and Academic Year (auto 2026-2027).
Automatically pre-loads the full official syllabus so students don't need to type anything!
"""

import streamlit as st
import datetime
from models import save_user_profile, add_term, clear_all_terms
from preloaded_syllabi import preload_standard_syllabus
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
    "Class 11", "Class 12"
]


def render_setup_wizard(user_id: int):
    # Hero Section
    st.markdown("""
        <div class="setup-hero">
            <h1>⚡ NEXUS</h1>
            <p style="color: #38BDF8; font-size: 1.25rem; font-weight: 600;">Your Personal Syllabus & Exam Dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <p style="color: #E2E8F0; font-size: 1.05rem;">
                Welcome! Let's configure your profile in seconds.<br>
                Your complete official syllabus will be <strong>automatically preloaded for you</strong>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Step 1: Personal Details & Class/Board Selection ──
    st.markdown("""
        <div class="nexus-card" style="border-left: 4px solid #38BDF8;">
            <h3 style="color: #F8FAFC; margin-top: 0;">🎓 1. Select Your Class & Curriculum</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Pick your grade and board — Nexus will auto-generate your full syllabus!</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "👤 Your Name *",
            placeholder="e.g. Arjun, Priya, Alex",
            key="setup_user_name"
        )
        
        class_name = st.selectbox(
            "🏫 Select Your Class / Grade *",
            CLASS_OPTIONS,
            index=9,  # Default to Class 10
            key="setup_class_name"
        )

    with col2:
        board_type = st.selectbox(
            "📜 Select Your Board / Curriculum *",
            ["ICSE", "CBSE", "State Board", "Other"],
            index=0,  # Default to ICSE
            key="setup_board_type"
        )

        final_board = board_type
        if board_type == "State Board":
            selected_sb = st.selectbox(
                "Select State Board *",
                STATE_BOARDS,
                key="setup_state_board_specific"
            )
            acronym = selected_sb.split(" — ")[0]
            final_board = f"State Board ({acronym})"

        current_year = datetime.date.today().year
        academic_year = st.text_input(
            "📅 Academic Session",
            value=f"{current_year}-{current_year + 1}",
            key="setup_academic_year"
        )

    # ── Step 2: Exam Schedule ──
    st.markdown("---")
    st.markdown("""
        <div class="nexus-card" style="border-left: 4px solid #A855F7;">
            <h3 style="color: #F8FAFC; margin-top: 0;">📅 2. Exam Terms & Milestones</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">We've set up smart exam dates for your academic year. You can customize them anytime.</p>
        </div>
    """, unsafe_allow_html=True)

    col_t_pref1, col_t_pref2 = st.columns([1, 2])
    with col_t_pref1:
        num_terms = st.radio(
            "Number of Terms / Exams:",
            options=[1, 2, 3, 4],
            index=2,  # Defaults to 3 terms
            horizontal=True,
            key="setup_num_terms_radio"
        )

    default_name_map = {
        1: ["Final Board / Annual Exam"],
        2: ["Mid-Term Exam", "Final Board Exam"],
        3: ["Unit Test / Term 1", "Mid-Term / Pre-Board", "Final Board Exam"],
        4: ["Unit Test 1", "Mid-Term / Half Yearly", "Pre-Board Exam", "Final Board Exam"]
    }
    default_names = default_name_map.get(num_terms, [f"Term {i+1}" for i in range(num_terms)])

    term_data = []
    cols = st.columns(num_terms)
    
    for i in range(num_terms):
        default_title = default_names[i] if i < len(default_names) else f"Term {i + 1}"
        default_date = datetime.date.today() + datetime.timedelta(days=70 * (i + 1))

        with cols[i]:
            t_name = st.text_input(
                f"Term {i + 1} Name",
                value=default_title,
                key=f"setup_t_name_{num_terms}_{i}"
            )
            t_date = st.date_input(
                f"Exam Date",
                value=default_date,
                key=f"setup_t_date_{num_terms}_{i}"
            )
            term_data.append((t_name, t_date.strftime("%Y-%m-%d")))

    st.markdown("---")

    # ── Auto-Loaded Syllabus Preview Banner ──
    st.info(f"✨ When you click continue, the complete **{final_board} ({class_name})** syllabus with all subjects, chapters, and topics will be automatically generated. You only need to tick off topics as you study!")

    submitted = st.button(
        f"🚀 Complete Setup & Auto-Load {class_name} {final_board} Syllabus",
        type="primary",
        use_container_width=True,
        key="setup_submit_button"
    )

    if submitted:
        # Validation
        if not name.strip():
            st.error("Please enter your name to proceed.")
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

        # Pre-load official CBSE/ICSE syllabus automatically
        with st.spinner(f"⚡ Loading official {final_board} ({class_name}) syllabus into your dashboard..."):
            preload_standard_syllabus(user_id=user_id, board=final_board, class_name=class_name)

        st.success("✅ Setup complete & official syllabus loaded! Loading your dashboard...")
        st.rerun()
