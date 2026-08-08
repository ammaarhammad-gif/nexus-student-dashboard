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
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
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

        /* ═══════ Sidebar ═══════ */
        section[data-testid="stSidebar"] {
            background-color: #0F172A;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
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
        <div style="margin-bottom: 24px;">
            <h1 style="color: #F8FAFC; margin-bottom: 4px; font-weight: 700;">{title}</h1>
            {f'<p style="color: #94A3B8; font-size: 1.05rem; margin-top: 0;">{subtitle}</p>' if subtitle else ''}
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
