import streamlit as st
import logging
from database import init_db
from models import (
    is_setup_complete, get_user_profile, get_user_theme, get_user_wallpaper_config,
    set_user_theme, set_user_wallpaper_config, clear_user_wallpaper_config
)
from styles import apply_custom_css, render_cinematic_welcome_banner, render_welcome_splash_screen, WALLPAPER_PRESETS




from pages_modules.setup_wizard import render_setup_wizard
from pages_modules.dashboard import render_dashboard_page
from pages_modules.syllabus import render_syllabus_page
from pages_modules.statistics import render_statistics_page
from pages_modules.planner import render_planner_page
from pages_modules.wallpapers import render_wallpapers_page
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

def get_resolved_wallpaper(user_id=None):
    """Helper to retrieve resolved wallpaper URL, blur, opacity, and preset_id for a user."""
    if not user_id:
        return None, 0, 0.30, None
    try:
        wp_cfg = get_user_wallpaper_config(user_id)
        mode = wp_cfg.get("mode", "none")
        blur = wp_cfg.get("blur", 0)
        opacity = wp_cfg.get("opacity", 0.30)
        preset_id = wp_cfg.get("preset_id", "")
        if mode == "custom":
            return wp_cfg.get("custom_url"), blur, opacity, "custom"
        elif mode == "preset":
            for p in WALLPAPER_PRESETS:
                if p["id"] == preset_id:
                    return p["url"], blur, opacity, preset_id
        return None, 0, 0.30, None
    except Exception:
        return None, 0, 0.30, None

# Apply Theme Styling & Wallpaper (Syncs instantly with session state and DB)
active_theme = "Light"
wp_url, wp_blur, wp_opacity, wp_preset_id = None, 0, 0.30, None

if "user_id" in st.session_state:
    try:
        active_theme = get_user_theme(st.session_state["user_id"])
        st.session_state["theme_mode"] = active_theme
        wp_url, wp_blur, wp_opacity, wp_preset_id = get_resolved_wallpaper(st.session_state["user_id"])
    except Exception:
        active_theme = "Light"
elif "theme_mode" in st.session_state:
    active_theme = st.session_state["theme_mode"]

apply_custom_css(active_theme, wallpaper_url=wp_url, wallpaper_blur=wp_blur, overlay_opacity=wp_opacity, preset_id=wp_preset_id)



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
    render_cinematic_welcome_banner(user_name="Scholar", class_name="Classes 1 to 10", board="ICSE & CBSE", theme="Light")
    
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
                        st.session_state["show_welcome_splash"] = True
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
                        st.session_state["show_welcome_splash"] = True
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
    st.session_state["theme_mode"] = user_theme
    wp_url, wp_blur, wp_opacity, wp_preset_id = get_resolved_wallpaper(user_id)
    apply_custom_css(user_theme, wallpaper_url=wp_url, wallpaper_blur=wp_blur, overlay_opacity=wp_opacity, preset_id=wp_preset_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # ── Fullscreen Welcome Splash Screen on Login / Signup / Setup ──
    if st.session_state.get("show_welcome_splash"):
        user_name = profile.get("name") or st.session_state.get("username", "Student")
        class_name = profile.get("class_name", "Class 10")
        board = profile.get("board", "CBSE")
        
        st.balloons()
        render_welcome_splash_screen(user_name, class_name, board, theme=user_theme)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🚀 Continue to Dashboard", type="primary", use_container_width=True, key="enter_dashboard_btn"):
                st.session_state["show_welcome_splash"] = False
                st.rerun()
        return

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
        page_options = [
            "🏠 Dashboard",
            "📚 Syllabus Manager",
            "📊 Statistics",
            "🗓️ Study Planner",
            "🖼️ Wallpapers & Themes",
            "⚙️ Settings"
        ]

        # Handle programmatic navigation requests
        if "main_nav_target" in st.session_state:
            target = st.session_state.pop("main_nav_target")
            if target in page_options:
                st.session_state["active_nav_radio"] = target

        current_nav_index = 0
        if "active_nav_radio" in st.session_state and st.session_state["active_nav_radio"] in page_options:
            current_nav_index = page_options.index(st.session_state["active_nav_radio"])

        page = st.radio(
            "Go to page",
            page_options,
            index=current_nav_index,
            key="active_nav_radio",
            label_visibility="collapsed"
        )
        
        # ── Quick Wallpaper & Theme Switcher in Sidebar ──
        st.markdown("---")
        with st.expander("🖼️ Quick Wallpaper & Theme", expanded=False):
            wp_cfg = get_user_wallpaper_config(user_id)
            curr_mode = wp_cfg.get("mode", "none")
            curr_preset = wp_cfg.get("preset_id")
            
            # Theme fast switch
            c_th1, c_th2 = st.columns(2)
            with c_th1:
                if st.button("☀️ Light", use_container_width=True, type="primary" if not is_dark else "secondary", key="sb_light_btn"):
                    set_user_theme(user_id, "Light")
                    st.session_state["theme_mode"] = "Light"
                    st.rerun()
            with c_th2:
                if st.button("🌙 Dark", use_container_width=True, type="primary" if is_dark else "secondary", key="sb_dark_btn"):
                    set_user_theme(user_id, "Dark")
                    st.session_state["theme_mode"] = "Dark"
                    st.rerun()
            
            # Quick preset select
            quick_options = ["Solid (No Wallpaper)"] + [p["name"] for p in WALLPAPER_PRESETS[:8]]
            curr_selection_idx = 0
            if curr_mode == "preset":
                for i, p in enumerate(WALLPAPER_PRESETS[:8]):
                    if p["id"] == curr_preset:
                        curr_selection_idx = i + 1
                        break
            
            chosen_wp_label = st.selectbox(
                "Quick Wallpaper:",
                quick_options,
                index=curr_selection_idx,
                key="sb_quick_wp_select"
            )
            
            if st.button("✨ Apply Quick Wallpaper", use_container_width=True, key="sb_apply_quick_wp_btn"):
                if chosen_wp_label == "Solid (No Wallpaper)":
                    clear_user_wallpaper_config(user_id)
                    st.toast("Reset to solid theme!", icon="✨")
                else:
                    target_preset = next((p for p in WALLPAPER_PRESETS if p["name"] == chosen_wp_label), None)
                    if target_preset:
                        set_user_wallpaper_config(user_id, mode="preset", preset_id=target_preset["id"], blur=wp_cfg.get("blur", 0), opacity=0.30)
                        set_user_theme(user_id, "Dark")
                        st.session_state["theme_mode"] = "Dark"
                        st.toast(f"Applied {target_preset['name']} in Dark Glassmorphism!", icon="🖼️")
                st.rerun()

            if st.button("🎨 Open Full Wallpaper Studio ➔", use_container_width=True, key="sb_open_studio_btn"):
                st.session_state["active_nav_radio"] = "🖼️ Wallpapers & Themes"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            clear_session_param()
            for key in ["user_id", "username", "active_nav_radio"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            
        footer_border = "rgba(255,255,255,0.08)" if is_dark else "#E2E8F0"
        footer_name_color = "#FFFFFF" if is_dark else "#0F172A"
        st.markdown(f"""
            <div style="margin-top: 18px; text-align: center; border-top: 1px solid {footer_border}; padding-top: 14px;">
                <p style="color: #64748B; font-size: 0.85rem; margin: 0; font-weight: 500;">Crafted with ❤️ by</p>
                <h4 style="color: {footer_name_color}; font-size: 1.1rem; font-weight: 700; margin: 2px 0 6px 0; font-family: 'Outfit', sans-serif;">Ammaar Akhtar</h4>
                <span style="display: inline-block; color: {'#38BDF8' if is_dark else '#4F46E5'}; font-size: 0.78rem; font-weight: 600; background: {'rgba(56, 189, 248, 0.1)' if is_dark else 'rgba(79, 70, 229, 0.08)'}; padding: 3px 10px; border-radius: 12px; border: 1px solid {'rgba(56, 189, 248, 0.2)' if is_dark else 'rgba(79, 70, 229, 0.15)'};">
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
    elif page == "🖼️ Wallpapers & Themes":
        render_wallpapers_page(user_id)
    elif page == "⚙️ Settings":
        render_settings_page(user_id)

if __name__ == "__main__":
    main()
