import streamlit as st

PRIMARY_COLOR = "#4F46E5"
PRIMARY_DARK = "#3730A3"
BACKGROUND = "#F8FAFC"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#1E293B"
MUTED_COLOR = "#64748B"
BORDER_COLOR = "#E2E8F0"
SUCCESS_COLOR = "#059669"
WARNING_COLOR = "#D97706"


def apply_theme():
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}

        .stApp {{
            background-color: {BACKGROUND};
        }}

        h1 {{
            color: {TEXT_COLOR};
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        h2, h3 {{
            color: {TEXT_COLOR};
            font-weight: 600;
        }}

        p, span, label {{
            color: {TEXT_COLOR};
        }}

        .stButton > button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1.25rem;
            font-weight: 600;
            transition: background-color 0.15s ease;
        }}

        .stButton > button:hover {{
            background-color: {PRIMARY_DARK};
            color: white;
        }}

        [data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 14px;
            padding: 1rem 1.25rem;
        }}

        [data-testid="stMetricLabel"] {{
            color: {MUTED_COLOR};
            font-weight: 500;
        }}

        [data-testid="stMetricValue"] {{
            color: {TEXT_COLOR};
            font-weight: 700;
        }}

        [data-testid="stChatMessage"] {{
            border-radius: 14px;
            padding: 0.25rem 0.5rem;
        }}

        [data-testid="stSidebar"] {{
            background-color: {CARD_BG};
            border-right: 1px solid {BORDER_COLOR};
        }}

        [data-testid="stSidebarNav"] a {{
            border-radius: 8px;
            font-weight: 500;
        }}

        .stAlert {{
            border-radius: 12px;
        }}

        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
        }}

        .mas-hero {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {PRIMARY_DARK} 100%);
            border-radius: 20px;
            padding: 2.5rem 2rem;
            color: white;
            margin-bottom: 1.5rem;
        }}

        .mas-hero h1 {{
            color: white;
            margin-bottom: 0.5rem;
        }}

        .mas-hero p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.05rem;
            margin-bottom: 0;
        }}

        .mas-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 0.75rem;
        }}

        .mas-badge {{
            display: inline-block;
            background-color: #EEF2FF;
            color: {PRIMARY_COLOR};
            border-radius: 999px;
            padding: 0.2rem 0.75rem;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )