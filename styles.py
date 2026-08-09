"""
styles.py — Custom CSS theming for the Nexus Student Dashboard.

Applies a high-performance, dark futuristic glassmorphism theme with
crystal-clear typography, glowing neon accents, 60 FPS GPU-accelerated transitions,
and 100% visible, high-contrast colors across all pages and devices.
"""

import streamlit as st


def apply_custom_css():
    """Injects the complete polished CSS theme into the Streamlit app."""
    st.markdown("""
        <style>
        /* ═══════ Google Fonts ═══════ */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

        /* ═══════ Global Core & Reset ═══════ */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #0B0F19 !important;
            color: #F8FAFC !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }

        /* Subtle animated ambient gradient on main view */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                        radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.06) 0%, transparent 40%);
            pointer-events: none;
            z-index: 0;
        }

        /* ═══════ Typography ═══════ */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            color: #FFFFFF !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }

        p, span, label, div {
            color: #E2E8F0;
        }

        strong, b {
            color: #FFFFFF !important;
            font-weight: 600;
        }

        /* ═══════ Glassmorphism Cards ═══════ */
        .nexus-card {
            background: rgba(19, 27, 46, 0.85) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.05);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease, border-color 0.2s ease;
            will-change: transform;
            transform: translate3d(0, 0, 0);
        }

        .nexus-card:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 16px 40px -10px rgba(99, 102, 241, 0.2), 0 0 15px rgba(99, 102, 241, 0.1);
            transform: translateY(-2px);
        }

        /* ═══════ Metric Stat Boxes ═══════ */
        .metric-box {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 20px 18px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
            will-change: transform;
        }

        .metric-box:hover {
            border-color: rgba(56, 189, 248, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(56, 189, 248, 0.15);
        }

        .metric-title {
            color: #94A3B8 !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif !important;
            color: #FFFFFF;
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .metric-sub {
            color: #64748B;
            font-size: 0.8rem;
            margin-top: 6px;
            font-weight: 500;
        }

        /* ═══════ Status Badges ═══════ */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            border: 1px solid transparent;
        }

        .badge-not-started   { background-color: rgba(148, 163, 184, 0.15); color: #CBD5E1; border-color: rgba(148, 163, 184, 0.3); }
        .badge-in-progress   { background-color: rgba(234, 179, 8, 0.2);   color: #FDE047; border-color: rgba(234, 179, 8, 0.4); }
        .badge-completed     { background-color: rgba(34, 197, 94, 0.2);   color: #4ADE80; border-color: rgba(34, 197, 94, 0.4); }
        .badge-revision-done { background-color: rgba(59, 130, 246, 0.2);  color: #60A5FA; border-color: rgba(59, 130, 246, 0.4); }

        /* ═══════ Custom Progress Bars ═══════ */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #6366F1 0%, #38BDF8 50%, #22C55E 100%) !important;
            border-radius: 10px;
        }

        /* ═══════ High-Contrast Modern Sidebar ═══════ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090D16 0%, #0F172A 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            font-family: 'Outfit', sans-serif !important;
            color: #38BDF8 !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
        }

        /* Sidebar Navigation Radio Buttons */
        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 10px 16px !important;
            margin-bottom: 8px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(56, 189, 248, 0.15) !important;
            border-color: #38BDF8 !important;
            transform: translateX(4px);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] div,
        section[data-testid="stSidebar"] [data-baseweb="radio"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #F8FAFC !important;
        }

        /* Active Selected Radio Item */
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.85) 0%, rgba(56, 189, 248, 0.85) 100%) !important;
            border: 1px solid #38BDF8 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        /* ═══════ Form Controls & Streamlit Inputs ═══════ */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background-color: #131B2E !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            font-size: 0.95rem !important;
            transition: all 0.2s ease !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.4) !important;
            background-color: #1A243D !important;
        }

        .stSelectbox [data-baseweb="select"] {
            background-color: #131B2E !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: #FFFFFF !important;
        }

        .stSelectbox [data-baseweb="select"] div {
            color: #FFFFFF !important;
            font-weight: 500;
        }

        /* ═══════ Checkbox Styling (Touch & Visual) ═══════ */
        .stCheckbox {
            padding: 4px 0;
        }

        .stCheckbox label {
            font-size: 1rem !important;
            font-weight: 500 !important;
            color: #F8FAFC !important;
            cursor: pointer;
        }

        .stCheckbox label span[role="checkbox"] {
            background-color: #131B2E !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 6px !important;
            width: 20px !important;
            height: 20px !important;
            transition: all 0.2s ease !important;
        }

        .stCheckbox label span[role="checkbox"][aria-checked="true"] {
            background-color: #22C55E !important;
            border-color: #22C55E !important;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.4) !important;
        }

        /* ═══════ Buttons ═══════ */
        .stButton > button {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            padding: 8px 18px !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stButton > button:hover {
            border-color: #6366F1 !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
            transform: translateY(-1px) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366F1 0%, #38BDF8 100%) !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
        }

        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5) !important;
            transform: translateY(-2px) !important;
        }

        /* ═══════ Tabs Styling ═══════ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(15, 23, 42, 0.6);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(56, 189, 248, 0.3)) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
        }

        /* ═══════ Expanders / Accordion ═══════ */
        details[data-testid="stExpander"] {
            background: rgba(19, 27, 46, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 14px !important;
            margin-bottom: 12px !important;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            transition: border-color 0.2s ease;
        }

        details[data-testid="stExpander"]:hover {
            border-color: rgba(99, 102, 241, 0.3) !important;
        }

        details[data-testid="stExpander"] summary {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
            padding: 12px 18px !important;
        }

        /* ═══════ Welcome Banner ═══════ */
        .welcome-banner {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #06B6D4 100%);
            border-radius: 16px;
            padding: 28px 34px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 12px 35px rgba(79, 70, 229, 0.3);
        }

        .welcome-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
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

        /* ═══════ Setup Wizard Hero ═══════ */
        .setup-hero {
            text-align: center;
            padding: 40px 20px 20px 20px;
        }

        .setup-hero h1 {
            font-size: 3rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #38BDF8, #818CF8, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
        }

        /* ═══════ Custom Scrollbars ═══════ */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0B0F19;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.4);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(56, 189, 248, 0.6);
        }

        /* ═══════ Responsive Media Queries ═══════ */
        @media (max-width: 768px) {
            .metric-box {
                padding: 14px 16px;
                margin-bottom: 10px;
            }

            .metric-value {
                font-size: 1.6rem !important;
            }

            .nexus-card {
                padding: 16px 18px;
                border-radius: 12px;
            }

            .welcome-banner {
                padding: 20px 20px;
            }

            .welcome-banner h2 {
                font-size: 1.4rem !important;
            }

            h1 {
                font-size: 1.8rem !important;
            }

            .setup-hero h1 {
                font-size: 2.2rem !important;
            }

            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
            }

            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }
        }

        </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Render a stylish page header with optional subtitle."""
    st.markdown(f"""
        <div style="margin-bottom: 24px; padding: 18px 24px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98)); border-left: 5px solid #38BDF8; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.35); border-top: 1px solid rgba(255,255,255,0.06);">
            <h1 style="color: #FFFFFF !important; font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; font-size: 2.2rem !important; margin: 0 0 6px 0 !important; letter-spacing: -0.02em;">{title}</h1>
            {f'<p style="color: #94A3B8 !important; font-size: 1.05rem !important; margin: 0 !important; font-weight: 500;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value, accent_color: str = "#F8FAFC", subtitle: str = ""):
    """Render a single styled metric box."""
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color: {accent_color};">{value}</div>
            {f'<div class="metric-sub">{subtitle}</div>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)
