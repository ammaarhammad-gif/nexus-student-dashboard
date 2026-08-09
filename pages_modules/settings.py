"""
settings.py — Application Settings and Academic Configuration.

Allows editing profile, changing board/class, selecting theme (Light, Dark, Default),
reloading official syllabus, managing exam terms, and data maintenance.
"""

import streamlit as st
import datetime
import io
import base64

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from models import (
    get_user_profile, save_user_profile, get_all_terms, add_term,
    update_term, delete_term, clear_all_terms, reset_all_data,
    get_user_theme, set_user_theme,
    get_user_wallpaper_config, set_user_wallpaper_config, clear_user_wallpaper_config
)
from preloaded_syllabi import preload_standard_syllabus, reload_and_replace_syllabus
from styles import render_header, WALLPAPER_PRESETS
from pages_modules.setup_wizard import CLASS_OPTIONS


def process_uploaded_wallpaper(uploaded_file, max_width: int = 1920, quality: int = 80):
    """Resizes and compresses an uploaded image into a high-performance JPEG data URL."""
    try:
        if HAS_PIL:
            image = Image.open(uploaded_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            if image.width > max_width:
                aspect = image.height / image.width
                new_height = int(max_width * aspect)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=quality, optimize=True)
            img_bytes = buffered.getvalue()
        else:
            uploaded_file.seek(0)
            img_bytes = uploaded_file.read()

        b64_str = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception:
        return None


def render_settings_page(user_id: int):
    user_theme = get_user_theme(user_id)
    render_header("⚙️ Application Settings", "Manage your profile, theme appearance, academic calendar, and syllabus.", theme=user_theme)

    profile = get_user_profile(user_id)

    # ── Section 1: User Profile & Curriculum ──
    st.subheader("👤 Student Profile & Curriculum")
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=profile.get("name", ""))
            curr_board_str = profile.get("board", "ICSE")
            
            # Detect primary board type
            primary_board = curr_board_str if curr_board_str in ["ICSE", "CBSE", "Other"] else "ICSE"
            
            new_board_type = st.selectbox(
                "Board / Curriculum",
                ["ICSE", "CBSE", "Other"],
                index=["ICSE", "CBSE", "Other"].index(primary_board) if primary_board in ["ICSE", "CBSE", "Other"] else 0
            )
            
            final_board = new_board_type

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

        # Detect if curriculum target was changed
        curriculum_changed = (final_board != curr_board_str or new_class_name != curr_class)
        auto_update_syllabus = True
        if curriculum_changed:
            st.info(f"💡 Switching from **{curr_board_str} {curr_class}** ➔ **{final_board} {new_class_name}**.")
            auto_update_syllabus = st.checkbox(
                f"🔄 Automatically replace subjects & topics with official {final_board} {new_class_name} curriculum",
                value=True
            )
            
        save_profile_btn = st.form_submit_button("💾 Save Profile Settings", use_container_width=True)
        if save_profile_btn:
            save_user_profile(user_id, new_name.strip(), new_academic_year.strip(), final_board, new_class_name)
            if curriculum_changed and auto_update_syllabus:
                with st.spinner(f"Loading official {final_board} {new_class_name} syllabus..."):
                    reload_and_replace_syllabus(user_id, final_board, new_class_name)
                st.success(f"✅ Saved profile and loaded official {final_board} {new_class_name} syllabus!")
            else:
                st.success("✅ Profile settings updated successfully!")
            st.rerun()

    # ── Section 2: Theme & Appearance + Wallpaper Customizer ──
    st.markdown("---")
    c_hdr1, c_hdr2 = st.columns([3, 2])
    with c_hdr1:
        st.subheader("🎨 Appearance, Themes & Wallpapers")
        st.caption("Personalize your study space with curated high-definition wallpapers, custom gallery uploads, and glassmorphism.")
    with c_hdr2:
        st.write("")
        if st.button("🖼️ Open Full Wallpaper Studio ➔", type="primary", use_container_width=True, key="settings_launch_studio_btn"):
            st.session_state["active_nav_radio"] = "🖼️ Wallpapers & Themes"
            st.rerun()

    theme_options = ["☀️ Light (Default)", "🌙 Dark", "💻 System Default"]
    current_theme = get_user_theme(user_id)
    
    if current_theme == "Dark":
        theme_index = 1
    elif current_theme == "Default":
        theme_index = 2
    else:
        theme_index = 0

    col_th1, col_th2 = st.columns([3, 1])
    with col_th1:
        selected_theme_label = st.radio(
            "Select Dashboard Theme:",
            theme_options,
            index=theme_index,
            horizontal=True,
            key="theme_radio_selector"
        )
    with col_th2:
        st.write("") # spacer
        if st.button("Apply Theme", use_container_width=True, type="primary", key="btn_apply_theme"):
            if "Dark" in selected_theme_label:
                new_th = "Dark"
            elif "System" in selected_theme_label:
                new_th = "Default"
            else:
                new_th = "Light"
            set_user_theme(user_id, new_th)
            st.session_state["theme_mode"] = new_th
            st.toast(f"✅ Theme set to {selected_theme_label}!", icon="🎨")
            st.rerun()

    # ── Wallpaper Customization Hub ──
    st.markdown("#### 🖼️ Dashboard Wallpaper & Background")
    wp_cfg = get_user_wallpaper_config(user_id)
    curr_mode = wp_cfg.get("mode", "none")
    curr_preset = wp_cfg.get("preset_id")
    curr_custom = wp_cfg.get("custom_url")
    curr_blur = wp_cfg.get("blur", 0)
    curr_opacity = wp_cfg.get("opacity", 0.82)

    # Status indicator
    if curr_mode == "preset":
        preset_name = next((p["name"] for p in WALLPAPER_PRESETS if p["id"] == curr_preset), curr_preset)
        st.info(f"Active Wallpaper: **{preset_name}**")
    elif curr_mode == "custom":
        st.info("Active Wallpaper: **Custom Image from Gallery / Device** 📸")
    else:
        st.caption("Active Wallpaper: *Default Solid Theme Background*")

    wp_tab1, wp_tab2, wp_tab3 = st.tabs([
        "🖼️ Curated Wallpapers (20 Options)",
        "📤 Upload Custom Wallpaper",
        "🚫 Solid Theme (No Wallpaper)"
    ])

    with wp_tab1:
        st.caption("Browse 20 curated 4K aesthetic wallpapers categorized for study focus and inspiration:")
        cat_filter = st.selectbox(
            "Filter Category",
            ["All Wallpapers (20)", "🌌 Space & Sci-Fi", "🏙️ Cyber & Neon", "🌿 Nature & Calm", "📚 Study & Vibes", "✨ Abstract"],
            key="wp_cat_filter"
        )
        filtered_presets = WALLPAPER_PRESETS if "All" in cat_filter else [p for p in WALLPAPER_PRESETS if p.get("category") == cat_filter]

        # Display in 4 columns grid
        cols_per_row = 4
        for i in range(0, len(filtered_presets), cols_per_row):
            row_items = filtered_presets[i:i+cols_per_row]
            cols = st.columns(len(row_items))
            for idx, p in enumerate(row_items):
                with cols[idx]:
                    is_active = (curr_mode == "preset" and curr_preset == p["id"])
                    border_style = "3px solid #38BDF8; box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);" if is_active else "1px solid rgba(255,255,255,0.15);"
                    
                    st.markdown(f"""
                        <div style="border-radius: 12px; overflow: hidden; border: {border_style}; margin-bottom: 8px; background: #1E293B;">
                            <img src="{p['thumb']}" style="width: 100%; height: 110px; object-fit: cover; display: block;" />
                            <div style="padding: 8px 10px; text-align: center;">
                                <div style="font-size: 0.82rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFFFFF;">{p['name']}</div>
                                <div style="font-size: 0.72rem; opacity: 0.75; color: #94A3B8;">{p.get('category', '')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    btn_label = "✅ Active" if is_active else "Set Wallpaper"
                    if st.button(btn_label, key=f"set_wp_{p['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                        op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                        set_user_wallpaper_config(user_id, mode="preset", preset_id=p["id"], blur=curr_blur, opacity=op_val)
                        set_user_theme(user_id, "Dark")
                        st.session_state["theme_mode"] = "Dark"
                        st.toast(f"✅ Applied {p['name']} in Dark Glassmorphism!", icon="🖼️")
                        st.rerun()

    with wp_tab2:
        st.caption("Upload any photo or aesthetic image from your gallery, mobile storage, or computer:")
        uploaded_wp = st.file_uploader(
            "Choose a wallpaper image",
            type=["png", "jpg", "jpeg", "webp"],
            key="custom_wp_uploader"
        )
        
        if uploaded_wp is not None:
            data_url = process_uploaded_wallpaper(uploaded_wp)
            if data_url:
                st.markdown("##### Preview:")
                st.image(uploaded_wp, use_container_width=True, caption="Live Preview of Uploaded Wallpaper")
                if st.button("✨ Apply Custom Wallpaper", type="primary", use_container_width=True, key="save_custom_wp_btn"):
                    op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                    set_user_wallpaper_config(user_id, mode="custom", custom_url=data_url, blur=curr_blur, opacity=op_val)
                    set_user_theme(user_id, "Dark")
                    st.session_state["theme_mode"] = "Dark"
                    st.toast("✅ Custom wallpaper applied in Dark Glassmorphism!", icon="📸")
                    st.rerun()
            else:
                st.error("Could not process image. Please try another JPG or PNG file.")
        elif curr_mode == "custom" and curr_custom:
            st.markdown("##### Currently Active Custom Wallpaper:")
            st.image(curr_custom, use_container_width=True, caption="Active Custom Wallpaper")
            if st.button("🗑️ Remove Custom Wallpaper", key="del_custom_wp_btn"):
                clear_user_wallpaper_config(user_id)
                st.toast("Removed custom wallpaper.", icon="🧹")
                st.rerun()

    with wp_tab3:
        st.caption("Prefer the distraction-free solid background theme without background photos?")
        if st.button("🚫 Remove Wallpaper & Reset to Solid Theme", type="primary", use_container_width=True, key="reset_solid_wp_btn"):
            clear_user_wallpaper_config(user_id)
            st.toast("Reset to solid theme background!", icon="✨")
            st.rerun()

    # ── Advanced Blur & Glassmorphism Adjustments ──
    if curr_mode != "none":
        with st.expander("🎛️ Wallpaper & Glassmorphism Fine-Tuning", expanded=False):
            c_sl1, c_sl2 = st.columns(2)
            with c_sl1:
                new_blur = st.slider(
                    "Background Image Blur (px)",
                    min_value=0,
                    max_value=14,
                    value=int(curr_blur),
                    help="Add soft blur to the wallpaper to make dashboard text and numbers pop with crystal clarity."
                )
            with c_sl2:
                new_opacity = st.slider(
                    "Card Contrast & Overlay Tint",
                    min_value=0.50,
                    max_value=0.95,
                    value=float(curr_opacity),
                    step=0.02,
                    help="Higher values give higher contrast for text; lower values make cards more transparent and glass-like."
                )
            if st.button("💾 Save Display Adjustments", key="save_wp_adjustments_btn", use_container_width=True):
                set_user_wallpaper_config(user_id, mode=curr_mode, preset_id=curr_preset, custom_url=curr_custom, blur=new_blur, opacity=new_opacity)
                st.toast("✅ Wallpaper visual adjustments saved!", icon="🎛️")
                st.rerun()


    # ── Section 3: Syllabus Switcher & Auto-Loader ──
    st.markdown("---")
    st.subheader("📚 Switch & Reload Official Board Syllabus")
    st.caption("Select any Board and Class below to instantly replace your current syllabus with the complete official subjects and topics.")
    
    col_rel_b, col_rel_c, col_rel_btn = st.columns([2, 2, 2])
    with col_rel_b:
        curr_b_val = profile.get("board", "ICSE")
        p_b_val = curr_b_val if curr_b_val in ["ICSE", "CBSE", "Other"] else "ICSE"
        switch_board = st.selectbox(
            "Target Board",
            ["ICSE", "CBSE", "Other"],
            index=["ICSE", "CBSE", "Other"].index(p_b_val) if p_b_val in ["ICSE", "CBSE", "Other"] else 0,
            key="switch_board_select"
        )
    with col_rel_c:
        curr_c_val = profile.get("class_name", "Class 10")
        c_idx_val = CLASS_OPTIONS.index(curr_c_val) if curr_c_val in CLASS_OPTIONS else 9
        switch_class = st.selectbox(
            "Target Class",
            CLASS_OPTIONS,
            index=c_idx_val,
            key="switch_class_select"
        )
    with col_rel_btn:
        st.write("")
        st.write("")
        if st.button("🔄 Replace & Load Syllabus", use_container_width=True, type="primary"):
            final_sw_board = switch_board
            with st.spinner(f"Loading complete {final_sw_board} {switch_class} curriculum..."):
                save_user_profile(user_id, profile.get("name", ""), profile.get("academic_year", ""), final_sw_board, switch_class)
                reload_and_replace_syllabus(user_id, final_sw_board, switch_class)
            st.success(f"✅ Successfully loaded {final_sw_board} {switch_class} syllabus with all subjects & topics!")
            st.rerun()


    # ── Section 4: Manage Exam Terms ──
    st.markdown("---")
    st.subheader("📅 Manage Exam Terms & Dates")
    st.caption("Keep your exam milestones updated. Check 'Already done' if an exam has concluded so countdowns start from your next active exam.")
    terms = get_all_terms(user_id)
    
    if terms:
        for term in terms:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
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
                t_done = st.checkbox(
                    "☑️ Already done",
                    value=bool(term.get("is_already_done", 0)),
                    key=f"t_done_{term['id']}",
                    help="Check if this exam term has passed"
                )
            with c4:
                st.write("") # Spacer
                if st.button("💾 Save", key=f"btn_update_t_{term['id']}"):
                    update_term(user_id, term["id"], t_name, t_date.strftime("%Y-%m-%d"), is_already_done=1 if t_done else 0)
                    st.toast("Term updated!", icon="✅")
                    st.rerun()
                if st.button("🗑️ Del", key=f"btn_del_t_{term['id']}", type="primary"):
                    delete_term(user_id, term["id"])
                    st.rerun()

    with st.expander("➕ Add New Exam Term"):
        with st.form("add_new_term_form", clear_on_submit=True):
            col_nt1, col_nt2 = st.columns(2)
            with col_nt1:
                new_t_name = st.text_input("Term Name", placeholder="e.g. Pre-Board Examination")
            with col_nt2:
                new_t_date = st.date_input("Exam Date", value=datetime.date.today() + datetime.timedelta(days=60))
            new_t_done = st.checkbox("☑️ Already done (Exam concluded)", value=False)
            if st.form_submit_button("Add Term", use_container_width=True):
                if new_t_name.strip():
                    add_term(user_id, new_t_name.strip(), new_t_date.strftime("%Y-%m-%d"), is_already_done=1 if new_t_done else 0)
                    st.success("Term added!")
                    st.rerun()

    # ── Section 5: Data Reset ──
    st.markdown("---")
    st.subheader("⚠️ Reset All Data")
    st.warning("Resetting will wipe all subjects, chapters, topics, study sessions, and progress permanently.")
    
    confirm_reset = st.checkbox("I understand that resetting will permanently delete all my dashboard data.")
    if st.button("🔴 Reset All Data", type="primary", disabled=not confirm_reset):
        reset_all_data(user_id)
        st.success("All data has been reset! Reloading...")
        st.rerun()

