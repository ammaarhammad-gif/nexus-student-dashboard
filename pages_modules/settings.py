"""
settings.py — Nexus Unified Settings & Customization Module.

Consolidates:
1. 👤 Profile & Curriculum (Board, Class, Academic Session, Name, Syllabus reload)
2. 🗓️ Exam Terms (Term names, dates, concluded status, countdown configurations)
3. 🎨 Appearance (20 Curated 4K Presets, custom wallpaper upload, solid theme, blur intensity, dark overlay, light/dark switch)
4. 📦 Data Export (Master Anki TSV, Universal CSV, Academic Vector PDF)
5. ⚠️ Danger Zone (Reset all progress & database records)
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
    update_term, delete_term, reset_all_data,
    get_user_theme, set_user_theme,
    get_user_wallpaper_config, set_user_wallpaper_config, clear_user_wallpaper_config
)
from preloaded_syllabi import reload_and_replace_syllabus
from styles import render_top_header_bar, render_header, render_breadcrumbs, WALLPAPER_PRESETS, render_empty_state, render_html
from pages_modules.setup_wizard import CLASS_OPTIONS
from anki_export import export_all_to_anki
from pdf_generator import generate_weekly_progress_pdf


MAX_WALLPAPER_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def process_uploaded_wallpaper(uploaded_file, max_width: int = 1920, quality: int = 80):
    """
    Safely validates, bounds, resizes and compresses an uploaded wallpaper image.
    Enforces a 5MB size limit and PIL decompression bomb protections.
    """
    if uploaded_file is None:
        return None

    try:
        # 1. Enforce file size limit
        file_size = getattr(uploaded_file, "size", 0)
        if file_size > MAX_WALLPAPER_SIZE_BYTES:
            st.error("Uploaded image exceeds the 5MB file size limit. Please choose a smaller image.")
            return None

        if HAS_PIL:
            # Prevent DecompressionBomb attacks
            Image.MAX_IMAGE_PIXELS = 10_000_000

            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            
            # Validate format strictly
            if image.format not in ("JPEG", "PNG", "WEBP", "JPG"):
                st.error("Invalid image format. Only JPG, PNG, and WebP images are allowed.")
                return None

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
            if len(img_bytes) > MAX_WALLPAPER_SIZE_BYTES:
                return None

        b64_str = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception as e:
        st.error("Unable to process the uploaded image. Please ensure it is a valid, uncorrupted image file.")
        return None


def render_settings_page(user_id: int):
    render_top_header_bar(

        user_id,
        "⚙️ Settings",
        "Academic profile, exam terms, visual appearance studio, and data backups.",
        ["NEXUS", "Settings"]
    )

    tab_profile, tab_exams, tab_appearance, tab_export, tab_danger = st.tabs([
        "👤 Academic Profile",
        "🗓️ Exam Terms",
        "🎨 Appearance Studio",
        "📦 Backups & Export",
        "⚠️ Danger Zone"
    ])


    with tab_profile:
        _render_profile_tab(user_id)

    with tab_exams:
        _render_exams_tab(user_id)

    with tab_appearance:
        _render_appearance_tab(user_id)

    with tab_export:
        _render_export_tab(user_id)

    with tab_danger:
        _render_danger_tab(user_id)


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 1: PROFILE & CURRICULUM
# ══════════════════════════════════════════════════════════════════════════

def _render_profile_tab(user_id: int):
    profile = get_user_profile(user_id)
    st.subheader("👤 Student Profile & Curriculum")

    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=profile.get("name", ""))
            curr_board_str = profile.get("board", "CBSE")
            primary_board = curr_board_str if curr_board_str in ["CBSE", "ICSE", "Other"] else "CBSE"

            new_board_type = st.selectbox(
                "Board / Curriculum",
                ["CBSE", "ICSE", "Other"],
                index=["CBSE", "ICSE", "Other"].index(primary_board)
            )

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

        curriculum_changed = (new_board_type != curr_board_str or new_class_name != curr_class)
        auto_update_syllabus = True
        if curriculum_changed:
            st.info(f"💡 Switching curriculum from **{curr_board_str} {curr_class}** ➔ **{new_board_type} {new_class_name}**.")
            auto_update_syllabus = st.checkbox(
                f"🔄 Automatically replace subjects & topics with official {new_board_type} {new_class_name} syllabus",
                value=True
            )

        if st.form_submit_button("💾 Save Profile Settings", use_container_width=True, type="primary"):
            save_user_profile(user_id, new_name.strip(), new_academic_year.strip(), new_board_type, new_class_name)
            if curriculum_changed and auto_update_syllabus:
                with st.spinner(f"Loading official {new_board_type} {new_class_name} syllabus..."):
                    reload_and_replace_syllabus(user_id, new_board_type, new_class_name)
                st.success(f"✅ Saved profile and loaded official {new_board_type} {new_class_name} syllabus!")
            else:
                st.success("✅ Profile settings updated successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader("📖 Nexus Product Tour & Command Center Guide")
    st.markdown("Need a quick refresher on how all 10 modules, spaced repetition, Feynman active recall, and focus timers operate together?")
    if st.button("🚀 Replay Interactive Product Tour & Guide", type="secondary", use_container_width=True, key="replay_guide_btn"):
        st.session_state["show_onboarding_guide"] = True
        st.session_state["guide_step"] = 0
        st.rerun()

    st.markdown("---")
    st.subheader("🔄 Quick Reload Official Curriculum")
    st.caption("Need to reset your syllabus back to the standard official curriculum structure?")
    if st.button(f"⚡ Reload Official {profile.get('board', 'CBSE')} ({profile.get('class_name', 'Class 10')}) Curriculum", use_container_width=True):
        with st.spinner("Reloading official syllabus..."):
            reload_and_replace_syllabus(user_id, profile.get("board", "CBSE"), profile.get("class_name", "Class 10"))
        st.success("Official curriculum reloaded successfully!")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 2: EXAM TERMS & CALENDAR
# ══════════════════════════════════════════════════════════════════════════

def _render_exams_tab(user_id: int):
    st.subheader("📅 Manage Exam Terms & Countdowns")
    st.caption("Define upcoming exam terms. When an exam concludes, check 'Already done' so countdown clocks automatically focus on your next milestone.")

    terms = get_all_terms(user_id)
    if terms:
        for term in terms:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                t_name = st.text_input("Term Name", value=term["name"], key=f"sett_t_name_{term['id']}")
            with c2:
                curr_date = datetime.date.today()
                try:
                    curr_date = datetime.datetime.strptime(term["exam_date"], "%Y-%m-%d").date()
                except Exception:
                    pass
                t_date = st.date_input("Exam Date", value=curr_date, key=f"sett_t_date_{term['id']}")
            with c3:
                st.write("")
                t_done = st.checkbox(
                    "☑️ Concluded",
                    value=bool(term.get("is_already_done", 0)),
                    key=f"sett_t_done_{term['id']}",
                    help="Check if this exam term has passed"
                )
            with c4:
                st.write("")
                if st.button("💾", key=f"sett_save_t_{term['id']}", help="Save"):
                    update_term(user_id, term["id"], t_name, t_date.strftime("%Y-%m-%d"), is_already_done=1 if t_done else 0)
                    st.toast("Term updated!", icon="✅")
                    st.rerun()
                if st.button("🗑️", key=f"sett_del_t_{term['id']}", help="Delete", type="primary"):
                    delete_term(user_id, term["id"])
                    st.rerun()

    with st.expander("➕ Add New Exam Term", expanded=(not terms)):
        with st.form("sett_add_term_form", clear_on_submit=True):
            col_nt1, col_nt2 = st.columns(2)
            with col_nt1:
                new_t_name = st.text_input("Term Name", placeholder="e.g. Pre-Board 1, Final CBSE Board Exam")
            with col_nt2:
                new_t_date = st.date_input("Exam Date", value=datetime.date.today() + datetime.timedelta(days=60))
            new_t_done = st.checkbox("☑️ Already done (Exam concluded)", value=False)
            if st.form_submit_button("Add Exam Term", use_container_width=True, type="primary"):
                if new_t_name.strip():
                    add_term(user_id, new_t_name.strip(), new_t_date.strftime("%Y-%m-%d"), is_already_done=1 if new_t_done else 0)
                    st.success(f"Added '{new_t_name}'!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 3: APPEARANCE & WALLPAPERS STUDIO
# ══════════════════════════════════════════════════════════════════════════

def _render_appearance_tab(user_id: int):
    st.subheader("🎨 Appearance & Visual Themes")
    st.caption("Choose between Light/Dark modes, select curated 4K aesthetic wallpapers, upload your own backdrop, and fine-tune glassmorphism blur and contrast.")

    # 1. Theme Selector
    theme_options = ["☀️ Light", "🌙 Dark", "💻 System Default"]
    current_theme = get_user_theme(user_id)
    if current_theme == "Dark":
        theme_index = 1
    elif current_theme == "Default":
        theme_index = 2
    else:
        theme_index = 0

    c_th1, c_th2 = st.columns([3, 1])
    with c_th1:
        sel_theme_lbl = st.radio("Dashboard Color Mode:", theme_options, index=theme_index, horizontal=True, key="sett_theme_radio")
    with c_th2:
        st.write("")
        if st.button("Apply Mode", use_container_width=True, type="primary", key="sett_apply_theme_btn"):
            new_th = "Dark" if "Dark" in sel_theme_lbl else ("Default" if "System" in sel_theme_lbl else "Light")
            set_user_theme(user_id, new_th)
            st.session_state["theme_mode"] = new_th
            st.toast(f"✅ Theme set to {sel_theme_lbl}!", icon="🎨")
            st.rerun()

    st.markdown("---")

    # 2. Wallpaper Studio Hub
    wp_cfg = get_user_wallpaper_config(user_id)
    curr_mode = wp_cfg.get("mode", "none")
    curr_preset = wp_cfg.get("preset_id")
    curr_custom = wp_cfg.get("custom_url")
    curr_blur = wp_cfg.get("blur", 0)
    curr_opacity = wp_cfg.get("opacity", 0.82)

    if curr_mode == "preset":
        preset_name = next((p["name"] for p in WALLPAPER_PRESETS if p["id"] == curr_preset), curr_preset)
        st.info(f"🖼️ Active Wallpaper: **{preset_name}**")
    elif curr_mode == "custom":
        st.info("📸 Active Wallpaper: **Custom Image Upload**")
    else:
        st.caption("Active Wallpaper: *Default Solid Theme Background*")

    wp_tab1, wp_tab2, wp_tab3 = st.tabs([
        "🌌 Curated 4K Wallpapers (20 Options)",
        "📤 Custom Upload",
        "🚫 Solid Theme"
    ])

    with wp_tab1:
        cat_filter = st.selectbox(
            "Category Filter",
            ["All Wallpapers (20)", "🌌 Space & Sci-Fi", "🏙️ Cyber & Neon", "🌿 Nature & Calm", "📚 Study & Vibes", "✨ Abstract"],
            key="sett_wp_cat_filt"
        )
        filtered_presets = WALLPAPER_PRESETS if "All" in cat_filter else [p for p in WALLPAPER_PRESETS if p.get("category") == cat_filter]

        cols_per_row = 4
        for i in range(0, len(filtered_presets), cols_per_row):
            row_items = filtered_presets[i:i+cols_per_row]
            cols = st.columns(len(row_items))
            for idx, p in enumerate(row_items):
                with cols[idx]:
                    is_active = (curr_mode == "preset" and curr_preset == p["id"])
                    p_palette = p.get("palette", {})
                    accent = p_palette.get("accent", "#38BDF8")
                    border_style = f"3px solid {accent}; box-shadow: 0 0 16px {accent};" if is_active else "1px solid rgba(255,255,255,0.15);"

                    st.markdown(f"""
                        <div style="border-radius: 12px; overflow: hidden; border: {border_style}; margin-bottom: 8px; background: #1E293B;">
                            <img src="{p['thumb']}" style="width: 100%; height: 105px; object-fit: cover; display: block;" />
                            <div style="padding: 6px 8px; text-align: center;">
                                <div style="font-size: 0.8rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFFFFF;">{p['name']}</div>
                                <div style="font-size: 0.7rem; opacity: 0.75; color: #94A3B8;">{p.get('category', '')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_label = "✅ Active" if is_active else "Set Wallpaper"
                    if st.button(btn_label, key=f"sett_wp_btn_{p['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                        op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                        set_user_wallpaper_config(user_id, mode="preset", preset_id=p["id"], blur=curr_blur, opacity=op_val)
                        set_user_theme(user_id, "Dark")
                        st.session_state["theme_mode"] = "Dark"
                        st.toast(f"✅ Applied {p['name']}!", icon="🖼️")
                        st.rerun()

    with wp_tab2:
        uploaded_wp = st.file_uploader("Upload wallpaper image (JPG, PNG, WebP)", type=["png", "jpg", "jpeg", "webp"], key="sett_custom_wp_upload")
        if uploaded_wp is not None:
            data_url = process_uploaded_wallpaper(uploaded_wp)
            if data_url:
                st.image(uploaded_wp, use_container_width=True, caption="Preview of Uploaded Wallpaper")
                if st.button("✨ Apply Custom Wallpaper", type="primary", use_container_width=True, key="sett_save_custom_wp_btn"):
                    op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                    set_user_wallpaper_config(user_id, mode="custom", custom_url=data_url, blur=curr_blur, opacity=op_val)
                    set_user_theme(user_id, "Dark")
                    st.session_state["theme_mode"] = "Dark"
                    st.toast("✅ Custom wallpaper applied!", icon="📸")
                    st.rerun()

        elif curr_mode == "custom" and curr_custom:
            st.image(curr_custom, use_container_width=True, caption="Active Custom Wallpaper")
            if st.button("🗑️ Remove Custom Wallpaper", key="sett_del_custom_wp_btn"):
                clear_user_wallpaper_config(user_id)
                st.toast("Removed custom wallpaper.", icon="🧹")
                st.rerun()

    with wp_tab3:
        st.caption("Prefer a solid distraction-free theme background?")
        if st.button("🚫 Reset to Solid Theme", type="primary", use_container_width=True, key="sett_reset_solid_btn"):
            clear_user_wallpaper_config(user_id)
            st.toast("Reset to solid theme!", icon="✨")
            st.rerun()

    # Glassmorphism Controls
    if curr_mode != "none":
        with st.expander("🎛️ Glassmorphism Blur & Overlay Contrast Fine-Tuning", expanded=True):
            c_sl1, c_sl2 = st.columns(2)
            with c_sl1:
                new_blur = st.slider("Background Image Blur (px)", min_value=0, max_value=14, value=int(curr_blur), key="sett_blur_slider")
            with c_sl2:
                new_opacity = st.slider("Dark Overlay Opacity Tint", min_value=0.20, max_value=0.95, value=float(curr_opacity), step=0.02, key="sett_opac_slider")

            if st.button("💾 Save Visual Adjustments", key="sett_save_wp_adj_btn", use_container_width=True, type="primary"):
                set_user_wallpaper_config(user_id, mode=curr_mode, preset_id=curr_preset, custom_url=curr_custom, blur=new_blur, opacity=new_opacity)
                st.toast("Saved visual display adjustments!", icon="🎛️")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 4: DATA EXPORT
# ══════════════════════════════════════════════════════════════════════════

def _render_export_tab(user_id: int):
    st.subheader("📦 Flashcard Decks & Academic Audit Reports")
    st.caption("Export your complete flashcard repository directly into Anki (.tsv), CSV (.csv), or download comprehensive academic audit reports.")

    c_exp_a, c_exp_b, c_exp_c = st.columns(3)
    with c_exp_a:
        st.markdown("""
            <div class="metric-box" style="border-left: 4px solid #6366F1; padding: 16px;">
                <div style="font-weight: 700; color: #6366F1; font-size: 0.95rem;">🗂️ Master Anki Deck</div>
                <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin: 6px 0 12px 0;">
                    Mistakes, Active Recall Feynman decks, and Formula Vault with LaTeX formatting.
                </div>
            </div>
        """, unsafe_allow_html=True)
        master_tsv = export_all_to_anki(user_id, format_type="tsv")
        st.download_button(
            label="📥 Download Anki (.tsv)",
            data=master_tsv,
            file_name="Nexus_Master_Flashcards.tsv",
            mime="text/tab-separated-values",
            use_container_width=True,
            key="sett_dl_master_anki_tsv"
        )
    with c_exp_b:
        st.markdown("""
            <div class="metric-box" style="border-left: 4px solid #38BDF8; padding: 16px;">
                <div style="font-weight: 700; color: #38BDF8; font-size: 0.95rem;">📊 Universal CSV Deck</div>
                <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin: 6px 0 12px 0;">
                    Compatible with Notion, Quizlet, RemNote, Google Sheets, or Excel.
                </div>
            </div>
        """, unsafe_allow_html=True)
        master_csv = export_all_to_anki(user_id, format_type="csv")
        st.download_button(
            label="📊 Download CSV (.csv)",
            data=master_csv,
            file_name="Nexus_Master_Flashcards.csv",
            mime="text/csv",
            use_container_width=True,
            key="sett_dl_master_anki_csv"
        )
    with c_exp_c:
        st.markdown("""
            <div class="metric-box" style="border-left: 4px solid #10B981; padding: 16px;">
                <div style="font-weight: 700; color: #10B981; font-size: 0.95rem;">📄 Academic PDF Report</div>
                <div style="font-size: 0.78rem; color: var(--nexus-text-sub); margin: 6px 0 12px 0;">
                    Complete performance audit with syllabus matrix, velocity metrics & AI recommendations.
                </div>
            </div>
        """, unsafe_allow_html=True)
        pdf_rep = generate_weekly_progress_pdf(user_id, days=7)
        st.download_button(
            label="📄 Export 7-Day PDF Report",
            data=pdf_rep,
            file_name="Nexus_Academic_Report_7Days.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key="sett_dl_pdf_btn"
        )


# ══════════════════════════════════════════════════════════════════════════
# SUBVIEW 5: DANGER ZONE
# ══════════════════════════════════════════════════════════════════════════

def _render_danger_tab(user_id: int):
    st.subheader("⚠️ Danger Zone")
    st.warning("Resetting will wipe all subjects, chapters, topics, study sessions, quizzes, mistakes, and progress permanently.")

    confirm_reset = st.checkbox("I understand that resetting will permanently wipe all my dashboard data.")
    if st.button("🔴 Reset All Data", type="primary", disabled=not confirm_reset, key="sett_reset_all_btn"):
        reset_all_data(user_id)
        st.success("All data has been reset! Reloading...")
        st.rerun()
