"""
styles.py — Custom CSS theming engine for the Nexus Student Dashboard.

Supports:
1. ☀️ Light Theme (Default) — Ultra-clean, modern, high-contrast, beautiful soft shadows.
2. 🌙 Dark Theme — Futuristic glassmorphism, deep slate/navy, glowing cyber accents.
3. 💻 Default Theme — Automatically resolves to Light mode as standard default.
"""

import streamlit as st


def apply_custom_css(theme: str = "Light"):
    """Injects the complete CSS theme (Light, Dark, or Default) into the Streamlit app."""
    # Default maps to Light theme
    is_dark = (theme.strip().lower() == "dark")

    if is_dark:
        # ══════════════════════════════════════════════════════════════════════
        # 🌙 DARK THEME CSS
        # ══════════════════════════════════════════════════════════════════════
        theme_css = """
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #0B0F19 !important;
            color: #F8FAFC !important;
            -webkit-font-smoothing: antialiased;
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                        radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.06) 0%, transparent 40%);
            pointer-events: none;
            z-index: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        p, span, label, div {
            color: #E2E8F0;
        }

        .nexus-card {
            background: rgba(19, 27, 46, 0.85) !important;
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .nexus-card:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 16px 40px -10px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        .metric-box {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 14px;
            padding: 20px 18px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
        }

        .metric-box:hover {
            border-color: rgba(56, 189, 248, 0.5) !important;
            transform: translateY(-2px);
        }

        .metric-title {
            color: #94A3B8 !important;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif !important;
            color: #FFFFFF !important;
            font-size: 2.2rem;
            font-weight: 800;
        }

        .metric-sub {
            color: #64748B !important;
            font-size: 0.8rem;
            margin-top: 6px;
        }

        /* Sidebar Dark */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090D16 0%, #0F172A 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
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

        /* Inputs Dark */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            background-color: #131B2E !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
        }

        details[data-testid="stExpander"] {
            background: rgba(19, 27, 46, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 14px !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        .badge-not-started   { background-color: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.3); }
        .badge-in-progress   { background-color: rgba(234, 179, 8, 0.2);   color: #FDE047; border: 1px solid rgba(234, 179, 8, 0.4); }
        .badge-completed     { background-color: rgba(34, 197, 94, 0.2);   color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.4); }
        .badge-revision-done { background-color: rgba(59, 130, 246, 0.2);  color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); }
        """
    else:
        # ══════════════════════════════════════════════════════════════════════
        # ☀️ LIGHT THEME CSS (DEFAULT)
        # ══════════════════════════════════════════════════════════════════════
        theme_css = """
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            -webkit-font-smoothing: antialiased;
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.04) 0%, transparent 40%),
                        radial-gradient(circle at 90% 90%, rgba(2, 132, 199, 0.04) 0%, transparent 40%);
            pointer-events: none;
            z-index: 0;
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

        .nexus-card {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .nexus-card:hover {
            border-color: #CBD5E1 !important;
            box-shadow: 0 12px 30px -4px rgba(99, 102, 241, 0.12);
            transform: translateY(-2px);
        }

        .metric-box {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%) !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px;
            padding: 20px 18px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
        }

        .metric-box:hover {
            border-color: #6366F1 !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
        }

        .metric-title {
            color: #64748B !important;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif !important;
            color: #0F172A !important;
            font-size: 2.2rem;
            font-weight: 800;
        }

        .metric-sub {
            color: #94A3B8 !important;
            font-size: 0.8rem;
            margin-top: 6px;
        }

        /* Sidebar Light */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
            border-right: 1px solid #E2E8F0 !important;
            box-shadow: 2px 0 15px rgba(0, 0, 0, 0.03);
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
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        }

        .stSelectbox [data-baseweb="select"] div {
            color: #0F172A !important;
            font-weight: 500;
        }

        details[data-testid="stExpander"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
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
        @media (max-width: 768px) {
            .metric-box { padding: 14px 16px; margin-bottom: 10px; }
            .metric-value { font-size: 1.6rem !important; }
            .nexus-card { padding: 16px 18px; border-radius: 12px; }
            .welcome-banner { padding: 20px 20px; }
            .welcome-banner h2 { font-size: 1.4rem !important; }
            h1 { font-size: 1.8rem !important; }
            .setup-hero h1 { font-size: 2.2rem !important; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 100% !important; flex: 1 1 100% !important;
            }
        }
    """

    st.markdown(f"<style>{theme_css}\n{shared_css}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "", theme: str = "Light"):
    """Render a stylish page header with optional subtitle."""
    is_dark = (theme.strip().lower() == "dark")
    bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98))" if is_dark else "linear-gradient(135deg, #FFFFFF, #F8FAFC)"
    border = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"
    title_color = "#FFFFFF" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    st.markdown(f"""
        <div style="margin-bottom: 24px; padding: 18px 24px; background: {bg}; border-left: 5px solid #4F46E5; border-radius: 14px; box-shadow: 0 4px 18px rgba(0,0,0,{'0.3' if is_dark else '0.04'}); border-top: 1px solid {border}; border-right: 1px solid {border}; border-bottom: 1px solid {border};">
            <h1 style="color: {title_color} !important; font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; font-size: 2.1rem !important; margin: 0 0 4px 0 !important; letter-spacing: -0.02em;">{title}</h1>
            {f'<p style="color: {sub_color} !important; font-size: 1.02rem !important; margin: 0 !important; font-weight: 500;">{subtitle}</p>' if subtitle else ''}
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
