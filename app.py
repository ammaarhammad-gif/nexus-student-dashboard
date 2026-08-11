import streamlit as st
import logging
from database import init_db
from models import (
    is_setup_complete, has_completed_guide, get_user_profile, get_user_theme, get_user_wallpaper_config,
    set_user_theme, set_user_wallpaper_config, clear_user_wallpaper_config
)
from styles import apply_custom_css, render_cinematic_welcome_banner, render_welcome_splash_screen, render_html, WALLPAPER_PRESETS





from pages_modules.setup_wizard import render_setup_wizard
from pages_modules.onboarding_guide import render_onboarding_guide
from pages_modules.dashboard import render_dashboard_page
from pages_modules.learn import render_learn_page
from pages_modules.planner import render_planner_page
from pages_modules.practice import render_practice_page
from pages_modules.review import render_review_page
from pages_modules.focus import render_focus_page
from pages_modules.ai_command_center import render_ai_command_center_page
from pages_modules.statistics import render_statistics_page
from pages_modules.search import render_search_page
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
active_theme = "Dark"
wp_url, wp_blur, wp_opacity, wp_preset_id = WALLPAPER_PRESETS[0]["url"], 0, 0.35, "cosmic_nebula"

if "user_id" in st.session_state:
    try:
        active_theme = get_user_theme(st.session_state["user_id"])
        st.session_state["theme_mode"] = active_theme
        wp_url, wp_blur, wp_opacity, wp_preset_id = get_resolved_wallpaper(st.session_state["user_id"])
    except Exception:
        active_theme = "Dark"
elif "theme_mode" in st.session_state:
    active_theme = st.session_state["theme_mode"]
    wp_url, wp_blur, wp_opacity, wp_preset_id = WALLPAPER_PRESETS[0]["url"], 0, 0.35, "cosmic_nebula"

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
    # Centered modern auth layout
    c_pad1, c_auth, c_pad2 = st.columns([1, 1.4, 1])
    
    with c_auth:
        st.markdown("""
            <div class="auth-hero-container">
                <div class="auth-brand-badge">⚡ NEXUS ECOSYSTEM • CLASS 1-10</div>
                <h1 class="auth-hero-title">Welcome to Nexus</h1>
                <p class="auth-hero-subtitle">Your intelligent companion for CBSE & ICSE curriculum tracking, smart timetables, and performance mastery.</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Sign In to Nexus", "✨ Create Free Account"])
        
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("<h3 style='margin: 0 0 14px 0; font-size: 1.2rem; color: #FFFFFF; font-family: Outfit, sans-serif;'>Sign In to Your Workspace</h3>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="e.g. ammaarakhtar_718").strip()
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                keep_logged_in = st.checkbox("🔒 Keep me logged in on this device (30 days)", value=True)
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("⚡ Enter Your Study Space", use_container_width=True, type="primary")
                if submitted:
                    if not username or not password:
                        st.error("Please enter both username and password.")
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
                            st.success("Welcome back! Loading your workspace...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Please try again.")
                            
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("<h3 style='margin: 0 0 14px 0; font-size: 1.2rem; color: #FFFFFF; font-family: Outfit, sans-serif;'>Create Your Student Profile</h3>", unsafe_allow_html=True)
                new_username = st.text_input("Choose Username", placeholder="e.g. ammaar_scholar").strip()
                new_password = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚀 Create Free Account & Get Started", use_container_width=True, type="primary")
                if submitted:
                    if not new_username or not new_password or not confirm_password:
                        st.error("Please fill in all required fields.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        from models import create_user
                        user_id = create_user(new_username, new_password)
                        if user_id:
                            st.session_state["user_id"] = user_id
                            st.session_state["username"] = new_username
                            st.session_state["show_welcome_splash"] = True
                            st.success("Account created successfully! Welcome aboard.")
                            st.rerun()
                        else:
                            st.error("Username is already taken. Please choose another username.")
        
        # Feature Pills Footer below Auth Box
        st.markdown("""
            <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-top: 24px;">
                <span class="auth-feature-pill">📚 Official ICSE & CBSE Syllabus</span>
                <span class="auth-feature-pill">📅 Intelligent Timetable</span>
                <span class="auth-feature-pill">🎨 20+ Bespoke 4K Themes</span>
            </div>
            <div style="text-align: center; margin-top: 18px; color: #64748B; font-size: 0.8rem;">
                Crafted with ❤️ by <strong>Ammaar Akhtar</strong> • Cloud Synced & Encrypted
            </div>
        """, unsafe_allow_html=True)

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

    # Check if full onboarding guide/tour is active or needed
    if st.session_state.get("show_onboarding_guide", False) or not has_completed_guide(user_id):
        render_onboarding_guide(user_id)
        return

    # User Profile & Theme Context
    profile = get_user_profile(user_id)
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    # ══════════════════════════════════════════════════════════════════════════
    # PRIMARY SIDEBAR NAVIGATION (10 Consolidated Modules)
    # ══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        card_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95))" if is_dark else "linear-gradient(135deg, #FFFFFF, #F1F5F9)"
        card_border = "rgba(56, 189, 248, 0.28)" if is_dark else "#CBD5E1"
        name_color = "#FFFFFF" if is_dark else "#0F172A"
        badge_bg = "rgba(56, 189, 248, 0.15)" if is_dark else "rgba(79, 70, 229, 0.1)"
        badge_color = "#38BDF8" if is_dark else "#4F46E5"
        badge_border = "rgba(56, 189, 248, 0.3)" if is_dark else "rgba(79, 70, 229, 0.2)"
        user_name = profile.get('name', 'Ammaar')
        initial = (user_name[0] if user_name else "A").upper()

        render_html(f"""
            <div style="padding: 6px 0 12px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                    <span style="font-size: 1.5rem; filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.6));">⚡</span>
                    <span style="font-family: 'Outfit', sans-serif; color: {'#38BDF8' if is_dark else '#4F46E5'}; font-size: 1.5rem; font-weight: 900; letter-spacing: -0.02em;">NEXUS</span>
                </div>
                <p style="font-family: 'Plus Jakarta Sans', sans-serif; color: {'#94A3B8' if is_dark else '#64748B'}; font-size: 0.78rem; font-weight: 500; margin: 0 0 10px 0;">Academic Command Center</p>
                
                <div style="background: {card_bg}; border: 1px solid {card_border}; padding: 8px 10px; border-radius: 12px; display: flex; align-items: center; gap: 10px; box-shadow: 0 4px 14px rgba(0,0,0,{'0.3' if is_dark else '0.04'});">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #0284C7, #6366F1); color: #FFFFFF; font-weight: 800; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 0 8px rgba(56, 189, 248, 0.35);">
                        {initial}
                    </div>
                    <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        <strong style="font-family: 'Outfit', sans-serif; color: {name_color}; font-size: 0.95rem; font-weight: 700; display: block; line-height: 1.1;">{user_name}</strong>
                        <span style="display: inline-block; background: {badge_bg}; color: {badge_color}; font-size: 0.72rem; font-weight: 600; padding: 1px 6px; border-radius: 8px; border: 1px solid {badge_border}; margin-top: 2px;">
                            {profile.get('class_name', 'Class 10')} • {profile.get('board', 'ICSE')}
                        </span>
                    </div>
                </div>
            </div>
        """)


        # ── Quick Global Search in Sidebar ──
        search_query = st.text_input("Global Search", placeholder="⌕ Search Nexus... (Ctrl + K)", key="global_search_input", label_visibility="collapsed")
        
        if search_query and len(search_query.strip()) >= 2:
            from models import global_nexus_search
            results = global_nexus_search(user_id, search_query)
            total_hits = sum(len(v) for v in results.values())
            if total_hits == 0:
                st.caption(f"No matches found for '{search_query}'")
            else:
                with st.expander(f"✨ Search Matches ({total_hits})", expanded=True):
                    for t in results.get("topics", [])[:2]:
                        st.markdown(f"📚 **{t['topic_name']}** ({t['subject_name']})")
                    for n in results.get("notes", [])[:2]:
                        st.markdown(f"📝 **{n['title']}**")
                    for f in results.get("formulas", [])[:2]:
                        st.markdown(f"📐 **{f['title']}**")
                    for m in results.get("mistakes", [])[:2]:
                        st.markdown(f"❌ **{m['question'][:24]}...**")

        st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
        
        # ── Primary Navigation (7 Core Modules) ──
        primary_pages = [
            "🏠 Dashboard",
            "📚 Learn",
            "🗓️ Planner",
            "🎯 Practice",
            "🧠 Review",
            "⏱️ Focus",
            "🤖 Nexus AI"
        ]

        # ── More Section (3 Utility Modules) ──
        more_pages = [
            "📊 Analytics",
            "🔍 Search",
            "⚙️ Settings"
        ]

        all_pages = primary_pages + more_pages

        # Normalize legacy or redirect page names
        page_aliases = {
            "📚 Syllabus Manager": "📚 Learn",
            "📝 Notes": "📚 Learn",
            "📐 Formula Vault": "📚 Learn",
            "🗓️ Study Planner": "🗓️ Planner",
            "🎯 Quiz Engine": "🎯 Practice",
            "💡 Active Recall": "🎯 Practice",
            "🧠 Revision Queue": "🧠 Review",
            "❌ Mistake Vault": "🎯 Practice",
            "⏱️ Focus Studio": "⏱️ Focus",
            "🧠 AI Command Center": "🤖 Nexus AI",
            "📊 Statistics": "📊 Analytics",
            "🔍 Global Search": "🔍 Search",
            "🖼️ Wallpapers & Themes": "⚙️ Settings"
        }

        curr_page = st.session_state.get("current_page", "🏠 Dashboard")
        curr_page = page_aliases.get(curr_page, curr_page)
        if curr_page not in all_pages:
            curr_page = all_pages[0]
        st.session_state["current_page"] = curr_page

        nav_epoch = st.session_state.get("nav_epoch", 0)
        is_in_more = curr_page in more_pages

        render_html("""
            <style>
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] input[type="radio"],
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] input[type="radio"] + div,
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] div:has(> input[type="radio"]),
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child:not(:has([data-testid="stMarkdownContainer"])),
            section[data-testid="stSidebar"] [data-testid="stRadio"] svg {
                display: none !important;
                opacity: 0 !important;
                width: 0 !important;
                height: 0 !important;
                max-width: 0 !important;
                max-height: 0 !important;
                min-width: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                visibility: hidden !important;
                pointer-events: none !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"],
            section[data-testid="stSidebar"] [data-testid="stRadio"] label {
                padding: 10px 14px !important;
                border-radius: 12px !important;
                margin-bottom: 4px !important;
                transition: all 0.18s ease !important;
                cursor: pointer !important;
                border: 1px solid transparent !important;
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
                background: transparent !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
                background: rgba(255, 255, 255, 0.06) !important;
                transform: translateX(4px) !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),
            section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"][aria-checked="true"] {
                background: rgba(56, 189, 248, 0.14) !important;
                border: 1px solid rgba(56, 189, 248, 0.38) !important;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.22) !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"],
            section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
            section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                font-size: 0.94rem !important;
                font-weight: 600 !important;
                color: var(--nexus-text-title, #F8FAFC) !important;
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
            section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p {
                color: #38BDF8 !important;
                font-weight: 700 !important;
            }
            </style>
        """)

        # Primary Navigation Radio (7 core modules)
        primary_index = primary_pages.index(curr_page) if not is_in_more else None

        primary_selection = st.radio(
            "Primary Navigation",
            primary_pages,
            index=primary_index if primary_index is not None else None,
            key=f"nav_primary_{nav_epoch}",
            label_visibility="collapsed"
        )

        # ── "More" Divider ──
        divider_color = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
        label_color = "#64748B" if is_dark else "#94A3B8"
        render_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 12px 0 6px 0;">
                <div style="flex: 1; height: 1px; background: {divider_color};"></div>
                <span style="font-family: 'Outfit', sans-serif; font-size: 0.72rem; font-weight: 700; color: {label_color}; text-transform: uppercase; letter-spacing: 0.1em; white-space: nowrap;">More</span>
                <div style="flex: 1; height: 1px; background: {divider_color};"></div>
            </div>
        """)

        # More Navigation Radio (3 utility modules)
        more_index = more_pages.index(curr_page) if is_in_more else None

        more_selection = st.radio(
            "More Navigation",
            more_pages,
            index=more_index if more_index is not None else None,
            key=f"nav_more_{nav_epoch}",
            label_visibility="collapsed"
        )

        # Determine active page: whichever radio was last clicked
        if primary_selection and primary_selection != st.session_state.get("_prev_primary"):
            page = primary_selection
        elif more_selection and more_selection != st.session_state.get("_prev_more"):
            page = more_selection
        else:
            page = curr_page

        st.session_state["_prev_primary"] = primary_selection
        st.session_state["_prev_more"] = more_selection
        st.session_state["current_page"] = page

        render_html("<div style='margin-top: 12px;'></div>")

        footer_border = "rgba(255,255,255,0.08)" if is_dark else "#E2E8F0"
        
        col_sync, col_logout = st.columns([1.4, 1])
        with col_sync:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 5px; color: {'#10B981' if is_dark else '#059669'}; font-size: 0.76rem; font-weight: 600; padding-top: 6px;">
                    <span style="font-size: 0.85rem;">☁</span> All data synced
                </div>
            """, unsafe_allow_html=True)
        with col_logout:
            if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
                clear_session_param()
                for key in ["user_id", "username", "current_page", "nav_epoch", "authenticated"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        footer_name_color = "#FFFFFF" if is_dark else "#0F172A"
        st.markdown(f"""
            <div style="margin-top: 10px; text-align: center; border-top: 1px solid {footer_border}; padding-top: 8px;">
                <p style="color: #64748B; font-size: 0.75rem; margin: 0; font-weight: 500;">Crafted with ❤️ by <strong style="color: {footer_name_color}; font-family: 'Outfit', sans-serif;">Ammaar Akhtar</strong></p>
            </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE ROUTER (10 Clean Modules)
    # ══════════════════════════════════════════════════════════════════════════
    if page == "🏠 Dashboard":
        render_dashboard_page(user_id)
    elif page == "📚 Learn":
        render_learn_page(user_id)
    elif page == "🗓️ Planner":
        render_planner_page(user_id)
    elif page == "🎯 Practice":
        render_practice_page(user_id)
    elif page == "🧠 Review":
        render_review_page(user_id)
    elif page == "⏱️ Focus":
        render_focus_page(user_id)
    elif page == "🤖 Nexus AI":
        render_ai_command_center_page(user_id)
    elif page == "📊 Analytics":
        render_statistics_page(user_id)
    elif page == "🔍 Search":
        render_search_page(user_id)
    elif page == "⚙️ Settings":
        render_settings_page(user_id)


if __name__ == "__main__":
    main()
