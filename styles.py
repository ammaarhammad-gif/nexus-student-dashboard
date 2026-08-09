"""
styles.py — Custom CSS theming engine for the Nexus Student Dashboard.

Supports:
1. ☀️ Light Theme — Ultra-clean, modern, high-contrast, beautiful soft shadows.
2. 🌙 Dark Theme — Futuristic glassmorphism, deep slate/navy, glowing cyber accents, vivid text.
3. 🖼️ Dynamic Wallpaper Palettes — 20 bespoke color schemes tailored perfectly to each wallpaper's mood and tones.
"""

import streamlit as st


# ══════════════════════════════════════════════════════════════════════════
# DEFAULT PALETTES
# ══════════════════════════════════════════════════════════════════════════
DEFAULT_DARK_PALETTE = {
    "accent": "#38BDF8",
    "accent_sub": "#818CF8",
    "card_bg": "rgba(15, 23, 42, 0.70)",
    "card_border": "rgba(255, 255, 255, 0.14)",
    "card_hover_border": "#38BDF8",
    "text_title": "#FFFFFF",
    "text_main": "#F8FAFC",
    "text_sub": "#94A3B8",
    "text_muted": "#64748B",
    "sidebar_bg": "linear-gradient(180deg, rgba(9, 13, 22, 0.84) 0%, rgba(15, 23, 42, 0.88) 100%)",
    "expander_bg": "rgba(15, 23, 42, 0.62)",
    "input_bg": "rgba(19, 27, 46, 0.88)",
    "btn_gradient": "linear-gradient(135deg, #6366F1 0%, #0284C7 100%)",
    "glow": "rgba(56, 189, 248, 0.35)"
}

DEFAULT_LIGHT_PALETTE = {
    "accent": "#4F46E5",
    "accent_sub": "#0284C7",
    "card_bg": "rgba(255, 255, 255, 0.72)",
    "card_border": "#E2E8F0",
    "card_hover_border": "#4F46E5",
    "text_title": "#0F172A",
    "text_main": "#0F172A",
    "text_sub": "#64748B",
    "text_muted": "#94A3B8",
    "sidebar_bg": "linear-gradient(180deg, rgba(255, 255, 255, 0.86) 0%, rgba(248, 250, 252, 0.92) 100%)",
    "expander_bg": "rgba(255, 255, 255, 0.72)",
    "input_bg": "rgba(255, 255, 255, 0.95)",
    "btn_gradient": "linear-gradient(135deg, #4F46E5 0%, #0284C7 100%)",
    "glow": "rgba(79, 70, 229, 0.25)"
}


# ══════════════════════════════════════════════════════════════════════════
# 20 CURATED AESTHETIC HIGH-RES WALLPAPERS WITH BESPOKE PALETTES
# ══════════════════════════════════════════════════════════════════════════
WALLPAPER_PRESETS = [
    {
        "id": "cosmic_nebula",
        "name": "🌌 Cosmic Nebula",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#818CF8",
            "accent_sub": "#38BDF8",
            "card_bg": "rgba(13, 16, 38, 0.70)",
            "card_border": "rgba(129, 140, 248, 0.24)",
            "card_hover_border": "#818CF8",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#C7D2FE",
            "text_muted": "#818CF8",
            "sidebar_bg": "linear-gradient(180deg, rgba(9, 11, 28, 0.84) 0%, rgba(15, 18, 42, 0.88) 100%)",
            "expander_bg": "rgba(15, 18, 42, 0.62)",
            "input_bg": "rgba(15, 18, 42, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #6366F1 0%, #38BDF8 100%)",
            "glow": "rgba(129, 140, 248, 0.40)"
        }
    },
    {
        "id": "cyberpunk_city",
        "name": "🏙️ Cyberpunk Neo-Tokyo",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#F43F5E",
            "accent_sub": "#06B6D4",
            "card_bg": "rgba(18, 12, 30, 0.72)",
            "card_border": "rgba(244, 63, 94, 0.28)",
            "card_hover_border": "#F43F5E",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#FECDD3",
            "text_muted": "#F43F5E",
            "sidebar_bg": "linear-gradient(180deg, rgba(14, 8, 24, 0.85) 0%, rgba(24, 12, 38, 0.90) 100%)",
            "expander_bg": "rgba(24, 12, 38, 0.64)",
            "input_bg": "rgba(24, 12, 38, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #F43F5E 0%, #8B5CF6 50%, #06B6D4 100%)",
            "glow": "rgba(244, 63, 94, 0.40)"
        }
    },
    {
        "id": "alpine_forest",
        "name": "🌄 Misty Nordic Forest",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#10B981",
            "accent_sub": "#34D399",
            "card_bg": "rgba(10, 24, 20, 0.72)",
            "card_border": "rgba(16, 185, 129, 0.25)",
            "card_hover_border": "#34D399",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#A7F3D0",
            "text_muted": "#6EE7B7",
            "sidebar_bg": "linear-gradient(180deg, rgba(6, 18, 15, 0.85) 0%, rgba(12, 30, 24, 0.90) 100%)",
            "expander_bg": "rgba(12, 30, 24, 0.62)",
            "input_bg": "rgba(12, 30, 24, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%)",
            "glow": "rgba(16, 185, 129, 0.40)"
        }
    },
    {
        "id": "mountain_alpenglow",
        "name": "🏔️ Snow Summit Alpenglow",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#FB7185",
            "accent_sub": "#F59E0B",
            "card_bg": "rgba(22, 14, 26, 0.72)",
            "card_border": "rgba(251, 113, 133, 0.25)",
            "card_hover_border": "#FB7185",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#FFE4E6",
            "text_muted": "#FDA4AF",
            "sidebar_bg": "linear-gradient(180deg, rgba(16, 9, 20, 0.85) 0%, rgba(28, 16, 32, 0.90) 100%)",
            "expander_bg": "rgba(28, 16, 32, 0.62)",
            "input_bg": "rgba(28, 16, 32, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #E11D48 0%, #FB7185 50%, #F59E0B 100%)",
            "glow": "rgba(251, 113, 133, 0.40)"
        }
    },
    {
        "id": "obsidian_wave",
        "name": "✨ Liquid Obsidian Wave",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#38BDF8",
            "accent_sub": "#94A3B8",
            "card_bg": "rgba(14, 19, 30, 0.74)",
            "card_border": "rgba(148, 163, 184, 0.24)",
            "card_hover_border": "#38BDF8",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#CBD5E1",
            "text_muted": "#94A3B8",
            "sidebar_bg": "linear-gradient(180deg, rgba(8, 12, 20, 0.85) 0%, rgba(16, 22, 34, 0.90) 100%)",
            "expander_bg": "rgba(16, 22, 34, 0.62)",
            "input_bg": "rgba(16, 22, 34, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #0284C7 0%, #38BDF8 100%)",
            "glow": "rgba(56, 189, 248, 0.40)"
        }
    },
    {
        "id": "midnight_library",
        "name": "📚 Midnight Grand Library",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#F59E0B",
            "accent_sub": "#FBBF24",
            "card_bg": "rgba(26, 18, 12, 0.74)",
            "card_border": "rgba(245, 158, 11, 0.28)",
            "card_hover_border": "#FBBF24",
            "text_title": "#FFFBEB",
            "text_main": "#FDFBF7",
            "text_sub": "#FDE68A",
            "text_muted": "#F59E0B",
            "sidebar_bg": "linear-gradient(180deg, rgba(18, 11, 7, 0.86) 0%, rgba(32, 21, 14, 0.92) 100%)",
            "expander_bg": "rgba(32, 21, 14, 0.65)",
            "input_bg": "rgba(32, 21, 14, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #D97706 0%, #F59E0B 50%, #FBBF24 100%)",
            "glow": "rgba(245, 158, 11, 0.40)"
        }
    },
    {
        "id": "golden_sunset",
        "name": "🌇 Golden Horizon Sunset",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#FB923C",
            "accent_sub": "#F59E0B",
            "card_bg": "rgba(28, 16, 12, 0.74)",
            "card_border": "rgba(251, 146, 60, 0.28)",
            "card_hover_border": "#FB923C",
            "text_title": "#FFF7ED",
            "text_main": "#FDFBF7",
            "text_sub": "#FED7AA",
            "text_muted": "#FB923C",
            "sidebar_bg": "linear-gradient(180deg, rgba(20, 10, 7, 0.86) 0%, rgba(34, 18, 14, 0.90) 100%)",
            "expander_bg": "rgba(34, 18, 14, 0.64)",
            "input_bg": "rgba(34, 18, 14, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #EA580C 0%, #FB923C 50%, #FBBF24 100%)",
            "glow": "rgba(251, 146, 60, 0.40)"
        }
    },
    {
        "id": "sakura_dawn",
        "name": "🌸 Sakura Blossom Dawn",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#F472B6",
            "accent_sub": "#FB7185",
            "card_bg": "rgba(26, 12, 22, 0.72)",
            "card_border": "rgba(244, 114, 182, 0.26)",
            "card_hover_border": "#F472B6",
            "text_title": "#FFF1F2",
            "text_main": "#FDFBF7",
            "text_sub": "#FBCFE8",
            "text_muted": "#F472B6",
            "sidebar_bg": "linear-gradient(180deg, rgba(18, 7, 15, 0.85) 0%, rgba(32, 14, 26, 0.90) 100%)",
            "expander_bg": "rgba(32, 14, 26, 0.62)",
            "input_bg": "rgba(32, 14, 26, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #DB2777 0%, #F472B6 50%, #FDA4AF 100%)",
            "glow": "rgba(244, 114, 182, 0.40)"
        }
    },
    {
        "id": "emerald_aurora",
        "name": "🌌 Emerald Aurora Borealis",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#2DD4BF",
            "accent_sub": "#4ADE80",
            "card_bg": "rgba(8, 24, 28, 0.72)",
            "card_border": "rgba(45, 212, 191, 0.26)",
            "card_hover_border": "#2DD4BF",
            "text_title": "#F0FDFA",
            "text_main": "#F8FAFC",
            "text_sub": "#99F6E4",
            "text_muted": "#2DD4BF",
            "sidebar_bg": "linear-gradient(180deg, rgba(5, 16, 20, 0.85) 0%, rgba(10, 30, 34, 0.90) 100%)",
            "expander_bg": "rgba(10, 30, 34, 0.62)",
            "input_bg": "rgba(10, 30, 34, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #0D9488 0%, #2DD4BF 50%, #4ADE80 100%)",
            "glow": "rgba(45, 212, 191, 0.40)"
        }
    },
    {
        "id": "matrix_terminal",
        "name": "💎 Matrix Cyber Terminal",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#22C55E",
            "accent_sub": "#86EFAC",
            "card_bg": "rgba(6, 22, 12, 0.75)",
            "card_border": "rgba(34, 197, 94, 0.30)",
            "card_hover_border": "#4ADE80",
            "text_title": "#F0FDF4",
            "text_main": "#F8FAFC",
            "text_sub": "#BBF7D0",
            "text_muted": "#4ADE80",
            "sidebar_bg": "linear-gradient(180deg, rgba(4, 15, 8, 0.86) 0%, rgba(8, 28, 16, 0.92) 100%)",
            "expander_bg": "rgba(8, 28, 16, 0.65)",
            "input_bg": "rgba(8, 28, 16, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #16A34A 0%, #22C55E 50%, #86EFAC 100%)",
            "glow": "rgba(34, 197, 94, 0.40)"
        }
    },
    {
        "id": "deep_ocean",
        "name": "🌊 Deep Ocean Twilight",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1682687220063-4742bd7fd538?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1682687220063-4742bd7fd538?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#38BDF8",
            "accent_sub": "#0284C7",
            "card_bg": "rgba(10, 22, 38, 0.72)",
            "card_border": "rgba(56, 189, 248, 0.25)",
            "card_hover_border": "#38BDF8",
            "text_title": "#F0F9FF",
            "text_main": "#F8FAFC",
            "text_sub": "#BAE6FD",
            "text_muted": "#38BDF8",
            "sidebar_bg": "linear-gradient(180deg, rgba(6, 14, 26, 0.85) 0%, rgba(12, 28, 48, 0.90) 100%)",
            "expander_bg": "rgba(12, 28, 48, 0.62)",
            "input_bg": "rgba(12, 28, 48, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #0284C7 0%, #38BDF8 100%)",
            "glow": "rgba(56, 189, 248, 0.40)"
        }
    },
    {
        "id": "pastel_clouds",
        "name": "☁️ Pastel Cloud Reverie",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#C084FC",
            "accent_sub": "#E879F9",
            "card_bg": "rgba(22, 14, 34, 0.72)",
            "card_border": "rgba(192, 132, 252, 0.26)",
            "card_hover_border": "#C084FC",
            "text_title": "#FAF5FF",
            "text_main": "#F8FAFC",
            "text_sub": "#E9D5FF",
            "text_muted": "#C084FC",
            "sidebar_bg": "linear-gradient(180deg, rgba(14, 8, 22, 0.85) 0%, rgba(26, 16, 40, 0.90) 100%)",
            "expander_bg": "rgba(26, 16, 40, 0.62)",
            "input_bg": "rgba(26, 16, 40, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #9333EA 0%, #C084FC 50%, #E879F9 100%)",
            "glow": "rgba(192, 132, 252, 0.40)"
        }
    },
    {
        "id": "zen_minimal",
        "name": "🏛️ Zen Minimalist Studio",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#94A3B8",
            "accent_sub": "#CBD5E1",
            "card_bg": "rgba(18, 22, 28, 0.75)",
            "card_border": "rgba(148, 163, 184, 0.22)",
            "card_hover_border": "#CBD5E1",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#CBD5E1",
            "text_muted": "#94A3B8",
            "sidebar_bg": "linear-gradient(180deg, rgba(11, 14, 18, 0.85) 0%, rgba(20, 26, 34, 0.90) 100%)",
            "expander_bg": "rgba(20, 26, 34, 0.62)",
            "input_bg": "rgba(20, 26, 34, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #475569 0%, #64748B 100%)",
            "glow": "rgba(148, 163, 184, 0.30)"
        }
    },
    {
        "id": "synthwave_grid",
        "name": "⚡ Synthwave Neon Grid",
        "category": "🏙️ Cyber & Neon",
        "url": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#E879F9",
            "accent_sub": "#F43F5E",
            "card_bg": "rgba(22, 10, 32, 0.74)",
            "card_border": "rgba(232, 121, 249, 0.28)",
            "card_hover_border": "#E879F9",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#F5D0FE",
            "text_muted": "#E879F9",
            "sidebar_bg": "linear-gradient(180deg, rgba(14, 6, 22, 0.85) 0%, rgba(28, 12, 40, 0.90) 100%)",
            "expander_bg": "rgba(28, 12, 40, 0.62)",
            "input_bg": "rgba(28, 12, 40, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #C026D3 0%, #E879F9 50%, #F43F5E 100%)",
            "glow": "rgba(232, 121, 249, 0.40)"
        }
    },
    {
        "id": "coastal_sunset",
        "name": "🍂 Golden Coastal Shore",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#F59E0B",
            "accent_sub": "#06B6D4",
            "card_bg": "rgba(14, 24, 30, 0.72)",
            "card_border": "rgba(245, 158, 11, 0.25)",
            "card_hover_border": "#F59E0B",
            "text_title": "#FFFBEB",
            "text_main": "#FDFBF7",
            "text_sub": "#FEF08A",
            "text_muted": "#F59E0B",
            "sidebar_bg": "linear-gradient(180deg, rgba(8, 16, 20, 0.85) 0%, rgba(18, 30, 38, 0.90) 100%)",
            "expander_bg": "rgba(18, 30, 38, 0.62)",
            "input_bg": "rgba(18, 30, 38, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #D97706 0%, #F59E0B 50%, #06B6D4 100%)",
            "glow": "rgba(245, 158, 11, 0.40)"
        }
    },
    {
        "id": "starlight_odyssey",
        "name": "🪐 Andromeda Galaxy Stars",
        "category": "🌌 Space & Sci-Fi",
        "url": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#A855F7",
            "accent_sub": "#38BDF8",
            "card_bg": "rgba(16, 12, 34, 0.72)",
            "card_border": "rgba(168, 85, 247, 0.26)",
            "card_hover_border": "#A855F7",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#DDD6FE",
            "text_muted": "#A855F7",
            "sidebar_bg": "linear-gradient(180deg, rgba(10, 7, 24, 0.85) 0%, rgba(20, 14, 42, 0.90) 100%)",
            "expander_bg": "rgba(20, 14, 42, 0.62)",
            "input_bg": "rgba(20, 14, 42, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #7E22CE 0%, #A855F7 50%, #38BDF8 100%)",
            "glow": "rgba(168, 85, 247, 0.40)"
        }
    },
    {
        "id": "emerald_foliage",
        "name": "🌿 Tropical Emerald Foliage",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#10B981",
            "accent_sub": "#34D399",
            "card_bg": "rgba(8, 22, 16, 0.74)",
            "card_border": "rgba(16, 185, 129, 0.26)",
            "card_hover_border": "#34D399",
            "text_title": "#F0FDF4",
            "text_main": "#F8FAFC",
            "text_sub": "#A7F3D0",
            "text_muted": "#10B981",
            "sidebar_bg": "linear-gradient(180deg, rgba(5, 15, 10, 0.85) 0%, rgba(10, 28, 20, 0.90) 100%)",
            "expander_bg": "rgba(10, 28, 20, 0.62)",
            "input_bg": "rgba(10, 28, 20, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%)",
            "glow": "rgba(16, 185, 129, 0.40)"
        }
    },
    {
        "id": "lofi_study_desk",
        "name": "☕ Lofi Coffee & Focus Desk",
        "category": "📚 Study & Vibes",
        "url": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#D97706",
            "accent_sub": "#F59E0B",
            "card_bg": "rgba(26, 18, 12, 0.74)",
            "card_border": "rgba(217, 119, 6, 0.26)",
            "card_hover_border": "#F59E0B",
            "text_title": "#FFFBEB",
            "text_main": "#FDFBF7",
            "text_sub": "#FDE68A",
            "text_muted": "#D97706",
            "sidebar_bg": "linear-gradient(180deg, rgba(18, 11, 7, 0.86) 0%, rgba(32, 21, 14, 0.92) 100%)",
            "expander_bg": "rgba(32, 21, 14, 0.65)",
            "input_bg": "rgba(32, 21, 14, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #B45309 0%, #D97706 50%, #F59E0B 100%)",
            "glow": "rgba(217, 119, 6, 0.40)"
        }
    },
    {
        "id": "prism_spectrum",
        "name": "🔮 Prism Refraction Waves",
        "category": "✨ Abstract",
        "url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#818CF8",
            "accent_sub": "#EC4899",
            "card_bg": "rgba(18, 14, 36, 0.72)",
            "card_border": "rgba(129, 140, 248, 0.26)",
            "card_hover_border": "#818CF8",
            "text_title": "#FFFFFF",
            "text_main": "#F8FAFC",
            "text_sub": "#E0E7FF",
            "text_muted": "#818CF8",
            "sidebar_bg": "linear-gradient(180deg, rgba(12, 8, 24, 0.85) 0%, rgba(22, 16, 44, 0.90) 100%)",
            "expander_bg": "rgba(22, 16, 44, 0.62)",
            "input_bg": "rgba(22, 16, 44, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #6366F1 0%, #818CF8 50%, #EC4899 100%)",
            "glow": "rgba(129, 140, 248, 0.40)"
        }
    },
    {
        "id": "midnight_dunes",
        "name": "🌙 Moonlit Sahara Dunes",
        "category": "🌿 Nature & Calm",
        "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=2560&q=90",
        "thumb": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=400&q=75",
        "palette": {
            "accent": "#EAB308",
            "accent_sub": "#38BDF8",
            "card_bg": "rgba(22, 20, 14, 0.74)",
            "card_border": "rgba(234, 179, 8, 0.26)",
            "card_hover_border": "#EAB308",
            "text_title": "#FEF9C3",
            "text_main": "#FDFBF7",
            "text_sub": "#FEF08A",
            "text_muted": "#EAB308",
            "sidebar_bg": "linear-gradient(180deg, rgba(15, 13, 9, 0.86) 0%, rgba(28, 24, 16, 0.90) 100%)",
            "expander_bg": "rgba(28, 24, 16, 0.64)",
            "input_bg": "rgba(28, 24, 16, 0.90)",
            "btn_gradient": "linear-gradient(135deg, #CA8A04 0%, #EAB308 50%, #38BDF8 100%)",
            "glow": "rgba(234, 179, 8, 0.40)"
        }
    }
]


def get_wallpaper_palette(preset_id: str = None, wallpaper_url: str = None) -> dict:
    """Finds the tailored color palette for the active wallpaper preset or URL."""
    if preset_id:
        for p in WALLPAPER_PRESETS:
            if p["id"] == preset_id:
                return p["palette"]
    if wallpaper_url:
        for p in WALLPAPER_PRESETS:
            if p["url"] in wallpaper_url or wallpaper_url in p["url"]:
                return p["palette"]
    return DEFAULT_DARK_PALETTE


def apply_custom_css(theme: str = "Dark", wallpaper_url: str = None, wallpaper_blur: int = 0, overlay_opacity: float = 0.30, preset_id: str = None):
    """
    Injects the complete CSS theme (Light or Dark) and optional glassmorphism wallpaper into the Streamlit app.
    Automatically applies bespoke text colors, button gradients, and borders matching each wallpaper aesthetic.
    """
    is_dark = (theme.strip().lower() == "dark")
    has_wallpaper = bool(wallpaper_url and str(wallpaper_url).strip())
    
    if is_dark:
        palette = get_wallpaper_palette(preset_id=preset_id, wallpaper_url=wallpaper_url) if has_wallpaper else DEFAULT_DARK_PALETTE
        
        card_bg = palette["card_bg"] if has_wallpaper else "rgba(19, 27, 46, 0.92)"
        sidebar_bg = palette["sidebar_bg"] if has_wallpaper else "linear-gradient(180deg, #090D16 0%, #0F172A 100%)"
        expander_bg = palette["expander_bg"] if has_wallpaper else "rgba(19, 27, 46, 0.85)"
        
        theme_vars = f"""
        :root {{
            --nexus-bg: {'transparent' if has_wallpaper else '#0B0F19'};
            --nexus-card-bg: {card_bg};
            --nexus-card-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.13)"};
            --nexus-card-hover-border: {palette["card_hover_border"]};
            --nexus-accent: {palette["accent"]};
            --nexus-accent-sub: {palette["accent_sub"]};
            --nexus-text-main: {palette["text_main"]};
            --nexus-text-title: {palette["text_title"]};
            --nexus-text-sub: {palette["text_sub"]};
            --nexus-text-muted: {palette["text_muted"]};
            --nexus-input-bg: {palette["input_bg"]};
            --nexus-input-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.18)"};
            --nexus-input-text: {palette["text_title"]};
            --nexus-sidebar-bg: {sidebar_bg};
            --nexus-sidebar-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.1)"};
            --nexus-expander-bg: {expander_bg};
            --nexus-expander-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.12)"};
            --nexus-tab-bg: rgba(15, 23, 42, 0.6);
            --nexus-tab-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.08)"};
            --nexus-btn-bg: #1E293B;
            --nexus-btn-text: {palette["text_title"]};
            --nexus-btn-border: {palette["card_border"] if has_wallpaper else "rgba(255, 255, 255, 0.15)"};
            --nexus-btn-gradient: {palette["btn_gradient"]};
            --nexus-glow: {palette["glow"]};
        }}
        """
        
        if has_wallpaper:
            blur_rule = f"filter: blur({wallpaper_blur}px) brightness(0.96) !important;" if wallpaper_blur > 0 else "filter: brightness(0.96) !important;"
            wallpaper_css = f"""
            .stApp::before, [data-testid="stAppViewContainer"]::before {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background-image: url('{wallpaper_url}') !important;
                background-size: cover !important; background-position: center center !important;
                background-repeat: no-repeat !important; background-attachment: fixed !important;
                {blur_rule}
                image-rendering: -webkit-optimize-contrast !important;
                image-rendering: high-quality !important;
                z-index: -2 !important; pointer-events: none !important;
            }}
            .stApp::after, [data-testid="stAppViewContainer"]::after {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background: rgba(11, 15, 25, {overlay_opacity}) !important;
                z-index: -1 !important; pointer-events: none !important;
            }}
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], section.main, .block-container, [data-testid="stMainBlockContainer"], .stMain {{
                background-color: transparent !important;
                background: transparent !important;
            }}
            .nexus-card, div[data-testid="stMetric"], details[data-testid="stExpander"], div[data-testid="stForm"] {{
                backdrop-filter: blur(14px) saturate(170%) !important;
                -webkit-backdrop-filter: blur(14px) saturate(170%) !important;
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
            color: var(--nexus-text-main) !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: var(--nexus-text-title) !important;
        }

        p, span, label, div {
            color: var(--nexus-text-main);
        }

        .caption, small, [data-testid="stCaptionContainer"] {
            color: var(--nexus-text-sub) !important;
        }

        strong, b {
            color: var(--nexus-text-title) !important;
            font-weight: 600;
        }

        /* Sidebar Dark */
        section[data-testid="stSidebar"] {
            background: var(--nexus-sidebar-bg) !important;
            border-right: 1px solid var(--nexus-sidebar-border) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            background: rgba(30, 41, 59, 0.65) !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 12px !important;
            padding: 10px 16px !important;
            margin-bottom: 8px !important;
            transition: all 0.2s ease !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(30, 41, 59, 0.90) !important;
            border-color: var(--nexus-accent) !important;
            transform: translateX(4px);
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: var(--nexus-btn-gradient) !important;
            border: 1px solid var(--nexus-accent) !important;
            box-shadow: 0 4px 16px var(--nexus-glow) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] p {
            color: var(--nexus-text-title) !important;
            font-weight: 600 !important;
        }

        /* Inputs & Controls Dark */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
            background-color: var(--nexus-input-bg) !important;
            color: var(--nexus-text-title) !important;
            border: 1px solid var(--nexus-input-border) !important;
            border-radius: 10px !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
            border-color: var(--nexus-accent) !important;
            box-shadow: 0 0 0 3px var(--nexus-glow) !important;
        }

        /* Selectbox Container */
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] > div {
            background-color: var(--nexus-input-bg) !important;
            color: var(--nexus-text-title) !important;
            border: 1px solid var(--nexus-input-border) !important;
            border-radius: 10px !important;
        }

        .stSelectbox [data-baseweb="select"] div,
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] p {
            color: var(--nexus-text-title) !important;
        }

        /* BaseWeb Selectbox Dropdown Popover & Listbox Dark Mode */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        div[data-baseweb="layer"] div[data-baseweb="popover"],
        div[data-baseweb="layer"] div[data-baseweb="menu"],
        ul[role="listbox"],
        ul[data-baseweb="menu"] {
            background-color: #0F172A !important;
            background: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 12px !important;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.8) !important;
            overflow: hidden !important;
        }

        li[role="option"],
        li[data-baseweb="menu-item"],
        [data-baseweb="menu"] li,
        ul[role="listbox"] li {
            background-color: #0F172A !important;
            background: #0F172A !important;
            color: #F8FAFC !important;
            padding: 10px 14px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        li[role="option"] *,
        li[data-baseweb="menu-item"] *,
        [data-baseweb="menu"] li *,
        ul[role="listbox"] li * {
            background-color: transparent !important;
            background: transparent !important;
            color: #F8FAFC !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"],
        li[data-baseweb="menu-item"]:hover,
        ul[role="listbox"] li:hover {
            background-color: rgba(56, 189, 248, 0.22) !important;
            background: rgba(56, 189, 248, 0.22) !important;
            color: var(--nexus-accent) !important;
        }

        li[role="option"]:hover *,
        li[role="option"][aria-selected="true"] *,
        ul[role="listbox"] li:hover * {
            color: var(--nexus-accent) !important;
            font-weight: 600 !important;
        }

        /* Expanders Dark */
        details[data-testid="stExpander"],
        div[data-testid="stExpander"] {
            background: var(--nexus-expander-bg) !important;
            border: 1px solid var(--nexus-expander-border) !important;
            border-radius: 14px !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            overflow: hidden !important;
            margin-bottom: 10px !important;
        }

        details[data-testid="stExpander"] > summary,
        details[data-testid="stExpander"] summary,
        .streamlit-expanderHeader,
        summary.streamlit-expanderHeader {
            background: var(--nexus-card-bg) !important;
            color: var(--nexus-text-title) !important;
            font-weight: 600 !important;
            border-bottom: 1px solid var(--nexus-card-border) !important;
            padding: 12px 16px !important;
        }

        details[data-testid="stExpander"] summary *,
        .streamlit-expanderHeader * {
            color: var(--nexus-text-title) !important;
        }

        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover {
            background: rgba(30, 41, 59, 0.95) !important;
            color: var(--nexus-accent) !important;
        }

        details[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background: transparent !important;
            color: var(--nexus-text-main) !important;
            padding: 14px 16px !important;
        }

        /* Popovers Dark (Trigger Buttons & Body) */
        div[data-testid="stPopover"],
        div[data-testid="stPopover"] > button,
        div[data-testid="stPopover"] button {
            background: #1E293B !important;
            background-color: #1E293B !important;
            color: var(--nexus-text-title) !important;
            border: 1px solid var(--nexus-btn-border) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.2s ease !important;
            font-weight: 600 !important;
        }

        div[data-testid="stPopover"] > button *,
        div[data-testid="stPopover"] button * {
            color: var(--nexus-text-title) !important;
        }

        div[data-testid="stPopover"] > button:hover,
        div[data-testid="stPopover"] button:hover {
            background: #334155 !important;
            background-color: #334155 !important;
            border-color: var(--nexus-accent) !important;
            color: var(--nexus-accent) !important;
            box-shadow: 0 4px 14px var(--nexus-glow) !important;
        }

        div[data-testid="stPopover"] > button:hover *,
        div[data-testid="stPopover"] button:hover * {
            color: var(--nexus-accent) !important;
        }

        div[data-testid="stPopoverBody"],
        div[data-testid="stPopoverContent"],
        div[data-testid="stPopoverBody"] > div {
            background-color: #0F172A !important;
            background: #0F172A !important;
            color: #F8FAFC !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 14px !important;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8) !important;
            padding: 16px !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid var(--nexus-tab-border) !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--nexus-text-sub) !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(30, 41, 59, 0.9) !important;
            color: var(--nexus-accent) !important;
            border: 1px solid var(--nexus-accent) !important;
            box-shadow: 0 0 12px var(--nexus-glow) !important;
        }

        /* Buttons Dark */
        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        button[data-testid="baseButton-secondary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="secondary"] {
            background: #1E293B !important;
            background-color: #1E293B !important;
            color: var(--nexus-text-main) !important;
            border: 1px solid var(--nexus-btn-border) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button *,
        div[data-testid="stFormSubmitButton"] > button *,
        div[data-testid="stDownloadButton"] > button *,
        button[data-testid="baseButton-secondary"] *,
        button[data-testid="stBaseButton-secondary"] *,
        button[kind="secondary"] * {
            color: var(--nexus-text-main) !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        button[kind="secondary"]:hover {
            background: #334155 !important;
            background-color: #334155 !important;
            border-color: var(--nexus-accent) !important;
            color: var(--nexus-accent) !important;
            box-shadow: 0 4px 14px var(--nexus-glow) !important;
        }

        .stButton > button:hover *,
        div[data-testid="stFormSubmitButton"] > button:hover *,
        button[data-testid="baseButton-secondary"]:hover *,
        button[data-testid="stBaseButton-secondary"]:hover * {
            color: var(--nexus-accent) !important;
        }

        .stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"],
        button[data-testid="baseButton-primary"],
        button[data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            background: var(--nexus-btn-gradient) !important;
            background-color: transparent !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 18px var(--nexus-glow) !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="primary"] *,
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
        button[data-testid="baseButton-primary"] *,
        button[data-testid="stBaseButton-primary"] * {
            color: #FFFFFF !important;
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
            --nexus-accent: #4F46E5;
            --nexus-accent-sub: #0284C7;
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
            --nexus-btn-gradient: linear-gradient(135deg, #4F46E5 0%, #0284C7 100%);
            --nexus-glow: rgba(79, 70, 229, 0.25);
        }}
        """
        
        if has_wallpaper:
            blur_rule = f"filter: blur({wallpaper_blur}px) brightness(0.96) !important;" if wallpaper_blur > 0 else "filter: brightness(0.96) !important;"
            wallpaper_css = f"""
            .stApp::before, [data-testid="stAppViewContainer"]::before {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background-image: url('{wallpaper_url}') !important;
                background-size: cover !important; background-position: center center !important;
                background-repeat: no-repeat !important; background-attachment: fixed !important;
                {blur_rule}
                image-rendering: -webkit-optimize-contrast !important;
                image-rendering: high-quality !important;
                z-index: -2 !important; pointer-events: none !important;
            }}
            .stApp::after, [data-testid="stAppViewContainer"]::after {{
                content: '' !important;
                position: fixed !important;
                top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important;
                background: rgba(248, 250, 252, {overlay_opacity}) !important;
                z-index: -1 !important; pointer-events: none !important;
            }}
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], section.main, .block-container, [data-testid="stMainBlockContainer"], .stMain {{
                background-color: transparent !important;
                background: transparent !important;
            }}
            .nexus-card, div[data-testid="stMetric"], details[data-testid="stExpander"], div[data-testid="stForm"] {{
                backdrop-filter: blur(14px) saturate(170%) !important;
                -webkit-backdrop-filter: blur(14px) saturate(170%) !important;
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

        /* Selectbox Container Light */
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }

        .stSelectbox [data-baseweb="select"] div,
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] p {
            color: #0F172A !important;
            font-weight: 500;
        }

        /* BaseWeb Selectbox Dropdown Popover & Listbox Light Mode */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        ul[role="listbox"],
        ul[data-baseweb="menu"] {
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08) !important;
            overflow: hidden !important;
        }

        li[role="option"],
        li[data-baseweb="menu-item"],
        [data-baseweb="menu"] li,
        ul[role="listbox"] li {
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            color: #0F172A !important;
            padding: 10px 14px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
            border-bottom: 1px solid #F1F5F9 !important;
        }

        li[role="option"] *,
        li[data-baseweb="menu-item"] *,
        [data-baseweb="menu"] li *,
        ul[role="listbox"] li * {
            background-color: transparent !important;
            background: transparent !important;
            color: #0F172A !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"],
        li[data-baseweb="menu-item"]:hover,
        ul[role="listbox"] li:hover {
            background-color: #EEF2FF !important;
            background: #EEF2FF !important;
            color: #4F46E5 !important;
        }

        li[role="option"]:hover *,
        li[role="option"][aria-selected="true"] *,
        ul[role="listbox"] li:hover * {
            color: #4F46E5 !important;
            font-weight: 600 !important;
        }

        /* Expanders Light */
        details[data-testid="stExpander"],
        div[data-testid="stExpander"] {
            background: var(--nexus-expander-bg) !important;
            border: 1px solid var(--nexus-expander-border) !important;
            border-radius: 14px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            overflow: hidden !important;
            margin-bottom: 10px !important;
        }

        details[data-testid="stExpander"] > summary,
        details[data-testid="stExpander"] summary,
        .streamlit-expanderHeader,
        summary.streamlit-expanderHeader {
            background: var(--nexus-card-bg) !important;
            color: #0F172A !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #E2E8F0 !important;
            padding: 12px 16px !important;
        }

        details[data-testid="stExpander"] summary *,
        .streamlit-expanderHeader * {
            color: #0F172A !important;
        }

        details[data-testid="stExpander"] summary:hover,
        .streamlit-expanderHeader:hover {
            background: #F1F5F9 !important;
            color: #4F46E5 !important;
        }

        details[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background: transparent !important;
            color: #334155 !important;
            padding: 14px 16px !important;
        }

        /* Popovers Light (Trigger Buttons & Body) */
        div[data-testid="stPopover"],
        div[data-testid="stPopover"] > button,
        div[data-testid="stPopover"] button {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.2s ease !important;
            font-weight: 600 !important;
        }

        div[data-testid="stPopover"] > button *,
        div[data-testid="stPopover"] button * {
            color: #0F172A !important;
        }

        div[data-testid="stPopover"] > button:hover,
        div[data-testid="stPopover"] button:hover {
            background: #F8FAFC !important;
            background-color: #F8FAFC !important;
            border-color: #4F46E5 !important;
            color: #4F46E5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
        }

        div[data-testid="stPopover"] > button:hover *,
        div[data-testid="stPopover"] button:hover * {
            color: #4F46E5 !important;
        }

        div[data-testid="stPopoverBody"],
        div[data-testid="stPopoverContent"],
        div[data-testid="stPopoverBody"] > div {
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12) !important;
            padding: 16px !important;
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

        /* Buttons Light */
        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        button[data-testid="baseButton-secondary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="secondary"] {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button *,
        div[data-testid="stFormSubmitButton"] > button *,
        div[data-testid="stDownloadButton"] > button *,
        button[data-testid="baseButton-secondary"] *,
        button[data-testid="stBaseButton-secondary"] *,
        button[kind="secondary"] * {
            color: #0F172A !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        button[kind="secondary"]:hover {
            border-color: #4F46E5 !important;
            color: #4F46E5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
        }

        .stButton > button:hover *,
        div[data-testid="stFormSubmitButton"] > button:hover *,
        button[data-testid="baseButton-secondary"]:hover *,
        button[data-testid="stBaseButton-secondary"]:hover * {
            color: #4F46E5 !important;
        }

        .stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"],
        button[data-testid="baseButton-primary"],
        button[data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #0284C7 100%) !important;
            background-color: transparent !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="primary"] *,
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
        button[data-testid="baseButton-primary"] *,
        button[data-testid="stBaseButton-primary"] * {
            color: #FFFFFF !important;
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

        /* Authentication Screen Premium Styling */
        .auth-hero-container {
            text-align: center;
            margin-bottom: 24px;
            padding-top: 15px;
        }

        .auth-brand-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38BDF8;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 5px 14px;
            border-radius: 30px;
            margin-bottom: 12px;
        }

        .auth-hero-title {
            font-family: 'Outfit', sans-serif !important;
            font-size: clamp(2.0rem, 5vw, 2.7rem) !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #FFFFFF 0%, #E0E7FF 50%, #38BDF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 8px 0 !important;
            letter-spacing: -0.02em;
        }

        .auth-hero-subtitle {
            font-size: clamp(0.9rem, 2.5vw, 1.02rem) !important;
            color: #94A3B8 !important;
            max-width: 520px;
            margin: 0 auto !important;
            line-height: 1.5;
        }

        .auth-feature-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(30, 41, 59, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #E2E8F0;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 8px 14px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }

        .nexus-card {
            background: var(--nexus-card-bg) !important;
            border: 1px solid var(--nexus-card-border) !important;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);
            backdrop-filter: blur(14px) saturate(170%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(170%) !important;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .nexus-card:hover {
            border-color: var(--nexus-card-hover-border) !important;
            box-shadow: 0 12px 30px -4px var(--nexus-glow);
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
            backdrop-filter: blur(14px) saturate(170%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(170%) !important;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
        }

        .metric-box:hover {
            border-color: var(--nexus-card-hover-border) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--nexus-glow);
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
            color: var(--nexus-accent) !important;
            text-shadow: 0 0 16px var(--nexus-glow);
        }

        .metric-sub {
            color: var(--nexus-text-muted) !important;
            font-size: 0.8rem;
            margin-top: 6px;
        }

        /* Custom Progress Bars */
        .stProgress > div > div > div > div {
            background-image: var(--nexus-btn-gradient) !important;
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
            background: var(--nexus-btn-gradient);
            border-radius: 16px;
            padding: 28px 34px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px var(--nexus-glow);
        }

        .welcome-banner h2 {
            color: #FFFFFF !important;
            margin: 0 0 6px 0 !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }

        .welcome-banner p {
            color: rgba(255, 255, 255, 0.92) !important;
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
    """Render a stylish page header with optional subtitle matching active wallpaper colors."""
    is_dark = (theme.strip().lower() == "dark")
    bg = "var(--nexus-expander-bg)" if is_dark else "linear-gradient(135deg, #FFFFFF, #F8FAFC)"
    border = "var(--nexus-card-border)" if is_dark else "#E2E8F0"
    title_color = "var(--nexus-text-title)" if is_dark else "#0F172A"
    sub_color = "var(--nexus-text-sub)" if is_dark else "#64748B"
    accent_border = "var(--nexus-accent)" if is_dark else "#4F46E5"

    st.markdown(f"""
        <div style="margin-bottom: 20px; padding: 16px 20px; background: {bg}; border-left: 5px solid {accent_border}; border-radius: 14px; box-shadow: 0 4px 18px rgba(0,0,0,{'0.35' if is_dark else '0.04'}); border-top: 1px solid {border}; border-right: 1px solid {border}; border-bottom: 1px solid {border}; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);">
            <h1 style="color: {title_color} !important; font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; font-size: clamp(1.35rem, 4vw, 2.1rem) !important; margin: 0 0 4px 0 !important; letter-spacing: -0.02em; line-height: 1.25;">{title}</h1>
            {f'<p style="color: {sub_color} !important; font-size: clamp(0.85rem, 2.5vw, 1.02rem) !important; margin: 0 !important; font-weight: 500; line-height: 1.45;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value, accent_color: str = None, subtitle: str = "", theme: str = "Light", **kwargs):
    """Render a single styled metric box."""
    accent = accent_color if accent_color else "var(--nexus-accent)"
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color: {accent};">{value}</div>
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
