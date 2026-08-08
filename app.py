import streamlit as st
import logging
from database import init_db
from models import is_setup_complete, get_user_profile
from styles import apply_custom_css
from pages_modules.setup_wizard import render_setup_wizard
from pages_modules.dashboard import render_dashboard_page
from pages_modules.syllabus import render_syllabus_page
from pages_modules.statistics import render_statistics_page
from pages_modules.planner import render_planner_page
from pages_modules.settings import render_settings_page

# Page Configuration
st.set_page_config(
    page_title="Nexus Student Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Futuristic Theme Styling First
apply_custom_css()

# Ensure Database and Schema are Initialized
db_ok = False
try:
    db_ok = init_db()
except Exception as e:
    logging.error(f"Database initialization failed: {e}")

def render_db_config_instructions():
    st.markdown("<div class='setup-hero'><h1>⚡ NEXUS</h1><p>Syllabus & Exam Manager</p></div>", unsafe_allow_html=True)
    st.warning("🔌 PostgreSQL Database Credentials Required")
    st.markdown("""
    To deploy and run **Nexus Student Dashboard**, you must connect it to a cloud PostgreSQL database.
    
    ### How to configure locally:
    1. Create a free PostgreSQL database on **[Supabase](https://supabase.com)** or **[Neon](https://neon.tech)**.
    2. Create a folder named `.streamlit` at the root of this project.
    3. Inside `.streamlit/`, create a file named `secrets.toml` with your database credentials:
       ```toml
       # .streamlit/secrets.toml
       [postgres]
       url = "postgresql://postgres:your_password@your_db_host:5432/postgres"
       ```
    4. Restart your Streamlit server or refresh this page.
    
    ### How to configure in Streamlit Community Cloud:
    Add the same `[postgres]` configuration section to the **Secrets** settings in your Streamlit Cloud Dashboard.
    """)

def render_auth_page():
    st.markdown("<div class='setup-hero'><h1>⚡ NEXUS</h1><p>Syllabus & Exam Manager</p></div>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])
    
    with tab_login:
        st.subheader("Welcome back!")
        with st.form("login_form"):
            username = st.text_input("Username").strip()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    from models import verify_user
                    user = verify_user(username, password)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["username"] = user["username"]
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
    with tab_signup:
        st.subheader("Create a new account")
        with st.form("signup_form"):
            new_username = st.text_input("Username").strip()
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            if submitted:
                if not new_username or not new_password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    from models import create_user
                    user_id = create_user(new_username, new_password)
                    if user_id:
                        st.session_state["user_id"] = user_id
                        st.session_state["username"] = new_username
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Username is already taken.")

def main():
    if not db_ok:
        render_db_config_instructions()
        return

    # Check User Authentication
    if "user_id" not in st.session_state:
        render_auth_page()
        return

    user_id = st.session_state["user_id"]

    # Check if first-time onboarding setup is needed
    if not is_setup_complete(user_id):
        render_setup_wizard(user_id)
        return

    profile = get_user_profile(user_id)

    # Sidebar Navigation Menu
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <h2 style="color: #6366F1; margin-bottom: 2px;">⚡ NEXUS</h2>
                <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">Syllabus & Exam Manager</p>
                <div style="margin-top: 10px; background: rgba(99, 102, 241, 0.1); padding: 8px 12px; border-radius: 8px;">
                    <strong style="color: #F8FAFC;">{profile.get('name', 'Student')}</strong><br>
                    <span style="color: #CBD5E1; font-size: 0.8rem;">{profile.get('class_name', '')} • {profile.get('board', '')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        page = st.radio(
            "Go to page",
            [
                "🏠 Dashboard",
                "📚 Syllabus Manager",
                "📊 Statistics",
                "🗓️ Study Planner",
                "⚙️ Settings"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            del st.session_state["user_id"]
            del st.session_state["username"]
            st.rerun()
            
        st.markdown("---")
        st.caption("🌐 Cloud PostgreSQL Storage Enabled")
        st.caption("v1.1.0 • Active")

    # Page Router
    if page == "🏠 Dashboard":
        render_dashboard_page(user_id)
    elif page == "📚 Syllabus Manager":
        render_syllabus_page(user_id)
    elif page == "📊 Statistics":
        render_statistics_page(user_id)
    elif page == "🗓️ Study Planner":
        render_planner_page(user_id)
    elif page == "⚙️ Settings":
        render_settings_page(user_id)

if __name__ == "__main__":
    main()
