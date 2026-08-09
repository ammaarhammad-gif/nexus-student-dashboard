"""
styles.py — Custom CSS theming engine for the Nexus Student Dashboard.

Supports:
1. ☀️ Light Theme (Default) — Ultra-clean, modern, high-contrast, beautiful soft shadows.
2. 🌙 Dark Theme — Futuristic glassmorphism, deep slate/navy, glowing cyber accents, vivid text.
3. 💻 System Default — Maps to Light mode as standard default.
"""

import streamlit as st


# ══════════════════════════════════════════════════════════════════════════
# 20 CURATED AESTHETIC HIGH-RES WALLPAPERS
# ══════════════════════════════════════════════════════════════════════════
WALLPAPER_PRESETS = [
    {
        "id": "cosmic_nebula",
        "name": "🌌 Cosmic Nebula",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "cyberpunk_city",
        "name": "🏙️ Cyberpunk Neo-Tokyo",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "alpine_forest",
        "name": "🌄 Misty Nordic Forest",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "mountain_alpenglow",
        "name": "🏔️ Snow Summit Alpenglow",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "obsidian_wave",
        "name": "✨ Liquid Obsidian Wave",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "midnight_library",
        "name": "📚 Midnight Grand Library",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "golden_sunset",
        "name": "🌇 Golden Horizon Sunset",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "sakura_dawn",
        "name": "🌸 Sakura Blossom Dawn",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "emerald_aurora",
        "name": "🌌 Emerald Aurora Borealis",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "matrix_terminal",
        "name": "💎 Matrix Cyber Terminal",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "deep_ocean",
        "name": "🌊 Deep Ocean Twilight",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1682687220063-4742bd7fd538?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1682687220063-4742bd7fd538?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "pastel_clouds",
        "name": "☁️ Pastel Cloud Reverie",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "zen_minimal",
        "name": "🏛️ Zen Minimalist Studio",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "synthwave_grid",
        "name": "⚡ Synthwave Neon Grid",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "coastal_sunset",
        "name": "🍂 Golden Coastal Shore",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "starlight_odyssey",
        "name": "🪐 Andromeda Galaxy Stars",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "emerald_foliage",
        "name": "🌿 Tropical Emerald Foliage",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "lofi_study_desk",
        "name": "☕ Lofi Coffee & Focus Desk",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "prism_spectrum",
        "name": "🔮 Prism Refraction Waves",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=400&q=75"
    },
    {
        "id": "midnight_dunes",
        "name": "🌙 Moonlit Sahara Dunes",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1920&q=80",
        "thumb": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=400&q=75"
    }
]


def apply_custom_css(theme: str = "Dark", wallpaper_url: str = None, wallpaper_blur: int = 0, overlay_opacity: float = 0.30):
    """
    Injects the complete CSS theme (Light or Dark) and optional glassmorphism wallpaper into the Streamlit app.
    Supports 20 preset curated wallpapers and custom user-uploaded images.
    """
    is_dark = (theme.strip().lower() == "dark")
    has_wallpaper = bool(wallpaper_url and str(wallpaper_url).strip())

    if is_dark:
        card_bg = "rgba(15, 23, 42, 0.65)" if has_wallpaper else "rgba(19, 27, 46, 0.9)"
        sidebar_bg = "linear-gradient(180deg, rgba(9, 13, 22, 0.78) 0%, rgba(15, 23, 42, 0.85) 100%)" if has_wallpaper else "linear-gradient(180deg, #090D16 0%, #0F172A 100%)"
        expander_bg = "rgba(15, 23, 42, 0.60)" if has_wallpaper else "rgba(19, 27, 46, 0.85)"
        
        theme_vars = f"""
        :root {{
            --nexus-bg: {'transparent' if has_wallpaper else '#0B0F19'};
            --nexus-card-bg: {card_bg};
            --nexus-card-border: rgba(255, 255, 255, 0.13);
            --nexus-card-hover-border: #38BDF8;
            --nexus-text-main: #F8FAFC;
            --nexus-text-title: #FFFFFF;
            --nexus-text-sub: #94A3B8;
            --nexus-text-muted: #64748B;
            --nexus-input-bg: rgba(19, 27, 46, 0.85);
            --nexus-input-border: rgba(255, 255, 255, 0.18);
            --nexus-input-text: #FFFFFF;
            --nexus-sidebar-bg: {sidebar_bg};
            --nexus-sidebar-border: rgba(255, 255, 255, 0.1);
            --nexus-expander-bg: {expander_bg};
            --nexus-expander-border: rgba(255, 255, 255, 0.12);
            --nexus-tab-bg: rgba(15, 23, 42, 0.6);
            --nexus-tab-border: rgba(255, 255, 255, 0.08);
            --nexus-btn-bg: #1E293B;
            --nexus-btn-text: #F8FAFC;
            --nexus-btn-border: rgba(255, 255, 255, 0.15);
        }}
        """
        
        if has_wallpaper:
            wallpaper_css = f"""
            .stApp::before, [data-testid="stAppViewContainer"]::before {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background-image: url('{wallpaper_url}') !important;
                background-size: cover !important; background-position: center center !important;
                background-repeat: no-repeat !important; background-attachment: fixed !important;
                filter: blur({wallpaper_blur}px) brightness(0.92) !important;
                transform: scale(1.04) !important;
                z-index: -2 !important; pointer-events: none !important;
            }}
            .stApp::after, [data-testid="stAppViewContainer"]::after {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background: rgba(11, 15, 25, {overlay_opacity}) !important;
                backdrop-filter: blur(1px) !important;
                z-index: -1 !important; pointer-events: none !important;
            }}
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], section.main, .block-container, [data-testid="stMainBlockContainer"], .stMain {{
                background-color: transparent !important;
                background: transparent !important;
            }}
            .nexus-card, div[data-testid="stMetric"], details[data-testid="stExpander"], div[data-testid="stForm"] {{
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            }}
            """
        else:
            wallpaper_css = """
            .stApp::before {
                content: '';
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.1) 0%, transparent 40%),
                            radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.08) 0%, transparent 40%);
                pointer-events: none;
                z-index: 0;
            }
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
                background-color: #0B0F19 !important;
            }
            """

        theme_rules = """
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
            color: #F8FAFC !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        p, span, label, div {
            color: #E2E8F0;
        }

        strong, b {
            color: #FFFFFF !important;
            font-weight: 600;
        }

        /* Sidebar Dark */
        section[data-testid="stSidebar"] {
            background: var(--nexus-sidebar-bg) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 10px 16px !important;
            margin-bottom: 8px !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(56, 189, 248, 0.15) !important;
            border-color: #38BDF8 !important;
            transform: translateX(4px);
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.85) 0%, rgba(56, 189, 248, 0.85) 100%) !important;
            border: 1px solid #38BDF8 !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] p {
            color: #F8FAFC !important;
            font-weight: 600 !important;
        }

        /* Inputs & Controls Dark */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
            background-color: #131B2E !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
            border-color: #38BDF8 !important;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
        }

        .stSelectbox [data-baseweb="select"] {
            background-color: #131B2E !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
        }

        .stSelectbox [data-baseweb="select"] div {
            color: #FFFFFF !important;
        }

        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
            background-color: #131B2E !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        ul[role="listbox"] li {
            color: #E2E8F0 !important;
        }

        details[data-testid="stExpander"] {
            background: var(--nexus-expander-bg) !important;
            border: 1px solid var(--nexus-expander-border) !important;
            border-radius: 14px !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
        }

        details[data-testid="stExpander"] summary {
            color: #F8FAFC !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #94A3B8 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(30, 41, 59, 0.9) !important;
            color: #38BDF8 !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
        }

        .stButton > button {
            background: #1E293B !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        }

        .stButton > button:hover {
            border-color: #38BDF8 !important;
            color: #38BDF8 !important;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.2) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366F1 0%, #0284C7 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        }

        .badge-not-started   { background-color: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.3); }
        .badge-in-progress   { background-color: rgba(234, 179, 8, 0.2);   color: #FDE047; border: 1px solid rgba(234, 179, 8, 0.4); }
        .badge-completed     { background-color: rgba(34, 197, 94, 0.2);   color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.4); }
        .badge-revision-done { background-color: rgba(59, 130, 246, 0.2);  color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); }
        """
    else:
        card_bg = "rgba(255, 255, 255, 0.70)" if has_wallpaper else "#FFFFFF"
        sidebar_bg = "linear-gradient(180deg, rgba(255, 255, 255, 0.85) 0%, rgba(248, 250, 252, 0.90) 100%)" if has_wallpaper else "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)"
        expander_bg = "rgba(255, 255, 255, 0.70)" if has_wallpaper else "#FFFFFF"
        
        theme_vars = f"""
        :root {{
            --nexus-bg: {'transparent' if has_wallpaper else '#F8FAFC'};
            --nexus-card-bg: {card_bg};
            --nexus-card-border: #E2E8F0;
            --nexus-card-hover-border: #6366F1;
            --nexus-text-main: #0F172A;
            --nexus-text-title: #0F172A;
            --nexus-text-sub: #64748B;
            --nexus-text-muted: #94A3B8;
            --nexus-input-bg: rgba(255, 255, 255, 0.9);
            --nexus-input-border: #CBD5E1;
            --nexus-input-text: #0F172A;
            --nexus-sidebar-bg: {sidebar_bg};
            --nexus-sidebar-border: #E2E8F0;
            --nexus-expander-bg: {expander_bg};
            --nexus-expander-border: #E2E8F0;
            --nexus-tab-bg: #F1F5F9;
            --nexus-tab-border: #E2E8F0;
            --nexus-btn-bg: #FFFFFF;
            --nexus-btn-text: #0F172A;
            --nexus-btn-border: #CBD5E1;
        }}
        """
        
        if has_wallpaper:
            wallpaper_css = f"""
            .stApp::before, [data-testid="stAppViewContainer"]::before {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background-image: url('{wallpaper_url}') !important;
                background-size: cover !important; background-position: center center !important;
                background-repeat: no-repeat !important; background-attachment: fixed !important;
                filter: blur({wallpaper_blur}px) brightness(0.95) !important;
                transform: scale(1.04) !important;
                z-index: -2 !important; pointer-events: none !important;
            }}
            .stApp::after, [data-testid="stAppViewContainer"]::after {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background: rgba(248, 250, 252, {overlay_opacity}) !important;
                backdrop-filter: blur(1px) !important;
                z-index: -1 !important; pointer-events: none !important;
            }}
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], section.main, .block-container, [data-testid="stMainBlockContainer"], .stMain {{
                background-color: transparent !important;
                background: transparent !important;
            }}
            .nexus-card, div[data-testid="stMetric"], details[data-testid="stExpander"], div[data-testid="stForm"] {{
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            }}
            """
        else:
            wallpaper_css = """
            .stApp::before {
                content: '';
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.04) 0%, transparent 40%),
                            radial-gradient(circle at 90% 90%, rgba(2, 132, 199, 0.04) 0%, transparent 40%);
                pointer-events: none;
                z-index: 0;
            }
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
                background-color: #F8FAFC !important;
            }
            """

        theme_rules = """
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
            color: #0F172A !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #0F172A !important;
        }

        p, span, label, div {
            color: #334155;
        }

        strong, b {
            color: #0F172A !important;
            font-weight: 600;
        }

        /* Sidebar Light */
        section[data-testid="stSidebar"] {
            background: var(--nexus-sidebar-bg) !important;
            border-right: 1px solid #E2E8F0 !important;
            box-shadow: 2px 0 15px rgba(0, 0, 0, 0.03);
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            background: #F1F5F9 !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 10px 16px !important;
            margin-bottom: 8px !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: #E2E8F0 !important;
            border-color: #6366F1 !important;
            transform: translateX(4px);
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: linear-gradient(135deg, #4F46E5 0%, #0284C7 100%) !important;
            border: 1px solid #4F46E5 !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] p {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        /* Inputs Light */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        }

        .stSelectbox [data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }

        .stSelectbox [data-baseweb="select"] div {
            color: #0F172A !important;
            font-weight: 500;
        }

        details[data-testid="stExpander"] {
            background: var(--nexus-expander-bg) !important;
            border: 1px solid var(--nexus-expander-border) !important;
            border-radius: 14px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
        }

        details[data-testid="stExpander"] summary {
            color: #0F172A !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background-color: #F1F5F9 !important;
            border: 1px solid #E2E8F0 !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #64748B !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #FFFFFF !important;
            color: #4F46E5 !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }

        .stButton > button {
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
        }

        .stButton > button:hover {
            border-color: #4F46E5 !important;
            color: #4F46E5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #0284C7 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
        }

        .badge-not-started   { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }
        .badge-in-progress   { background-color: #FEF9C3; color: #A16207; border: 1px solid #FDE047; }
        .badge-completed     { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
        .badge-revision-done { background-color: #DBEAFE; color: #1D4ED8; border: 1px solid #93C5FD; }
        """

    # ══════════════════════════════════════════════════════════════════════════
    # SHARED COMPONENT STYLES
    # ══════════════════════════════════════════════════════════════════════════
    shared_css = """
        /* Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

        .nexus-card {
            background: var(--nexus-card-bg) !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .nexus-card:hover {
            border-color: var(--nexus-card-hover-border) !important;
            box-shadow: 0 12px 30px -4px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        .nexus-card h1, .nexus-card h2, .nexus-card h3, .nexus-card h4, .nexus-card h5 {
            color: var(--nexus-text-title) !important;
        }

        .nexus-card p, .nexus-card span {
            color: var(--nexus-text-sub);
        }

        .metric-box {
            background: var(--nexus-card-bg) !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 14px;
            padding: 20px 18px;
            text-align: center;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06);
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
        }

        .metric-box:hover {
            border-color: #6366F1 !important;
            transform: translateY(-2px);
        }

        .metric-title {
            color: var(--nexus-text-sub) !important;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif !important;
            font-size: 2.2rem;
            font-weight: 800;
        }

        .metric-sub {
            color: var(--nexus-text-muted) !important;
            font-size: 0.8rem;
            margin-top: 6px;
        }

        /* Custom Progress Bars */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #4F46E5 0%, #06B6D4 50%, #22C55E 100%) !important;
            border-radius: 10px;
        }

        /* Checkbox Styling */
        .stCheckbox label span[role="checkbox"][aria-checked="true"] {
            background-color: #22C55E !important;
            border-color: #22C55E !important;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.4) !important;
        }

        /* Welcome Banner */
        .welcome-banner {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #0284C7 100%);
            border-radius: 16px;
            padding: 28px 34px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
        }

        .welcome-banner h2 {
            color: #FFFFFF !important;
            margin: 0 0 6px 0 !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }

        .welcome-banner p {
            color: rgba(255, 255, 255, 0.9) !important;
            margin: 0 !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }

        /* Setup Wizard Hero */
        .setup-hero {
            text-align: center;
            padding: 30px 20px 15px 20px;
        }

        .setup-hero h1 {
            font-size: 2.8rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #4F46E5, #0284C7, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
            letter-spacing: -0.03em;
        }

        /* Responsive Media Queries */
        iframe {
            max-width: 100% !important;
            width: 100% !important;
        }
        [data-testid="stIFrame"] {
            width: 100% !important;
        }
        @media (max-width: 900px) {
            .metric-box { padding: 14px 14px; margin-bottom: 10px; }
            .metric-value { font-size: 1.7rem !important; }
            .metric-title { font-size: 0.75rem !important; }
            .nexus-card { padding: 18px 20px; border-radius: 14px; }
            .welcome-banner { padding: 20px 22px; }
            .welcome-banner h2 { font-size: 1.45rem !important; }
            .setup-hero h1 { font-size: 2.3rem !important; }
        }
        @media (max-width: 768px) {
            .metric-box { padding: 12px 14px; margin-bottom: 8px; border-radius: 12px; }
            .metric-value { font-size: 1.5rem !important; }
            .metric-title { font-size: 0.72rem !important; }
            .metric-sub { font-size: 0.74rem !important; }
            .nexus-card { padding: 14px 16px; border-radius: 12px; margin-bottom: 12px; }
            .welcome-banner { padding: 16px 16px; border-radius: 14px; margin-bottom: 16px; }
            .welcome-banner h2 { font-size: 1.3rem !important; }
            .welcome-banner p { font-size: 0.9rem !important; }
            h1 { font-size: 1.6rem !important; }
            h2 { font-size: 1.35rem !important; }
            h3 { font-size: 1.15rem !important; }
            .setup-hero { padding: 20px 10px 10px 10px; }
            .setup-hero h1 { font-size: 2.0rem !important; }
            .setup-hero p { font-size: 1.0rem !important; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 100% !important; flex: 1 1 100% !important;
            }
        }
        @media (max-width: 480px) {
            .metric-box { padding: 10px 12px; }
            .metric-value { font-size: 1.35rem !important; }
            .nexus-card { padding: 12px 14px; }
            .setup-hero h1 { font-size: 1.75rem !important; }
        }
    """

    st.markdown(f"<style>{theme_vars}\n{wallpaper_css}\n{theme_rules}\n{shared_css}</style>", unsafe_allow_html=True)



def render_header(title: str, subtitle: str = "", theme: str = "Light"):
    """Render a stylish page header with optional subtitle."""
    is_dark = (theme.strip().lower() == "dark")
    bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98))" if is_dark else "linear-gradient(135deg, #FFFFFF, #F8FAFC)"
    border = "rgba(255,255,255,0.1)" if is_dark else "#E2E8F0"
    title_color = "#FFFFFF" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    st.markdown(f"""
        <div style="margin-bottom: 20px; padding: 16px 20px; background: {bg}; border-left: 5px solid #4F46E5; border-radius: 14px; box-shadow: 0 4px 18px rgba(0,0,0,{'0.35' if is_dark else '0.04'}); border-top: 1px solid {border}; border-right: 1px solid {border}; border-bottom: 1px solid {border};">
            <h1 style="color: {title_color} !important; font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; font-size: clamp(1.35rem, 4vw, 2.1rem) !important; margin: 0 0 4px 0 !important; letter-spacing: -0.02em; line-height: 1.25;">{title}</h1>
            {f'<p style="color: {sub_color} !important; font-size: clamp(0.85rem, 2.5vw, 1.02rem) !important; margin: 0 !important; font-weight: 500; line-height: 1.45;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value, accent_color: str = "#4F46E5", subtitle: str = "", theme: str = "Light", **kwargs):
    """Render a single styled metric box."""
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color: {accent_color};">{value}</div>
            {f'<div class="metric-sub">{subtitle}</div>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


import streamlit.components.v1 as components


def render_cinematic_welcome_banner(user_name: str = "Student", class_name: str = "Class 10", board: str = "CBSE", theme: str = "Light"):
    """
    Renders an ultra-premium, fully responsive cinematic animated welcome banner using Streamlit Components:
    1. Permanent bold title 'Welcome to Nexus Student Dashboard'
    2. Smooth transition typing 'Made by Ammaar Akhtar with love and hope'
    3. Seamless erase transition
    4. Word-by-word typewriter narrative of the app's purpose + personalized emotional motivational quote
    5. Fully responsive with fluid typography and dynamic height synchronization across Mobile, Tablet, & Desktop.
    """
    is_dark = (theme.strip().lower() == "dark")
    bg = "linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 50%, rgba(15, 23, 42, 0.98) 100%)" if is_dark else "linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #1E293B 100%)"
    border = "rgba(56, 189, 248, 0.35)" if is_dark else "rgba(99, 102, 241, 0.4)"
    shadow = "0 12px 35px -5px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.15)" if is_dark else "0 12px 35px -5px rgba(79, 70, 229, 0.35)"
    
    clean_name = str(user_name or "Student").replace('"', '').replace("'", "")
    clean_class = str(class_name or "Class 10").replace('"', '').replace("'", "")
    clean_board = str(board or "CBSE").replace('"', '').replace("'", "")
    
    html_code = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
        background: transparent;
        overflow-x: hidden;
        overflow-y: auto;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        width: 100%;
        margin: 0;
        padding: 0;
    }
    
    .nexus-cinematic-banner {
        background: __BG__;
        border: 1px solid __BORDER__;
        border-radius: 20px;
        padding: 22px 26px;
        box-shadow: __SHADOW__;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        transition: all 0.3s ease;
    }
    
    .glow-orb-1 {
        position: absolute; top: -60px; right: -60px; width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none;
    }
    
    .glow-orb-2 {
        position: absolute; bottom: -80px; left: 8%; width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none;
    }
    
    .meta-wrapper {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px 10px;
        margin-bottom: 4px;
        position: relative;
        z-index: 1;
    }

    .meta-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38BDF8;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 3px 10px;
        border-radius: 20px;
        white-space: nowrap;
    }
    
    .meta-class {
        color: #94A3B8;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }
    
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(1.25rem, 4.2vw, 1.95rem);
        font-weight: 900;
        margin: 6px 0 8px 0;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.25;
        word-wrap: break-word;
        overflow-wrap: break-word;
        position: relative;
        z-index: 1;
    }
    
    .text-container {
        font-size: clamp(0.85rem, 2.7vw, 0.96rem);
        line-height: 1.55;
        color: #CBD5E1;
        font-weight: 500;
        min-height: 62px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        position: relative;
        z-index: 1;
    }
    
    #nexus-anim-text {
        word-break: break-word;
    }

    #nexus-cursor {
        display: inline-block;
        width: 2px;
        height: 1.15em;
        background-color: #38BDF8;
        vertical-align: text-bottom;
        margin-left: 2px;
        animation: nexusBlink 0.8s infinite;
        box-shadow: 0 0 8px #38BDF8;
    }
    
    @keyframes nexusBlink {
        0%, 49% { opacity: 1; }
        50%, 100% { opacity: 0; }
    }

    @media (max-width: 768px) {
        .nexus-cinematic-banner {
            padding: 16px 18px;
            border-radius: 16px;
        }
        .hero-title {
            margin: 4px 0 6px 0;
            line-height: 1.26;
        }
        .text-container {
            line-height: 1.48;
            min-height: 55px;
        }
    }

    @media (max-width: 480px) {
        .nexus-cinematic-banner {
            padding: 14px 14px;
            border-radius: 14px;
        }
        .hero-title {
            font-size: 1.2rem;
            margin: 3px 0 5px 0;
        }
        .meta-badge {
            font-size: 0.65rem;
            padding: 2px 8px;
        }
        .meta-class {
            font-size: 0.72rem;
        }
        .text-container {
            font-size: 0.84rem;
            line-height: 1.45;
        }
    }
</style>
</head>
<body>
    <div class="nexus-cinematic-banner">
        <div class="glow-orb-1"></div>
        <div class="glow-orb-2"></div>
        
        <div class="meta-wrapper">
            <span class="meta-badge">⚡ NEXUS ECOSYSTEM</span>
            <span class="meta-class">__CLASS__ • __BOARD__</span>
        </div>
        
        <h1 class="hero-title">Welcome to Nexus Student Dashboard</h1>
        
        <div class="text-container">
            <span id="nexus-anim-text" style="color: #F8FAFC; transition: all 0.2s ease;"></span>
            <span id="nexus-cursor"></span>
        </div>
    </div>

    <script>
        var textEl = document.getElementById('nexus-anim-text');
        var cursorEl = document.getElementById('nexus-cursor');

        var phrase1 = "Made by Ammaar Akhtar with love and hope ❤️✨";
        var phrase2 = "Welcome __NAME__! Nexus is created for your journey in __CLASS__ (__BOARD__) to master every chapter, track your progress seamlessly, and conquer your exams with confidence.\\n\\n“Your potential is limitless, __NAME__. Every single page you study today builds the victory of tomorrow. Believe in yourself, stay unstoppable, and achieve the greatness you are destined for!” 🚀🔥📖";

        function syncHeight() {
            try {
                if (window.frameElement) {
                    var bannerEl = document.querySelector('.nexus-cinematic-banner');
                    var h = bannerEl ? (bannerEl.offsetHeight + 10) : document.body.scrollHeight;
                    if (h > 120) {
                        window.frameElement.style.height = h + 'px';
                        if (window.frameElement.parentElement) {
                            window.frameElement.parentElement.style.height = h + 'px';
                        }
                    }
                }
            } catch(e) {}
        }

        function typeString(str, speed, onDone) {
            var idx = 0;
            textEl.innerHTML = "";
            var interval = setInterval(function() {
                if (idx < str.length) {
                    if (str.substr(idx, 4) === "\\n\\n") {
                        textEl.innerHTML += "<br><br>";
                        idx += 4;
                    } else if (str[idx] === "\\n") {
                        textEl.innerHTML += "<br>";
                        idx++;
                    } else {
                        textEl.innerHTML += str[idx];
                        idx++;
                    }
                    if (idx % 12 === 0) {
                        syncHeight();
                    }
                } else {
                    clearInterval(interval);
                    syncHeight();
                    if (onDone) onDone();
                }
            }, speed);
        }

        function eraseString(speed, onDone) {
            var interval = setInterval(function() {
                var html = textEl.innerHTML;
                if (html.endsWith("<br><br>")) {
                    textEl.innerHTML = html.substring(0, html.length - 8);
                } else if (html.endsWith("<br>")) {
                    textEl.innerHTML = html.substring(0, html.length - 4);
                } else if (html.length > 0) {
                    textEl.innerHTML = html.substring(0, html.length - 1);
                } else {
                    clearInterval(interval);
                    syncHeight();
                    if (onDone) onDone();
                }
            }, speed);
        }

        window.addEventListener('load', syncHeight);
        window.addEventListener('resize', syncHeight);
        if (window.ResizeObserver) {
            new ResizeObserver(syncHeight).observe(document.body);
        }

        setTimeout(function() {
            syncHeight();
            typeString(phrase1, 38, function() {
                textEl.style.color = "#38BDF8";
                textEl.style.textShadow = "0 0 14px rgba(56, 189, 248, 0.6)";
                
                setTimeout(function() {
                    textEl.style.color = "#F8FAFC";
                    textEl.style.textShadow = "none";
                    eraseString(20, function() {
                        setTimeout(function() {
                            typeString(phrase2, 22, function() {
                                if (cursorEl) {
                                    cursorEl.style.animation = "nexusBlink 1.2s infinite";
                                }
                                syncHeight();
                            });
                        }, 250);
                    });
                }, 2000);
            });
        }, 200);
    </script>
</body>
</html>
"""

    rendered_html = html_code.replace("__BG__", bg)\
                             .replace("__BORDER__", border)\
                             .replace("__SHADOW__", shadow)\
                             .replace("__NAME__", clean_name)\
                             .replace("__CLASS__", clean_class)\
                             .replace("__BOARD__", clean_board)

    # Safe responsive fallback height: 320px for mobile/tablet, dynamically shrunk or expanded via syncHeight()
    components.html(rendered_html, height=320)


def render_welcome_splash_screen(user_name: str, class_name: str = "Class 10", board: str = "CBSE", theme: str = "Light"):
    """
    Renders an exhilarating, fullscreen welcome screen after login, signup, or setup:
    'Welcome to Nexus Student Dashboard <name of the user>'
    """
    is_dark = (theme.strip().lower() == "dark")
    bg = "linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 50%, rgba(15, 23, 42, 0.98) 100%)" if is_dark else "linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #1E293B 100%)"
    border = "rgba(56, 189, 248, 0.4)" if is_dark else "rgba(99, 102, 241, 0.4)"
    shadow = "0 20px 50px -10px rgba(0, 0, 0, 0.6), 0 0 30px rgba(56, 189, 248, 0.2)" if is_dark else "0 20px 50px -10px rgba(79, 70, 229, 0.4)"
    
    clean_name = str(user_name or "Student").strip()
    clean_class = str(class_name or "Class 10").strip()
    clean_board = str(board or "CBSE").strip()
    
    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
        background: transparent;
        overflow-x: hidden;
        overflow-y: auto;
        font-family: 'Plus Jakarta Sans', sans-serif;
        width: 100%;
        margin: 0;
        padding: 0;
    }}
    
    .splash-card {{
        background: {bg};
        border: 1px solid {border};
        border-radius: 22px;
        padding: 26px 22px;
        text-align: center;
        box-shadow: {shadow};
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .glow-bg {{
        position: absolute; top: -50px; left: 50%; transform: translateX(-50%);
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none;
    }}
    
    .badge {{
        display: inline-block; background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.4); color: #38BDF8;
        font-size: clamp(0.68rem, 2.2vw, 0.78rem); font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; padding: 4px 12px; border-radius: 30px; margin-bottom: 12px;
        position: relative; z-index: 1;
    }}
    
    .title {{
        font-family: 'Outfit', sans-serif;
        font-size: clamp(1.3rem, 4.5vw, 2.15rem);
        font-weight: 900;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.25;
        margin-bottom: 10px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        position: relative; z-index: 1;
    }}
    
    .user-highlight {{
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .sub {{
        color: #CBD5E1;
        font-size: clamp(0.88rem, 2.8vw, 1.02rem);
        line-height: 1.55;
        max-width: 620px;
        margin: 0 auto;
        font-weight: 500;
        word-wrap: break-word;
        overflow-wrap: break-word;
        position: relative; z-index: 1;
    }}

    @media (max-width: 768px) {{
        .splash-card {{
            padding: 20px 16px;
            border-radius: 16px;
        }}
    }}
</style>
</head>
<body>
    <div class="splash-card">
        <div class="glow-bg"></div>
        <div class="badge">✨ ACCOUNT READY • WELCOME TO NEXUS</div>
        <h1 class="title">Welcome to Nexus Student Dashboard, <span class="user-highlight">{clean_name}</span>! 🎉</h1>
        <p class="sub">Your personalized {clean_class} ({clean_board}) curriculum, study plan, and exam countdown are initialized. Let's make this your most victorious academic year yet!</p>
    </div>

    <script>
        function syncSplashHeight() {{
            try {{
                if (window.frameElement) {{
                    var cardEl = document.querySelector('.splash-card');
                    var h = cardEl ? (cardEl.offsetHeight + 10) : document.body.scrollHeight;
                    if (h > 120) {{
                        window.frameElement.style.height = h + 'px';
                        if (window.frameElement.parentElement) {{
                            window.frameElement.parentElement.style.height = h + 'px';
                        }}
                    }}
                }}
            }} catch(e) {{}}
        }}

        window.addEventListener('load', syncSplashHeight);
        window.addEventListener('resize', syncSplashHeight);
        if (window.ResizeObserver) {{
            new ResizeObserver(syncSplashHeight).observe(document.body);
        }}
        setTimeout(syncSplashHeight, 150);
    </script>
</body>
</html>
"""
    components.html(html_code, height=270)







