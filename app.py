import streamlit as st
import logging
from database import init_db
from models import is_setup_complete, get_user_profile, get_user_theme
from styles import apply_custom_css
from pages_modules.setup_wizard import render_setup_wizard
from pages_modules.dashboard import render_dashboard_page
from pages_modules.syllabus import render_syllabus_page
from pages_modules.statistics import render_statistics_page
from pages_modules.planner import render_planner_page
from pages_modules.settings import render_settings_page
from auth_utils import (
    create_session_token, verify_session_token,
    set_session_param, get_session_param, clear_session_param
)

# Page Configuration
st.set_page_config(
    page_title="Nexus Student Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Theme Styling (Defaults to Light for all users)
active_theme = "Light"
if "user_id" in st.session_state:
    try:
        active_theme = get_user_theme(st.session_state["user_id"])
    except Exception:
        active_theme = "Light"

apply_custom_css(active_theme)

# Google Site Verification for Search Engine Indexing (Injected into top-level <head>)
import streamlit.components.v1 as components
components.html("""
    <script>
        (function() {
            try {
                var meta = window.top.document.createElement('meta');
                meta.name = "google-site-verification";
                meta.content = "ArkovzIbKfH_-GW96FInyqF9VGOXvqFV_GVIP1mIYMw";
                window.top.document.getElementsByTagName('head')[0].appendChild(meta);
            } catch(e) { console.log(e); }
        })();
    </script>
""", height=0)

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
            keep_logged_in = st.checkbox("🔒 Keep me logged in", value=False)
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
                        if keep_logged_in:
                            token = create_session_token(user["id"], user["username"])
                            set_session_param(token)
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
        # Try to restore session from query param token
        token = get_session_param()
        if token:
            payload = verify_session_token(token)
            if payload:
                st.session_state["user_id"] = payload["uid"]
                st.session_state["username"] = payload["usr"]
            else:
                # Token invalid or expired, clear it
                clear_session_param()

    if "user_id" not in st.session_state:
        render_auth_page()
        return

    user_id = st.session_state["user_id"]

    # Check if first-time onboarding setup is needed
    if not is_setup_complete(user_id):
        render_setup_wizard(user_id)
        return

    profile = get_user_profile(user_id)
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # Sidebar Navigation Menu
    with st.sidebar:
        card_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95))" if is_dark else "linear-gradient(135deg, #FFFFFF, #F1F5F9)"
        card_border = "rgba(56, 189, 248, 0.35)" if is_dark else "#CBD5E1"
        name_color = "#FFFFFF" if is_dark else "#0F172A"
        badge_bg = "rgba(56, 189, 248, 0.2)" if is_dark else "rgba(79, 70, 229, 0.1)"
        badge_color = "#38BDF8" if is_dark else "#4F46E5"
        badge_border = "rgba(56, 189, 248, 0.3)" if is_dark else "rgba(79, 70, 229, 0.2)"

        st.markdown(f"""
            <div style="text-align: center; padding: 10px 0 16px 0;">
                <h2 style="font-family: 'Outfit', sans-serif; color: {'#38BDF8' if is_dark else '#4F46E5'}; font-size: 2rem; font-weight: 800; margin-bottom: 2px; letter-spacing: -0.02em;">⚡ NEXUS</h2>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; color: {'#94A3B8' if is_dark else '#64748B'}; font-size: 0.95rem; font-weight: 500; margin: 0;">Syllabus & Exam Manager</p>
                <div style="margin-top: 14px; background: {card_bg}; border: 1px solid {card_border}; padding: 12px 14px; border-radius: 14px; box-shadow: 0 4px 16px rgba(0,0,0,{'0.3' if is_dark else '0.04'});">
                    <strong style="font-family: 'Outfit', sans-serif; color: {name_color}; font-size: 1.25rem; font-weight: 700; display: block; margin-bottom: 3px;">{profile.get('name', 'Student')}</strong>
                    <span style="display: inline-block; background: {badge_bg}; color: {badge_color}; font-size: 0.8rem; font-weight: 600; padding: 2px 10px; border-radius: 12px; border: 1px solid {badge_border};">
                        {profile.get('class_name', 'Class 10')} • {profile.get('board', 'ICSE')}
                    </span>
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
            clear_session_param()
            for key in ["user_id", "username"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            
        st.markdown("""
            <div style="margin-top: 18px; text-align: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 14px;">
                <p style="color: #64748B; font-size: 0.85rem; margin: 0; font-weight: 500;">Crafted with ❤️ by</p>
                <h4 style="color: #F8FAFC; font-size: 1.1rem; font-weight: 700; margin: 2px 0 6px 0; font-family: 'Outfit', sans-serif;">Ammaar Akhtar</h4>
                <span style="display: inline-block; color: #38BDF8; font-size: 0.78rem; font-weight: 600; background: rgba(56, 189, 248, 0.1); padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2);">
                    🌐 Cloud Sync Active • v1.2.0
                </span>
            </div>
        """, unsafe_allow_html=True)

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
