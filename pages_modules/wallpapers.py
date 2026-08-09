"""
wallpapers.py — Dedicated Wallpaper Studio & Visual Customizer.

Provides:
1. 20 Curated 4K High-Definition aesthetic wallpapers categorized for study focus.
2. Custom image uploader from gallery/device with automatic resizing and compression.
3. Minimalist Solid Theme option.
4. Live Glassmorphism blur and card contrast/overlay fine-tuning.
5. Instant ☀️ Light and 🌙 Dark theme toggle.
"""

import streamlit as st
import io
import base64

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from models import (
    get_user_theme, set_user_theme,
    get_user_wallpaper_config, set_user_wallpaper_config, clear_user_wallpaper_config
)
from styles import render_header, WALLPAPER_PRESETS


def process_uploaded_wallpaper(uploaded_file, max_width: int = 1920, quality: int = 82):
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


def render_wallpapers_page(user_id: int):
    user_theme = get_user_theme(user_id)
    is_dark = (user_theme.strip().lower() == "dark")

    render_header(
        "🖼️ Wallpaper & Appearance Studio",
        "Personalize your study sanctuary with 20 curated 4K wallpapers, custom gallery uploads, and glassmorphism styling.",
        theme=user_theme
    )

    wp_cfg = get_user_wallpaper_config(user_id)
    curr_mode = wp_cfg.get("mode", "none")
    curr_preset = wp_cfg.get("preset_id")
    curr_custom = wp_cfg.get("custom_url")
    curr_blur = wp_cfg.get("blur", 0)
    curr_opacity = wp_cfg.get("opacity", 0.82)

    # ── Active Status Hero Banner ──
    active_name = "Default Solid Theme"
    active_thumb = None
    if curr_mode == "preset":
        match = next((p for p in WALLPAPER_PRESETS if p["id"] == curr_preset), None)
        if match:
            active_name = match["name"]
            active_thumb = match["thumb"]
    elif curr_mode == "custom":
        active_name = "Custom Photo from Device / Gallery"
        active_thumb = curr_custom

    banner_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95))" if is_dark else "linear-gradient(135deg, #FFFFFF, #F1F5F9)"
    banner_border = "rgba(56, 189, 248, 0.35)" if is_dark else "#CBD5E1"
    text_color = "#FFFFFF" if is_dark else "#0F172A"

    col_stat1, col_stat2 = st.columns([3, 1])
    with col_stat1:
        st.markdown(f"""
            <div style="background: {banner_bg}; border: 1px solid {banner_border}; border-radius: 16px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                    <div style="font-size: 2.2rem;">✨</div>
                    <div style="flex: 1; min-width: 200px;">
                        <div style="font-size: 0.82rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Current Study Ambience</div>
                        <div style="font-size: 1.35rem; font-weight: 700; color: {text_color}; font-family: 'Outfit', sans-serif;">{active_name}</div>
                        <div style="font-size: 0.85rem; color: {'#38BDF8' if is_dark else '#4F46E5'}; margin-top: 2px;">
                            Theme: <strong>{user_theme}</strong> • Blur: <strong>{curr_blur}px</strong> • Glass Opacity: <strong>{int(curr_opacity * 100)}%</strong>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_stat2:
        if curr_mode != "none":
            st.write("") # Spacer
            if st.button("🚫 Reset to Solid Theme", use_container_width=True, help="Switch back to minimalist solid background"):
                clear_user_wallpaper_config(user_id)
                st.toast("Reset to minimalist solid theme!", icon="✨")
                st.rerun()
        else:
            st.write("") # Spacer
            st.caption("💡 Pick a preset below to instantly activate wallpaper & glassmorphism!")

    # ── Main Studio Tabs ──
    tab_presets, tab_upload, tab_tuning, tab_theme = st.tabs([
        "🖼️ Curated 4K Wallpapers (20 Options)",
        "📤 Upload Custom Wallpaper",
        "🎛️ Glassmorphism & Blur Tuning",
        "🎨 Light / Dark Theme Mode"
    ])

    # ── TAB 1: CURATED 4K PRESETS ──
    with tab_presets:
        st.markdown("### 🌟 Choose Your Study Aesthetic")
        st.caption("Click any wallpaper below to instantly activate glowing dark glassmorphism and wallpaper ambience.")

        c_filt, c_rand = st.columns([3, 1])
        with c_filt:
            cat_options = ["All Wallpapers (20)", "🌌 Space & Sci-Fi", "🏙️ Cyber & Neon", "🌿 Nature & Calm", "📚 Study & Vibes", "✨ Abstract"]
            cat_filter = st.selectbox("Filter by Category", cat_options, key="wp_studio_cat_filter")
        with c_rand:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("🎲 Random Aesthetic", use_container_width=True, help="Surprise me with a random study wallpaper"):
                import random
                rand_wp = random.choice(WALLPAPER_PRESETS)
                op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                set_user_wallpaper_config(user_id, mode="preset", preset_id=rand_wp["id"], blur=curr_blur, opacity=op_val)
                set_user_theme(user_id, "Dark")
                st.session_state["theme_mode"] = "Dark"
                st.toast(f"✅ Activated {rand_wp['name']} in Dark Glassmorphism!", icon="🎲")
                st.rerun()

        filtered_presets = WALLPAPER_PRESETS if "All" in cat_filter else [p for p in WALLPAPER_PRESETS if p.get("category") == cat_filter]

        # 4 Columns Grid
        cols_per_row = 4
        for i in range(0, len(filtered_presets), cols_per_row):
            row_items = filtered_presets[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for idx, p in enumerate(row_items):
                with cols[idx]:
                    is_active = (curr_mode == "preset" and curr_preset == p["id"])
                    border_style = "3px solid #38BDF8; box-shadow: 0 0 18px rgba(56, 189, 248, 0.5);" if is_active else "1px solid rgba(255,255,255,0.15);"
                    badge_label = "✅ ACTIVE" if is_active else p.get("category", "").split(" ")[-1]
                    badge_bg = "#38BDF8" if is_active else "rgba(15, 23, 42, 0.75)"
                    badge_color = "#0B0F19" if is_active else "#E2E8F0"

                    st.markdown(f"""
                        <div style="border-radius: 14px; overflow: hidden; border: {border_style}; margin-bottom: 10px; background: #1E293B; position: relative; transition: all 0.3s ease;">
                            <div style="position: absolute; top: 8px; right: 8px; background: {badge_bg}; color: {badge_color}; font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 8px; z-index: 2; letter-spacing: 0.04em;">
                                {badge_label}
                            </div>
                            <img src="{p['thumb']}" style="width: 100%; height: 130px; object-fit: cover; display: block;" loading="lazy" />
                            <div style="padding: 10px 12px; text-align: center;">
                                <div style="font-size: 0.9rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFFFFF;">{p['name']}</div>
                                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">{p.get('category', '')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    btn_label = "✅ Active" if is_active else "✨ Apply Wallpaper"
                    if st.button(btn_label, key=f"studio_set_wp_{p['id']}", use_container_width=True, type="primary" if is_active else "secondary"):
                        op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                        set_user_wallpaper_config(user_id, mode="preset", preset_id=p["id"], blur=curr_blur, opacity=op_val)
                        set_user_theme(user_id, "Dark")
                        st.session_state["theme_mode"] = "Dark"
                        st.toast(f"✅ Applied {p['name']} in Dark Glassmorphism!", icon="🖼️")
                        st.rerun()

    # ── TAB 2: UPLOAD CUSTOM WALLPAPER ──
    with tab_upload:
        st.markdown("### 📸 Upload Any Image from Your Device")
        st.caption("Upload any photo, wallpaper, anime art, or inspirational picture from your phone or PC. We automatically optimize and compress it.")

        uploaded_wp = st.file_uploader(
            "Choose a wallpaper image (PNG, JPG, JPEG, WEBP)",
            type=["png", "jpg", "jpeg", "webp"],
            key="studio_custom_wp_uploader"
        )

        if uploaded_wp is not None:
            data_url = process_uploaded_wallpaper(uploaded_wp)
            if data_url:
                col_prev, col_act = st.columns([2, 1])
                with col_prev:
                    st.image(uploaded_wp, use_container_width=True, caption="Live Preview of Uploaded Wallpaper")
                with col_act:
                    st.write("")
                    st.write("")
                    st.success("✅ Image processed & optimized successfully!")
                    if st.button("✨ Set as Active Wallpaper", type="primary", use_container_width=True, key="studio_save_custom_wp_btn"):
                        op_val = 0.30 if curr_opacity >= 0.75 else curr_opacity
                        set_user_wallpaper_config(user_id, mode="custom", custom_url=data_url, blur=curr_blur, opacity=op_val)
                        set_user_theme(user_id, "Dark")
                        st.session_state["theme_mode"] = "Dark"
                        st.toast("✅ Custom wallpaper applied in Dark Glassmorphism!", icon="📸")
                        st.rerun()
            else:
                st.error("Could not process this image file. Please try another JPG or PNG image.")
        elif curr_mode == "custom" and curr_custom:
            st.markdown("#### Currently Active Custom Wallpaper:")
            c_p1, c_p2 = st.columns([2, 1])
            with c_p1:
                st.image(curr_custom, use_container_width=True, caption="Active Custom Background")
            with c_p2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remove Custom Wallpaper", key="studio_del_custom_wp_btn", type="primary", use_container_width=True):
                    clear_user_wallpaper_config(user_id)
                    st.toast("Custom wallpaper removed.", icon="🧹")
                    st.rerun()

    # ── TAB 3: GLASSMORPHISM & BLUR TUNING ──
    with tab_tuning:
        st.markdown("### 🎛️ Visual Clarity & Glassmorphism Fine-Tuning")
        st.caption("Adjust the blur and contrast tint so dashboard metrics and text are always crystal clear to read.")

        if curr_mode == "none":
            st.info("💡 You currently have the solid theme active. Pick any wallpaper preset or upload a custom image to unlock live background blur and glassmorphism.")

        c_sl1, c_sl2 = st.columns(2)
        with c_sl1:
            new_blur = st.slider(
                "Background Image Blur (px)",
                min_value=0,
                max_value=16,
                value=int(curr_blur),
                help="Add soft blur to the wallpaper to make text and charts pop with zero visual distraction."
            )
            blur_desc = "Sharp & Detailed" if new_blur == 0 else ("Subtle Blur" if new_blur <= 4 else ("Medium Focus Blur" if new_blur <= 8 else "Heavy Studio Frost"))
            st.caption(f"Blur Style: **{blur_desc}** ({new_blur}px)")

        with c_sl2:
            new_opacity = st.slider(
                "Background Dark Tint Overlay",
                min_value=0.10,
                max_value=0.80,
                value=min(0.80, max(0.10, float(curr_opacity))),
                step=0.05,
                help="Lower values make the wallpaper brighter and clearer; higher values make text darker and higher contrast."
            )
            st.caption(f"Overlay Tint: **{int(new_opacity * 100)}%**")

        if st.button("💾 Save Glassmorphism Settings", key="studio_save_tuning_btn", type="primary", use_container_width=True):
            set_user_wallpaper_config(
                user_id,
                mode=curr_mode if curr_mode != "none" else "none",
                preset_id=curr_preset,
                custom_url=curr_custom,
                blur=new_blur,
                opacity=new_opacity
            )
            st.toast("✅ Visual adjustments saved!", icon="🎛️")
            st.rerun()

    # ── TAB 4: THEME & COLOR MODE ──
    with tab_theme:
        st.markdown("### 🎨 Select Theme Mode")
        st.caption("Switch between light and dark modes. Wallpapers work beautifully with both!")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            is_light_active = (user_theme.lower() == "light")
            st.markdown(f"""
                <div style="background: #FFFFFF; border: 2px solid {'#4F46E5' if is_light_active else '#E2E8F0'}; border-radius: 14px; padding: 18px; color: #0F172A; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="font-size: 1.5rem; margin-bottom: 6px;">☀️ <strong>Light Theme</strong></div>
                    <div style="font-size: 0.88rem; color: #64748B;">Crisp, clean, high-contrast, modern aesthetic with soft shadows.</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("☀️ Set Light Theme", use_container_width=True, type="primary" if is_light_active else "secondary", key="studio_set_light_btn"):
                set_user_theme(user_id, "Light")
                st.session_state["theme_mode"] = "Light"
                st.toast("Theme set to Light!", icon="☀️")
                st.rerun()

        with col_t2:
            is_dark_active = (user_theme.lower() == "dark")
            st.markdown(f"""
                <div style="background: #0F172A; border: 2px solid {'#38BDF8' if is_dark_active else 'rgba(255,255,255,0.15)'}; border-radius: 14px; padding: 18px; color: #FFFFFF; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    <div style="font-size: 1.5rem; margin-bottom: 6px; color: #FFFFFF;">🌙 <strong>Dark Theme</strong></div>
                    <div style="font-size: 0.88rem; color: #94A3B8;">Futuristic glassmorphism, neon accents, deep navy slate palette.</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🌙 Set Dark Theme", use_container_width=True, type="primary" if is_dark_active else "secondary", key="studio_set_dark_btn"):
                set_user_theme(user_id, "Dark")
                st.session_state["theme_mode"] = "Dark"
                st.toast("Theme set to Dark!", icon="🌙")
                st.rerun()
