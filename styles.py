"""
styles.py — Custom CSS theming for the Nexus Student Dashboard.

Applies a modern dark futuristic theme with glassmorphism effects,
gradient cards, and polished typography using Google Fonts.
"""

import streamlit as st


def apply_custom_css():
    """Injects the complete CSS theme into the Streamlit app."""
    st.markdown("""
        <style>
        /* ═══════ Google Fonts ═══════ */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=Dancing+Script:wght@600;700&family=Caveat:wght@600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background-color: #0B0F19 !important;
            color: #F8FAFC !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
            color: #F8FAFC !important;
        }

        /* ═══════ Glassmorphism Card ═══════ */
        .nexus-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        .nexus-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        }

        /* ═══════ Gradient Stat Boxes ═══════ */
        .metric-box {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 14px;
            padding: 18px 20px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .metric-box:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
        }

        .metric-title {
            color: #94A3B8;
            font-size: 0.82rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif;
            color: #F8FAFC;
            font-size: 2.2rem;
            font-weight: 700;
        }

        .metric-sub {
            color: #64748B;
            font-size: 0.78rem;
            margin-top: 4px;
        }

        /* ═══════ Status Badges ═══════ */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .badge-not-started   { background-color: rgba(148, 163, 184, 0.2); color: #CBD5E1; }
        .badge-in-progress   { background-color: rgba(234, 179, 8, 0.2);   color: #FDE047; }
        .badge-completed     { background-color: rgba(34, 197, 94, 0.2);   color: #4ADE80; }
        .badge-revision-done { background-color: rgba(59, 130, 246, 0.2);  color: #60A5FA; }

        /* ═══════ Custom Progress Bars ═══════ */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #6366F1 0%, #A855F7 100%);
            border-radius: 10px;
        }

        /* ═══════ Sidebar High-Visibility & Cursive Typography ═══════ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090D16 0%, #0F172A 100%) !important;
            border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            font-family: 'Dancing Script', cursive !important;
            font-size: 2rem !important;
            color: #38BDF8 !important;
            text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
            letter-spacing: 1px;
            margin-top: 10px;
            margin-bottom: 12px;
        }

        /* Sidebar Radio Options Container */
        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            background: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
            padding: 8px 14px !important;
            margin-bottom: 8px !important;
            transition: all 0.25s ease-in-out !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(56, 189, 248, 0.2) !important;
            border-color: #38BDF8 !important;
            transform: translateX(4px);
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
        }

        /* Sidebar Radio Label Text */
        section[data-testid="stSidebar"] [data-baseweb="radio"] div,
        section[data-testid="stSidebar"] [data-baseweb="radio"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-family: 'Caveat', cursive !important;
            font-size: 1.45rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
        }

        /* Active Selected Radio Item */
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(168, 85, 247, 0.8) 100%) !important;
            border: 1px solid #F43F5E !important;
            box-shadow: 0 0 18px rgba(244, 63, 94, 0.5) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p {
            color: #FDE047 !important;
            font-size: 1.55rem !important;
            text-shadow: 0 0 8px rgba(253, 224, 71, 0.8) !important;
        }

        /* Sidebar Captions & Small Text */
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #7DD3FC !important;
            font-family: 'Caveat', cursive !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            opacity: 0.95 !important;
        }

        /* ═══════ Buttons ═══════ */
        .stButton > button {
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
        }

        /* ═══════ Expander Headers ═══════ */
        details[data-testid="stExpander"] summary {
            font-weight: 600;
        }

        /* ═══════ Welcome Banner ═══════ */
        .welcome-banner {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A855F7 100%);
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }

        .welcome-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        }

        .welcome-banner h2 {
            color: #FFFFFF;
            margin: 0 0 4px 0;
            font-size: 1.6rem;
        }

        .welcome-banner p {
            color: rgba(255, 255, 255, 0.8);
            margin: 0;
            font-size: 0.95rem;
        }

        /* ═══════ Setup Wizard ═══════ */
        .setup-hero {
            text-align: center;
            padding: 40px 20px 20px 20px;
        }

        .setup-hero h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #6366F1, #A855F7, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .setup-hero p {
            color: #94A3B8;
            font-size: 1.1rem;
        }

        /* ═══════ Subject Color Bar ═══════ */
        .subject-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }

        .subject-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        /* ═══════ Topic row highlight ═══════ */
        .topic-row {
            border-left: 3px solid #6366F1;
            padding-left: 14px;
            margin-left: 12px;
            margin-bottom: 10px;
            padding-top: 8px;
            padding-bottom: 4px;
        }

        </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Render a stylish page header with optional subtitle."""
    st.markdown(f"""
        <div style="margin-bottom: 24px; padding: 16px 22px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border-left: 5px solid #6366F1; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <h1 style="color: #FFFFFF !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; font-size: 2.2rem !important; margin: 0 0 6px 0 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.6);">{title}</h1>
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
